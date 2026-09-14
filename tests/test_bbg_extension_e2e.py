"""Real extension + loopback + original parser, using only synthetic web pages.

Opt in: $env:BBG_EXTENSION_E2E='1'; python -m unittest discover -s tests -p test_bbg_extension_e2e.py -v
Playwright is used exclusively by this test, never by the Bloomberg feature.
"""

import json
import os
from pathlib import Path
from queue import Queue
import tempfile
import threading
import time
import unittest
from unittest.mock import patch

from gui.bbg_browser import BloombergBrowser, EXTENSION_DIRECTORY
from gui.bbg_extract import BloombergExtractor


URL = "https://www.bloomberg.com/news/articles/2026-09-14/test-story?srnd=test"
DATA = json.loads((Path(__file__).parent / "fixtures" / "bbg_next_data.json").read_text(encoding="utf-8"))
EXPECTED = "测试段落：实体与链接。\n\nSecond paragraph — preserved."


@unittest.skipUnless(os.environ.get("BBG_EXTENSION_E2E") == "1", "Opt-in browser integration test")
class ExtensionE2ETests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from playwright.sync_api import sync_playwright
        cls.profile = tempfile.TemporaryDirectory(prefix="bbg-extension-test-")
        cls.playwright = sync_playwright().start()
        cls.context = cls.playwright.chromium.launch_persistent_context(
            cls.profile.name, channel="chromium", headless=True,
            args=[f"--disable-extensions-except={EXTENSION_DIRECTORY}",
                  f"--load-extension={EXTENSION_DIRECTORY}"],
        )

    @classmethod
    def tearDownClass(cls):
        cls.context.close()
        cls.playwright.stop()
        cls.profile.cleanup()

    def setUp(self):
        self.html = self.fixture(DATA)
        self.page = self.context.new_page()
        self.context.route("**/*", self.route)

    def tearDown(self):
        self.context.unroute("**/*", self.route)
        for page in self.context.pages:
            if not page.is_closed():
                page.close()

    @staticmethod
    def fixture(data, delayed=False):
        text = json.dumps(data, ensure_ascii=False).replace("</", "<\\/")
        if delayed:
            return ("<!doctype html><h1>Synthetic delayed article</h1><script>"
                    "setTimeout(()=>{const el=document.createElement('script');"
                    "el.id='__NEXT_DATA__';el.type='application/json';el.textContent=" +
                    json.dumps(text) + ";document.body.append(el)},600);</script>")
        return '<!doctype html><h1>Synthetic article</h1><script id="__NEXT_DATA__" type="application/json">' + text + '</script>'

    def route(self, route):
        if route.request.url.startswith("https://www.bloomberg.com/"):
            route.fulfill(status=200, content_type="text/html; charset=utf-8", body=self.html)
        elif route.request.url.startswith("http://127.0.0.1:"):
            route.continue_()
        else:
            route.abort()

    def run_extraction(self, *, edit=True, timeout=15, close_page=False, after_navigation=None):
        browser = BloombergBrowser(timeout=timeout)
        opened, results = Queue(), Queue()
        extractor = BloombergExtractor(URL)
        function = extractor.edit_bbg_article if edit else extractor._fetch_bbg_article
        thread = threading.Thread(target=lambda: results.put(function(browser)), daemon=True)
        with patch("gui.bbg_browser.webbrowser.open_new_tab", side_effect=lambda url: opened.put(url) or True):
            thread.start()
            try:
                self.page.goto(opened.get(timeout=3))
                self.page.wait_for_url("https://www.bloomberg.com/**", timeout=10000)
                if after_navigation is not None:
                    after_navigation()
                pump = self.page
                if close_page:
                    self.page.close()
                    pump = self.context.new_page()
                deadline = time.monotonic() + timeout + 3
                while results.empty() and time.monotonic() < deadline:
                    # Pump browser events so route handlers and the service worker run.
                    pump.wait_for_timeout(50)
                return results.get(timeout=1)
            finally:
                browser.close()
                thread.join(timeout=3)

    def test_dom_json_is_delivered_as_exact_python_dictionary(self):
        self.assertEqual(self.run_extraction(edit=False), (True, DATA))
        self.assertEqual(self.page.evaluate("typeof window.__NEXT_DATA__"), "object")
        # The named element is visible on window, but is not a parsed Next.js object.
        self.assertTrue(self.page.evaluate("window.__NEXT_DATA__ instanceof HTMLScriptElement"))

    def test_existing_article_parser_runs_without_changes(self):
        self.assertEqual(self.run_extraction(), (True, EXPECTED))

    def test_delayed_json_tag_is_observed(self):
        self.html = self.fixture(DATA, delayed=True)
        self.assertEqual(self.run_extraction(), (True, EXPECTED))

    def test_reload_keeps_the_request_associated_with_the_tab(self):
        self.html = self.fixture(DATA, delayed=True)
        self.assertEqual(self.run_extraction(after_navigation=lambda: self.page.reload()), (True, EXPECTED))

    def test_other_tab_with_same_url_cannot_supply_the_article(self):
        self.html = self.fixture(DATA, delayed=True)

        def open_other_tab():
            # This earlier-returning document must not satisfy the pending request.
            self.html = self.fixture({"props": {"pageProps": {"story": {}}}})
            self.context.new_page().goto(URL)

        self.assertEqual(self.run_extraction(after_navigation=open_other_tab), (True, EXPECTED))

    def test_closing_article_tab_returns_error(self):
        self.html = "<!doctype html><h1>Waiting for article data</h1>"
        success, message = self.run_extraction(close_page=True)
        self.assertFalse(success)
        self.assertIn("标签页已关闭", message)

    def test_missing_body_returns_error_without_crashing_parser(self):
        self.html = self.fixture({"props": {"pageProps": {"story": {}}}})
        success, message = self.run_extraction()
        self.assertFalse(success)
        self.assertIn("props.pageProps.story.body.content", message)

    def test_missing_json_reports_error(self):
        self.html = "<!doctype html><h1>Synthetic verification page without JSON</h1>"
        success, message = self.run_extraction(timeout=5)
        self.assertFalse(success)
        self.assertIn("__NEXT_DATA__", message)


if __name__ == "__main__":
    unittest.main()
