# 程序架构与接口说明

> 作者：Kitazaki Hinata

## 序：完整程序结构与流程图

1. main.py：主程序入口，包括初始化，调用 PySide 窗口
2. download.py：通过 API 或抓取方式获取数据并存入数据库
3. data.db：SQLite 数据库，存储下载后的数据
4. PySide6 交互界面：数据可视化
5. pyproject.toml：环境依赖配置
6. request_id.json：存放 API 请求所需的参数
7. 其他：日志文件、Markdown 文档、架构图与 HTML 展示页面

![Program Flow Chart](structure/program%20structure%20flow%20chart.png "program flow chart")

***

## Python 脚本架构与 JSON 文件说明

### Python 脚本介绍

- 功能：使用外部 API 或抓取方式获取数据，录入数据库/转存为 CSV；提供统一接口以便请求下载特殊类型数据
- 类文件：download.py（实现转换与入库等方法）
- 接口入口：database_importer.py
- 设计架构：简单工厂模式
- 环境与依赖：参考父级目录 pyproject.toml（[查看文件](../pyproject.toml)）
- 报错文件：doc/error.log（[查看文件](error.log)）

### JSON 文件介绍

- 功能：存放名称、上游 API 请求参数、数据修正方式等
- 主要参数：

```text
name: string，数据名称
code: string，向 API 发送的数据 id
freq: string，数据更新频率（仅在 BEA 类数据存在，取 "A"、"Q"、"M" 等）
category: string，数据类（仅在 BEA 类数据存在）
needs_pct: bool，是否需要将数值转换为百分比
needs_cleaning: bool，是否需要数据清洗（处理残缺数据）
```

```json
{
  "BEA": {
    "qoq_gdp_growth_q": {
      "name": "GDP Growth QoQ%",
      "code": "T10101",
      "freq": "Q",
      "category": "NIPA",
      "needs_pct": false,
      "needs_cleaning": false
    }
  }
}
```

***

## DatabaseConverter 方法类：统一转换与入库

注：除了 `write_into_db` 函数，其余函数均用于内部调用

- `_convert_month_str_to_num`：将月份字符串转换为数字
- `_rename_bea_date_col`：统一时间轴；输入 df，输出改好日期格式且首列为 `date` 的 df
- `_format_converter`：统一数据格式；
  - `data_name`：数据名称，用于报错与列名（如 `table_config["code"]`）
  - `is_pct_data`：是否百分比数据（默认 False；来自 JSON 配置 `needs_pct`）
- `_create_ts_sheet`：创建 `Time_Series` 表（存在则跳过）
- `write_into_db`：输出 DataFrame 到 data.db，并统一不同数据 DataFrame 的时间戳
  - `data_name`：df 与 db 的列名，以及报错信息
  - `start_date`：起始日期（字符串）
  - `is_time_series`：是否为时序数据（True 写入 `Time_Series`，否则创建新表）
  - `is_pct_data`：是否为百分比数据（来自 JSON 配置）

***

## DataSource 抽象类：定义下载与存储方法

所有继承 DataSource 的实例类必须实现以下方法：

1. `to_db`
   - 功能：将数据写入 `data.db`
   - 返回值：None / Dict(name, dataframe)
     - 直接调用则写库返回 None；若下载 CSV，`to_csv` 会将内部参数 `return_df` 设为 True，使其返回包含 DataFrame 的字典

2. `to_csv`
   - 功能：下载 CSV 到 `csv` 目录（后续可能改为直接对接 database）
   - 返回值：None

```python
class DataSource(ABC):
    @abstractmethod
    def to_db(self, return_df: bool = False):
        pass

    def to_csv(self) -> None:
        pass
```

***

## DataSource 实例类：按数据来源划分

| 类名                      | 数据来源说明                    | 数据源简称 `source` |
|---------------------------|---------------------------------|---------------------|
| BEADownloader             | 美国国家统计局 API 数据         | bea                 |
| YFDownloader              | 雅虎 yfinance 美股 API 数据     | yf                  |
| FREDDownloader            | 美国 Federal Reserve API 数据   | fred                |
| BLSDownloader             | 美国劳工局 API 数据             | bls                 |
| TEDownloader              | TradingEconomics 平台数据       | te                  |
| ISMDownloader             | ISM 美国制造业/服务业数据       | ism                 |
| FedWatchDownloader        | CME FedWatch 数据               | fw                  |
| DallasFedDownloader       | 达拉斯联储制造业数据            | dfm                 |
| NewYorkFedDownloader      | 纽约联储经济数据                | nyf                 |
| InflaNowcastingDownloader | 克里夫兰联储实时通胀预测数据    | cin                 |
| EminiDownloader           | CME E-mini 期货交易数据         | em                  |
| ForexSwapDownloader       | 外汇掉期数据                    | fs                  |

传入实例类的参数：

1. `json_dict`：从 `request_id.json` 读取的完整字典，用于传参与命名
2. `api_key`：从 `.env` 读取的 API key
3. `request_year`：请求起始年份

实例类的方法：

1. `to_db`：写入数据库（`return_df` 为内部参数，下载 CSV 时让其返回 DataFrame 字典）
2. `to_csv`：下载 CSV（后续可能改为直连 database）

***

## DownloaderFactory：统一构造入口

```python
@classmethod
def create_downloader(
    cls,
    source: str,
    json_data: dict,   # full json data, not just one item in the dict
    request_year: int,
) -> "DataDownloader" | None:
    ...
```

- `_get_api_key`：私有类方法，供类方法内部调用对应 API
- `create_downloader`：工厂方法，按输入参数创建实例
  - `source`：数据源简称（见上表）
  - `json_data`：传入 `main.py` 解析出的完整 JSON；工厂会按 `source` 提取需要的子字典传入实例

***

## 接口使用示例

```python
if __name__ == "__main__":
    # initialize
    setup_logging()  # 初始化日志系统
    json_data: dict = read_json()
    request_year: int = 2020  # 请求的开始年份

    # interface
    bea_downloader = DownloaderFactory.create_downloader(
        source="bea",
        json_data=json_data,
        request_year=request_year,
    )
    bea_downloader.to_db()
```
