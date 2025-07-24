# 程序架构与接口说明
> 作者：Kitazaki Hinata

**序：完整程序结构与流程图**
1. **download.py：通过API或者抓取方式获取数据并存入数据库**
2. data.db：数据库，存储每次下载的数据
3. C# GUI交互界面，数据可视化
4. pyproject.toml 环境依赖配置文档
5. 其他：日志文件，md文档，架构图与html展示性页面

![Program Flow Chart](structure/program structure flow chart.png "program flow chart")
***

###  download.py文件架构
**脚本介绍：** <br>
* 功能：使用外部API或者抓取方式获取数据，并录入数据库/转存为csv格式的数据；
提供接口方便请求下载特殊类型的数据。
* 入口：download.py 
* 环境与依赖：参考父级目录pyproject.toml文件
[查看文件](../pyproject.toml) <br>

**DataSource 抽象类**<br>
所有实例类均包含三个抽象方法：
>1. get_df  # 返回dataframe
>2. to_db  # 传入数据至data.db数据库
>3. to_csv  #下载csv格式的数据到csv文件夹下

```
class DataSource(ABC):
    @abstractmethod
    def get_df(self) -> pd.DataFrame:
        pass
    def to_db(self) -> None:
        pass
    def to_csv(self) -> None:
        pass
```
**实例类：按照数据来源进行分类**<br>
<details>
      <summary>点击展开类名与类说明</summary>

| 类名                 | 数据来源说明                  |
|--------------------|-------------------------|
| BEA_DataSource     | 美国国家统计局API数据            |
| FRED_DataSource    | 美国Federal Reserve API数据 |
| BLS_DataSource     | 美国劳工局API数据              |
| YF_DataSource      | 雅虎yfinance美股API数据       |
| TE_DataSource      | TradingEconomics平台数据    |
| FedWatch_DataSource | CME FedWatch数据          |
| Emini_DataSource   | CME E-mini期货交易数据        |
| NewYorkFed_DataSource | 纽约联储经济数据                |
| DallasFed_DataSource | 达拉斯联储数据                 |
| InflaNowcasting_DataSource | 通胀预测数据                  |
| ISM_DataSource     | 美国供应管理协会数据              |
| ForexSwap_DataSource | 外汇掉期数据                  |
</details>

