const sessionKey = tabId => `article:${tabId}`;

function articleKey(value) {
  const url = new URL(value);
  if (url.protocol !== "https:" || !["www.bloomberg.com", "bloomberg.com"].includes(url.hostname) ||
      url.username || url.password || (url.port && url.port !== "443")) {
    throw new Error("不是有效的彭博文章地址。");
  }
  return url.pathname.replace(/\/$/, "");
}

async function localRequest(session, path, body) {
  const response = await fetch(`${session.base}${path}`, {
    method: body === undefined ? "GET" : "POST",
    headers: {
      "Authorization": `Bearer ${session.token}`,
      ...(body === undefined ? {} : {"Content-Type": "application/json"})
    },
    ...(body === undefined ? {} : {body: JSON.stringify(body)}),
    cache: "no-store",
    signal: AbortSignal.timeout(10000)
  });
  const result = await response.json();
  if (!response.ok) throw new Error(result.error || "本机连接失败。");
  return result;
}

async function readSession(tabId) {
  const key = sessionKey(tabId);
  const session = (await chrome.storage.session.get(key))[key];
  if (session && session.deadline > Date.now()) return session;
  if (session) await chrome.storage.session.remove(key);
  return null;
}

async function handleMessage(message, sender) {
  if (sender.id !== chrome.runtime.id || sender.frameId !== 0 || !Number.isInteger(sender.tab?.id)) {
    throw new Error("无效的页面请求。");
  }
  const tabId = sender.tab.id;
  if (message.type === "begin") {
    const source = new URL(sender.url);
    if (source.protocol !== "http:" || source.hostname !== "127.0.0.1" ||
        source.pathname !== "/bbg/connect" || !/^[A-Za-z0-9_-]{43}$/.test(message.token)) {
      throw new Error("无效的本机连接请求。");
    }
    const session = {base: source.origin, token: message.token};
    const request = await localRequest(session, "/request");
    if (request.protocol !== 1 || !(request.timeout_ms > 0)) throw new Error("工作台连接版本不匹配。");
    articleKey(request.url);
    session.url = request.url;
    session.deadline = Date.now() + request.timeout_ms;
    await chrome.storage.session.set({[sessionKey(tabId)]: session});
    await chrome.tabs.update(tabId, {url: request.url});
    return {ok: true};
  }

  const session = await readSession(tabId);
  if (!session) return null; // Normal browsing is never exported.
  if (articleKey(sender.url) !== articleKey(session.url)) {
    throw new Error("当前标签页已离开请求的文章。");
  }
  if (message.type === "read-request") {
    return {timeout_ms: Math.max(1, session.deadline - Date.now())};
  }
  if (message.type === "result") {
    if (typeof message.json !== "string" && typeof message.error !== "string") {
      throw new Error("缺少 JSON 数据。");
    }
    let payload = {
      url: sender.url, json: message.json, error: message.error
    };
    if (new TextEncoder().encode(JSON.stringify(payload)).length > 16 * 1024 * 1024) {
      payload = {url: sender.url, error: "__NEXT_DATA__ 传输数据超过 16 MB，未传输。"};
    }
    const result = await localRequest(session, "/result", payload);
    await chrome.storage.session.remove(sessionKey(tabId));
    return result;
  }
  throw new Error("未知的扩展请求。");
}

chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  handleMessage(message, sender).then(sendResponse).catch(error => sendResponse({error: error.message}));
  return true;
});

chrome.tabs.onRemoved.addListener(async tabId => {
  const session = await readSession(tabId);
  if (session) {
    try {
      await localRequest(session, "/result", {url: session.url, error: "文章标签页已关闭。"});
    } catch (_) {
      // The application may have already closed its temporary receiver.
    }
  }
  await chrome.storage.session.remove(sessionKey(tabId));
});
