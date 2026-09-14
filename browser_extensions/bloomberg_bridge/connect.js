// The token stays on loopback / inside the extension, never in the article URL.
(() => {
  if (location.pathname !== "/bbg/connect") return;
  const token = location.hash.slice(1);
  if (!/^[A-Za-z0-9_-]{43}$/.test(token)) return;
  chrome.runtime.sendMessage({type: "begin", token}).then(response => {
    if (response?.error) document.getElementById("status").textContent = response.error;
  }).catch(() => {
    const status = document.getElementById("status");
    if (status) status.textContent = "连接已中断，请回到工作台重新加载文章。";
  });
})();
