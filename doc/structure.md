# 程序架构与接口说明
> 作者：Kitazaki Hinata

**序：完整程序结构与流程图**
1. **download.py：通过API或者抓取方式获取数据并存入数据库**
2. data.db：数据库，存储每次下载的数据
3. C# GUI交互界面，数据可视化
4. pyproject.toml 环境依赖配置文档
5. request_id.json 储存用于API请求的参数
6. 其他：日志文件，md文档，架构图与html展示性页面

![Program Flow Chart](structure/program structure flow chart.png "program flow chart")
***

###  python脚本架构与json文件说明
#### **python脚本介绍：** <br>
* 功能：使用外部API或者抓取方式获取数据，并录入数据库/转存为csv格式的数据；
提供接口方便请求下载特殊类型的数据。
* 类文件：data_download.py
* 入口：main.py
* 设计架构：简单工厂模式
* 环境与依赖：参考父级目录pyproject.toml文件  [查看文件](../pyproject.toml) <br>
* 报错文件：doc/error.log [查看文件](error.log) <br>

#### **json文件介绍：**<br>
* 功能：用于储存名称，向外层数据源发送的参数，数据修改方式等数据。 <br>
* 主要参数：<br>
```name``` : string，数据名称<br>
```code``` : string，向API发送的数据id<br>
```freq``` : string，数据更新周期（仅在BEA类数据存在，格式为“A”，“Q”，“M”等）<br>
```category``` : string，数据类（仅在BEA类数据存在）<br>
```needs_pct``` : bool，是否需要将数据转换为百分比格式<br>
```needs_cleaning``` : bool，是否需要数据清洗（处理残缺数据）<br>
```
  "BEA": {      
    "qoq_gdp_growth_q": {  
      "name": "GDP Growth QoQ%",
      "code": "T10101",
      "freq": "Q",
      "category": "NIPA",
      "needs_pct": false,
      "needs_cleaning": false
    }
```
#### **DataSource 抽象类：所有实例数据类的基类，定义下载和储存方法**<br>
<details>
      <summary>【展开抽象类说明】</summary>

所有继承DataSource的实例类必须包含两个方法：
1. ```to_db```
   - 功能：将数据传入至 `data.db` 数据库  
   - 返回值：None

2. ```to_csv```
   - 功能：下载 CSV 格式数据到 `csv` 文件夹
   - 返回值：None

```
class DataSource(ABC):
    @abstractmethod
    def to_db(self) -> None:
        pass
    def to_csv(self) -> None:
        pass
```
</details>

#### **DataSource 实例类：以数据来源为区分，定义多个实例类**<br>
<details>
      <summary>【展开实例类名与类结构说明】</summary>

<span id="实例类数据列表"></span>
##### 实例类数据列表

| 类名                 | 数据来源说明                  | 数据源简称（工厂类中使用） |
|--------------------|-------------------------|---------------|
| BEA_DataSource     | 美国国家统计局API数据            | bea           |
| YF_DataSource      | 雅虎yfinance美股API数据       | yf            |
| FRED_DataSource    | 美国Federal Reserve API数据 | fred          |
| BLS_DataSource     | 美国劳工局API数据              | bls           |
| TE_DataSource      | TradingEconomics平台数据    | te            |
| ISM_DataSource     | ISM美国制造业/服务业数据          | ism           |
| FedWatch_DataSource | CME FedWatch数据          | fw            |
| DallasFed_DataSource | 达拉斯联储制造业数据              | dfm           |
| NewYorkFed_DataSource | 纽约联储经济数据                | nyf           |
| InflaNowcasting_DataSource | 克里夫兰联储实时通胀预测数据          | cin           |
| Emini_DataSource   | CME E-mini期货交易数据        | em            |
| ForexSwap_DataSource | 外汇掉期数据                  | fs            |


1. ```self.json_dict``` : 从```request_id.json```文件中提取的字典格式数据，用于向api或者方法传参，输出数据名称。<br>
2. ```self.api_key``` : 从.env文件中提取出的api key，用于向api请求数据。<br>
3. ```to_db``` : 将数据写入数据库。<br>
4. ```to_csv``` : 将数据写入csv文件。<br>

</details>

#### **DownloaderFactory: 下载工厂类，统一接口**<br>
<details>
   <summary>【展开工厂设计模式】</summary>

```
    def create_downloader(
            cls,
            source: str,
            json_dict: Dict,
            api_key: str = None
    ) -> 'DataDownloader':
```
```create_downloader``` : 工厂方法，根据输入参数创建实例类对象并返回。<br>
- ```source``` : 输入数据源简称（参考上文的实例类名表）<br>
- ```json_dict``` : 提取json文档中的数据源参数并传入工厂<br>
- ```api_key``` : （不需要主动传入）输入数据源的API key<br>

```_get_api_key``` : 私有工厂方法，仅限类内部引用；导入.env文件里面的api数据，然后根据传入的参数获取对应的数据源的API key
- ```source``` : 输入数据源简称（参考上文的实例类名表）<br>
</details>

#### **接口使用示例**
```angular2html
if __name__ == "__main__":
    setup_logging()  # 初始化日志系统
    json_dict = read_json()

    bea_downloader = DownloaderFactory.create_downloader(
      source = 'bea', 
      json_dict = json_dict
)
    bea_downloader.to_db()  # 使用接口方法，数据传入data.db数据库
```

