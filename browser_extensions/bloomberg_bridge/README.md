# 使用自己的浏览器读取彭博文章

扩展读取文章页面中 `<script id="__NEXT_DATA__" type="application/json">` 的文本，将原始 JSON 传回本机工作台。Python 使用 `json.loads` 转为字典，并检查原文章解析函数需要的字段。无需 Selenium、F12、剪贴板或额外 Python 依赖。

## 首次加载扩展

1. 在你平时能正常打开彭博的 Chrome / Edge 用户配置中，打开 `chrome://extensions` / `edge://extensions`。
2. 开启“开发者模式”，点击“加载已解压的扩展”。
3. 选择本目录 **`browser_extensions/bloomberg_bridge`**，即包含 `manifest.json` 的文件夹。
4. 确保系统默认浏览器外部链接也使用这个浏览器配置，然后重启工作台。

这是本地浏览器扩展，不是 Codex 插件；不用发布商店或注册账号。加载后不要移动扩展文件夹。更新扩展代码时，在管理扩展页面点击“重新加载”。

## 使用

在工作台的彭博页面输入文章 URL，点击加载。浏览器首先显示本机连接页，扩展连接后自动在同一个标签页进入文章。等待 JSON 出现后，数据自动传回工作台，原来的 `edit_bbg_article` 负责生成并返回文章文本。

如果连接页停留不动，检查是否在正确的浏览器配置中加载并启用了扩展；新加载扩展后刷新连接页。默认等待 180 秒，超时后可重新点击加载。

出现人机验证时可直接在浏览器中手动处理，工作台不会卡住。扩展不会自动操作验证码。完成读取后保留文章标签页，扩展停止采集本次请求。

## 数据与兼容性

- 只采集从工作台连接页发起的那个文章标签页。平时手动打开的其他彭博标签页不会发送数据。
- 不修改 `navigator`、User-Agent、页面 JS 全局变量，不启用远程调试。
- JSON 只发送到本机 `127.0.0.1` 上本次请求的临时端口，使用随机请求令牌；令牌不会附加到彭博 URL。请求完成、取消或超时后关闭接收服务。
- JSON 原文经过解析后成为 Python `dict`，不增加外层包装、不重命名字段、不补造正文。数据格式不符时返回错误，避免原第 85 行之后的代码因字段或类型错误崩溃。
- 单次传输上限为 16 MB，超出时返回明确错误。
- 页面需要实际包含有效的 `__NEXT_DATA__` 和 `props.pageProps.story.body.content`。订阅提示不代表一定有完整正文；只处理页面实际提供的内容。
- 无法保证网站永远不要求验证；扩展在 Chrome / Edge 上的安装和目标网站的当前页面仍需实际验证。

扩展权限仅用于保存当前请求、在本机连接页建立连接，以及读取彭博页面 DOM；不读取 Cookie 或浏览历史。

参考：[Chrome 内容脚本](https://developer.chrome.com/docs/extensions/develop/concepts/content-scripts)、[扩展跨源请求](https://developer.chrome.com/docs/extensions/develop/concepts/network-requests)、[加载本地扩展](https://developer.chrome.com/docs/extensions/get-started/tutorial/hello-world#load-unpacked)。

## 验证

在项目根目录运行 Python 接收与解析测试：

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -p test_bbg_browser.py -v
```

已经安装 Playwright Chromium 时，还可以运行真实扩展集成测试：

```powershell
$env:BBG_EXTENSION_E2E = '1'
.\.venv\Scripts\python.exe -m unittest discover -s tests -p test_bbg_extension_e2e.py -v
```

集成测试使用独立临时配置和合成页面，不访问真实彭博文章或日常浏览器资料。它验证扩展、HTTP 接收、JSON 字典和原文章返回逻辑的完整链路；不代表真实网站一定放行。
