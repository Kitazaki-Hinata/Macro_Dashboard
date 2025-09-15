# API 文档生成指南

本项目推荐使用 pdoc 生成纯注释驱动的 API 文档（无需复杂配置）。

## 先决条件

- 已安装项目依赖（见 `pyproject.toml`）。
- 推荐安装 pdoc：

```powershell
pip install pdoc
```

## 生成 HTML 文档

在项目根目录执行：

```powershell
pdoc -o doc/api .\download.py .\logging_config.py .\worker_run_source.py .\main.py
```

- 生成后的 HTML 位于 `doc/api/`。
- 也可以添加 GUI 相关模块生成（部分为 UI 生成代码，注释较少）：

```powershell
pdoc -o doc/api .\gui
```

## 编写注释的风格建议

- 模块、类、函数/方法都加 docstring（中文为主，必要时中英双语）。
- 函数 docstring 建议包含：用途、参数、返回值、异常、副作用（I/O、网络、线程）。
- 关键步骤配少量行内注释，保持“读代码如读书”。

## 常见问题

- 若导入失败导致 pdoc 报错，可用环境变量跳过执行路径：
  - 例如需要 Selenium/浏览器的代码，运行 pdoc 时可能无需实际启动浏览器。
- 如需更强大的网站样式/索引，可考虑迁移到 Sphinx（`doc/` 下初始化 conf.py 与索引，再 `make html`）。
