// Read the shared DOM, not page-world JS globals. No F12 or clipboard needed.
(async () => {
  const request = await chrome.runtime.sendMessage({type: "read-request"}).catch(() => null);
  if (!request || request.error) return;
  const deadline = Date.now() + Math.max(1, request.timeout_ms - 1500);
  let sending = false;
  let finished = false;
  let lastError = "页面未提供 script#__NEXT_DATA__，可能仍在加载或显示人机验证。";

  function cleanup() {
    finished = true;
    clearInterval(timer);
    observer.disconnect();
  }

  async function check() {
    if (sending || finished) return;
    const element = document.getElementById("__NEXT_DATA__");
    const text = element?.textContent;
    let message = null;
    if (text?.trim()) {
      try {
        const value = JSON.parse(text);
        if (!value || typeof value !== "object" || Array.isArray(value)) {
          throw new Error("JSON 顶层必须是对象。");
        }
        message = {type: "result", json: text};
      } catch (_) {
        lastError = "已找到 __NEXT_DATA__，但标签内容不是有效的 JSON 对象。";
      }
    }
    if (!message && Date.now() >= deadline) message = {type: "result", error: lastError};
    if (!message) return;
    sending = true;
    try {
      const response = await chrome.runtime.sendMessage(message);
      if (response?.ok) cleanup();
      else if (Date.now() >= deadline) cleanup();
    } catch (_) {
      if (Date.now() >= deadline) cleanup();
    } finally {
      sending = false;
    }
  }

  const observer = new MutationObserver(() => { void check(); });
  observer.observe(document.documentElement, {childList: true, subtree: true, characterData: true});
  const timer = setInterval(check, 500);
  addEventListener("pagehide", cleanup, {once: true});
  await check();
})();
