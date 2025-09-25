<p align="center">

<h2 align="center">Macro Dashboard</h2>
  <p align="center">轻量级宏观工作台 | A free macro data visualization software.</p>

***

<p align="center">
    简体中文 | <a href="docs/README_zh.md">English</a>
</p>

**debug waitlist :**

1. all选项框与数据单选框没有设置不能同时选中
2. One_chart导入db里面的列名以及限制输入框只能输入列名
3. one chart无法添加第二个数据，且无法修改字体
4. YFinance数据在统一下载的时候下载不了
5. 多个数据并行下载会出现抢占db写入权限的现象
6. 再多次重新设置图表的时候，后面的数据会错位
7. 鼠标十字无法识别日期
8. 软件启动的时候自动读取json里面的内容然后更新
9. four chart里面数据有错开，数量都一致
10. 数据里面最后一日的日期有重叠
11. no show second line data on preview labeled

**extra function waitlist :**

1. 设置图表网格的透明度&颜色
3. reset设置框内的内容，包括颜色，数据名称
2. 偷彭博文章 
3. 设立一个使用说明页面
4. 储存上次设置好的线条样式

> Version: v0.9.00_beta

> Author: Kitazaki Hinata
> 
> Special thanks to : SeaStar, yuyoux7



**本程序仅用于学习和学术研究，请遵守目标网站使用条款。**

**图表数据仅供分析参考，实际数据请以官方数据源为准。**

**使用者应自行承担使用程序的任何风险，作者不对任何使用程序所造成的后果负责。**

**本程序所提供的信息不构成任何投资建议。**

***

## 一、项目说明

创建这个项目的目的是方便汇集不同宏观数据方便进行比较（频繁的打开各种不同网页抓取数据太过于麻烦）。
此项目使用脚本获取宏观经济数据，并将数据下载至本地数据库（data.db）文件当中，然后生成集成式的图表。
可下载的数据会陆续更新。

注意：强烈建议使用代理 IP 下载数据！弹出的浏览器窗口需保持打开状态，不要对其进行任何操作！不要快速重复下载数据，会触发 API 上限，或触发 IP 封禁。

***

## 二、准备工作与使用方法（包括配置环境，API key 获取）

### 1. 配置 Python 环境

- Python 解释器：3.12

### 2. 安装依赖

```powershell
# Windows PowerShell
pip install uv
uv sync
```

### 3. 获取 API key

请访问以下地址获取免费API key：

- BEA: <https://apps.bea.gov/api/signup/>
- FRED St. Louis: <https://fredaccount.stlouisfed.org/apikeys>
- BLS: <https://data.bls.gov/registrationEngine/>

### 4. 使用方法

- 打开软件，点击“设置”按钮，在API KEY栏中依次填写，或者在项目根目录新建文件「.env」，按以下方式写入 API key：

```ini
bea = "XXXXXX-YOUR-API-KEY"
fred = "YOURAPIKEY-123456"
bls = "YOUR-API-KEY-000000"
```

- 也可以复制仓库根目录下的 `.env.example` 为 `.env`，并按注释修改。

- 保存「.env」后打开入口文件
- 如果没有下载数据，选择开始年份（最早 2020），并下载数据
- 等待下载完成后，设置图表样式和想要展示的数据

***

## 三、数据总览

[查看完整数据清单](doc/data_available.html)

### 部分数据源

- Yahoo Finance API
- BEA API
- FRED API
- BLS API（注意：此 API 需要非中国 IP 进行访问）
- TradingEconomics
- 其他来源的数据

### 建议的并发与抓取参数

- Yahoo Finance：建议 `YF_WORKERS=1`，避免被限流
- BLS：`BLS_WORKERS=2`，`BLS_POST_TIMEOUT=120`（秒）
- TradingEconomics：调试期可 `TE_SHOW_BROWSER=true` 以显示浏览器；生产环境可 `TE_FORCE_HEADLESS=true` 无界面运行。
- TradingEconomics 缓存：默认禁用（`TE_DISABLE_CACHE=true`）。如需开启缓存，请设置 `TE_DISABLE_CACHE=false` 并可配合 `TE_CACHE_TTL_SECONDS=900` 减少重复抓取。

### 正在更新的数据源

<!-- markdownlint-disable MD033 -->
<details>
  <summary>点击查看详情</summary>

- AAII散户投资人情绪指数
- NAAIM经理人持仓指数
- 家庭/企业/政府负债比率，流动性指标
- 经常账户，贸易差额，FDI流入流出（BEA: ITA）
- 服务贸易（BEA: IntlServTrade）
- 美元计价的外储（BEA: IIP）
- 劳动力参与率 (Labor Force Participation Rate)
- 劳工成本与劳工效率
- 职位空缺与求职者比率 (Job Openings to Applicants Ratio)
- 分行业就业增长（如科技、医疗、制造业细分）
- 临时工雇佣数据 (Temporary Help Services Employment)
- 亚特兰大联储薪资增长追踪 (Wage Growth Tracker)
- 中间品生产者价格指数 (Intermediate PPI)
- 原材料生产者价格指数 (Crude Materials PPI)
- 薪资通胀压力指标 (如单位劳动力成本)
- 租金等价通胀指标 (Zillow租金指数、CoreLogic房价指数)
- 月度零售销售额 (Advance Monthly Retail Sales)
- 电子商务销售额占比
- 密歇根消费者现况指数 (Current Conditions Index)
- 核心资本货物订单 (非国防除飞机订单)
- 建筑支出月报 (Construction Spending)
- 企业并购活动金额与数量
- 标普500企业盈利预期修正比率
- 分商品类别的贸易差额 (能源、汽车、农产品等)
- 实际有效汇率指数 (Real Effective Exchange Rate)
- 主要贸易伙伴国对美出口依存度
- 供应链压力指数 (如纽约联储的GSCPI)
- 共债务占GDP比例
- 州与地方政府财政状况
- 社会保障与医疗保险支出趋势
- 企业税收与个人税收占比
- 商业票据利率
- M2货币供应量增长率
- 银行信贷标准调查 (Senior Loan Officer Opinion Survey)
- 成屋销售月报 (Existing Home Sales)
- 住房空置率 (Homeowner & Rental Vacancy Rates)
- 抵押贷款申请指数 (MBA Purchase Index)
- 商业地产价格指数 (如NCREIF)
- 工业产出与产能利用率 (Federal Reserve G.17报告)
- 费城联储制造业指数
- 堪萨斯城联储制造业指数
- Markit制造业PMI终值
- OECD美国综合领先指标
- 经济意外指数 (Citi Economic Surprise Index)
- 世界大型企业联合会 (Conference Board)
- 消费者信心细分（预期指数 vs 现况指数）
- 美国能源信息署 (EIA)
- 周度原油库存、炼油厂利用率
- 全美房地产经纪人协会 (NAR)
- 成屋销售价格中位数
- 彭博经济意外指数
- 标普500同比与基钦周期

 </details>
<!-- markdownlint-enable MD033 -->

***

## 四、开源许可、程序架构与接口说明、其他信息

开源许可：MIT-Non-Commercial license（参见根目录 LICENSE 文件）

数据处理程序架构与接口说明：[点击访问 md 文件](doc/structure.md)

BLS 数据代码查询：<https://beta.bls.gov/dataQuery/find>








