import copy
from http.client import HTTPConnection
import json
from pathlib import Path
from queue import Queue
import threading
import unittest
from unittest.mock import MagicMock, patch
from urllib.parse import urlsplit

from gui.bbg_browser import BloombergBrowser, BrowserReadError, validate_article_dict
from gui.bbg_extract import BloombergExtractor
from gui.ui_function import UiFunctions


URL = "https://www.bloomberg.com/news/articles/2026-09-14/test-story?srnd=test"
DATA = json.loads((Path(__file__).parent / "fixtures" / "bbg_next_data.json").read_text(encoding="utf-8"))
EXPECTED = "测试段落：实体与链接。\n\nSecond paragraph — preserved."


class BridgeTests(unittest.TestCase):
    def start_request(self, timeout=3, edit=True):
        self.browser = BloombergBrowser(timeout=timeout)
        self.opened = Queue()
        self.results = Queue()
        self.opener = patch("gui.bbg_browser.webbrowser.open_new_tab", side_effect=lambda url: self.opened.put(url) or True)
        self.opener.start()
        self.addCleanup(self.opener.stop)
        self.addCleanup(self.browser.close)
        extractor = BloombergExtractor(URL)
        function = extractor.edit_bbg_article if edit else extractor._fetch_bbg_article
        self.thread = threading.Thread(target=lambda: self.results.put(function(self.browser)), daemon=True)
        self.thread.start()
        self.address = urlsplit(self.opened.get(timeout=3))
        self.addCleanup(lambda: self.thread.join(timeout=3))

    def request(self, method, path, payload=None, token=None, host=None):
        connection = HTTPConnection("127.0.0.1", self.address.port, timeout=3)
        try:
            headers = {"Authorization": "Bearer " + (self.address.fragment if token is None else token)}
            if host:
                headers["Host"] = host
            body = None
            if payload is not None:
                body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
                headers["Content-Type"] = "application/json"
            connection.request(method, path, body=body, headers=headers)
            response = connection.getresponse()
            return response.status, response.read()
        finally:
            connection.close()

    def send_data(self, data=DATA, url=URL):
        return self.request("POST", "/result", {"url": url, "json": json.dumps(data, ensure_ascii=False)})

    def test_real_http_json_becomes_original_dictionary_without_wrapper(self):
        self.start_request(edit=False)
        status, body = self.request("GET", "/request")
        self.assertEqual(status, 200)
        self.assertEqual(json.loads(body)["url"], URL)
        self.assertEqual(self.send_data()[0], 200)
        success, data = self.results.get(timeout=3)
        self.assertTrue(success)
        self.assertIsInstance(data, dict)
        self.assertEqual(data, DATA)

    def test_real_http_to_unchanged_article_parser(self):
        self.start_request()
        self.assertEqual(self.send_data()[0], 200)
        self.assertEqual(self.results.get(timeout=3), (True, EXPECTED))

    def test_rejects_bad_token_host_and_other_article_then_accepts_canonical_url(self):
        self.start_request()
        self.assertEqual(self.request("GET", "/request", token="wrong")[0], 403)
        self.assertEqual(self.request("GET", "/request", host="evil.example")[0], 403)
        self.assertEqual(self.send_data(url="https://www.bloomberg.com/news/articles/other")[0], 400)
        self.assertTrue(self.results.empty())
        self.assertEqual(self.send_data(url=URL.replace("www.", "").split("?")[0])[0], 200)
        self.assertEqual(self.results.get(timeout=3), (True, EXPECTED))

    def test_invalid_json_takes_existing_error_branch(self):
        self.start_request()
        self.request("POST", "/result", {"url": URL, "json": "not JSON"})
        success, message = self.results.get(timeout=3)
        self.assertFalse(success)
        self.assertIn("不是有效 JSON", message)

    def test_missing_body_takes_existing_error_branch(self):
        self.start_request()
        self.send_data({"props": {"pageProps": {"story": {}}}})
        success, message = self.results.get(timeout=3)
        self.assertFalse(success)
        self.assertIn("props.pageProps.story.body.content", message)

    def test_extension_error_is_returned(self):
        self.start_request()
        self.request("POST", "/result", {"url": URL, "error": "页面未提供 __NEXT_DATA__"})
        self.assertIn("页面未提供 __NEXT_DATA__", self.results.get(timeout=3)[1])

    def test_timeout_is_actionable_and_closes_server(self):
        self.start_request(timeout=0.2)
        success, message = self.results.get(timeout=3)
        self.assertFalse(success)
        self.assertIn("加载", message)
        self.assertIsNone(self.browser._active)
        with self.assertRaises(OSError):
            self.request("GET", "/request")

    def test_cancel_releases_waiting_request(self):
        self.start_request()
        self.browser.close()
        success, message = self.results.get(timeout=3)
        self.assertFalse(success)
        self.assertIn("取消", message)

    def test_failed_browser_launch_is_returned_and_receiver_released(self):
        browser = BloombergBrowser()
        with patch("gui.bbg_browser.webbrowser.open_new_tab", return_value=False):
            success, message = BloombergExtractor(URL).edit_bbg_article(browser)
        self.assertFalse(success)
        self.assertIn("无法打开默认浏览器", message)
        self.assertIsNone(browser._active)


class DictionaryValidationTests(unittest.TestCase):
    def test_preserves_the_original_dictionary(self):
        data = copy.deepcopy(DATA)
        self.assertIs(validate_article_dict(data), data)
        self.assertEqual(data, DATA)

    def test_incompatible_nodes_cannot_reach_unchanged_parser(self):
        for bad_content in (None, {}, [None], [{"type": "paragraph", "content": None}],
                            [{"type": "paragraph", "content": [None]}],
                            [{"type": "paragraph", "content": [{"type": "text", "value": 123}]}],
                            [{"type": "paragraph", "content": [{"type": "link", "content": None}]}],
                            [{"type": "paragraph", "content": [{"type": "entity", "content": [None]}]}]):
            with self.subTest(content=bad_content):
                data = copy.deepcopy(DATA)
                data["props"]["pageProps"]["story"]["body"]["content"] = bad_content
                browser = MagicMock()
                browser.fetch_article.return_value = data
                success, message = BloombergExtractor(URL).edit_bbg_article(browser)
                self.assertFalse(success)
                self.assertIsInstance(message, str)
                browser.close.assert_called_once()


class UiTests(unittest.TestCase):
    def test_worker_result_is_delivered_by_ui_poll(self):
        ui = UiFunctions.__new__(UiFunctions)
        ui.main_window = MagicMock()
        ui._bbg_results = Queue()
        ui._bbg_timer = MagicMock()
        ui._bbg_thread = object()
        extractor = MagicMock()
        extractor.edit_bbg_article.return_value = (True, EXPECTED)
        ui._read_bbg_article(extractor, MagicMock())
        ui.main_window.bbg_article_showbox.setPlainText.assert_not_called()
        ui._poll_bbg_article()
        ui.main_window.bbg_article_showbox.setPlainText.assert_called_once_with(EXPECTED)
        ui.main_window.bbg_url_load_btn.setEnabled.assert_called_once_with(True)
        self.assertIsNone(ui._bbg_thread)


if __name__ == "__main__":
    unittest.main()
