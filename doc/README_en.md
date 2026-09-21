<p align="center">
  <img src="readme/chart.png" alt="Chart Example">
</p>
<h2 align="center">Macro Dashboard</h2>
  <p align="center">A lightweight desktop workspace for macroeconomic data analysis.</p>


<p align="center">
    English | <a href="https://github.com/Kitazaki-Hinata/Macro_Dashboard/tree/dev?tab=readme-ov-file">简体中文</a>
</p>

> Author: Kitazaki Hinata, SeaStar, yuyoux7

**<p style="color:red"> - This program is intended for learning and academic research. Please comply with the source websites' terms of use.</p>**

**<p style="color:red"> - Chart data is provided for analytical reference. Please verify values against the official data sources.</p>**

**<p style="color:red"> - Users are responsible for any risks associated with using the program. The author is not liable for any consequences resulting from the use of the program.</p>**

**<p style="color:red"> - The information provided by this program does not constitute any investment advice.</p>**


### 1. Project Description

Macro Dashboard is a desktop application built with Python and PySide6 for organizing and exploring macroeconomic data in educational and research settings. It brings together data from BEA, FRED, BLS, Yahoo Finance, TradingEconomics, and other sources, with support for data downloads, CSV export, and chart and table views. By reducing repetitive data collection across platforms, it enables users to compare historical trends in a single interface and explore potential lead and lag relationships through time shifts. The application also provides browser-assisted reading and text organization for Bloomberg news, bringing article text supplied by the source page into the workspace to support analysis in the context of economic news. Content availability depends on the data returned by the page, and use is subject to the source website's access permissions and terms of use.
Source-specific download modules share a common interface for data retrieval, format conversion, and storage. Time series are stored locally in a SQLite database (data.db) and displayed in interactive charts using PyQtGraph. Downloaded data can also be saved as CSV files for further analysis.
The data catalog and project configuration define the current coverage, with additional indicators planned for future updates. Historical coverage, update frequency, and statistical definitions depend on the original data source and should be considered when comparing indicators. Before downloading, ensure that your network can reach the selected sources and configure a proxy or VPN if needed. Keep browser windows opened by automated data downloads running and avoid manual interactions that could interrupt the process. Avoid repeated download requests in quick succession to stay within API quotas and access rate limits.


### 2. Setup and Usage (Environment Configuration and API Keys)

#### 1. Python Environment

- Python Interpreter: 3.12

#### 2. Install Dependencies

```powershell
# Windows PowerShell
pip install uv
uv sync
```


#### 3. Obtain API Keys
Request the relevant API keys from the following data providers:
```ini
BEA: https://apps.bea.gov/api/signup/
FRED St. Louis: https://fredaccount.stlouisfed.org/apikeys
BLS: https://data.bls.gov/registrationEngine/
```

#### 4. Usage Instructions
Start the application by running python main.py, or double-click main.bat on Windows. On first launch, click the "Settings" button at the bottom of the left sidebar and enter your API keys in the corresponding fields at the top left. Alternatively, create a file named .env in the project root directory and enter the API keys as follows:

```ini
bea = "XXXXXX-YOUR-API-KEY"
fred = "YOURAPIKEY-123456"
bls = "YOUR-API-KEY-000000"
```
If you have not yet downloaded any data, select a start year (the earliest year currently supported by the interface is 2020), read and accept the usage notice, and click the download button.

Once the download is complete, use the left sidebar to open the desired view. Select the data to display at the top left and click confirm.


### 3. Data Overview
[View the current data catalog](data_available.html)

#### Selected Data Sources
- Yahoo Finance API
- BEA API
- FRED API
- BLS API (Availability depends on your network environment and the provider's access restrictions)
- TradingEconomics
- Additional data sources are planned

### 4. Software License, Architecture, and Other Information
**Software License :** MIT Non-Commercial License (MIT-NC), for non-commercial use only. See the LICENSE file in the project root for the full terms. The data processing architecture and interfaces are described in the [architecture documentation](structure.md) (in Chinese).

**BLS Data Code Query :** https://beta.bls.gov/dataQuery/find

