# Macro Data Dashboard 开源的宏观经济数据工作台 

> **Version:** v0.6.00.alpha  
> **Author:** Kitazaki Hinata, SeaAndStars

> **Recent Updates:**  
>  1. 重新架构数据下载与数据库

**本程序仅用于学习和学术研究，请遵守目标网站使用条款。**<br>
**图表数据仅供分析参考，实际数据请以官方数据源为准。**<br>
**使用者应自行承担使用程序的任何风险，作者不对任何使用程序所造成的后果负责。**<br>
**本程序所提供的信息不构成任何投资建议。**<br>

***

### 一、项目说明
创建这个项目的目的是方便汇集不同宏观数据方便进行比较（频繁的打开各种不同网页抓取数据太过于麻烦）。
此项目分为两个功能，第一个是获取关键宏观经济数据，
并将数据下载至本地csv文件当中。第二个是利用csv中的数据生成集成式的图表。
可供查看的数据会陆续更新.

**注意：强烈建议使用代理IP下载数据！
弹出的浏览器窗口需保持打开状态，不要对其进行任何操作！禁止快速重复的下载数据（会触发API上限，亦或是IP封禁）**<br>
<br>

***

### 二、准备工作与使用方法（包括配置环境，API key获取）
###### 1. 配置Python环境：
- Python解释器：3.12
###### 2. 配置所需的Python包与模块：
```
# console配置虚拟环境
pip install uv
uv sync
```
###### 3. 移步至数据源获取API key：
- BEA：https://apps.bea.gov/api/signup/ <br>
- FRED St. Louis：https://fredaccount.stlouisfed.org/apikeys <br>
- BLS：https://data.bls.gov/registrationEngine/ <br>
###### 4. 使用方法：
1. 打开文件
2. 设置排列方式与数据
3. 如果没有下载数据，选择开始年份（最早2020），并下载数据
4. 等待下载完成后，点击绘制并展示

***

### 三、数据总览
[查看完整数据清单](doc/data_available.html) <br>
###### 部分数据源
- Yahoo Finance API
- BEA API
- FRED API
- BLS API
- 其他来源的数据

###### 正在更新的数据源
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

***

### 四、开源许可，程序架构与接口说明，其他信息
开源许可：MIT license<br>
程序架构与接口说明：[点击访问md文件](doc/structure.md)<br>
BLS数据代码查询：https://beta.bls.gov/dataQuery/find<br>




