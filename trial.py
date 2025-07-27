import yfinance
from datetime import date

start_date = "2020-01-01"
end_date = date.today()
ticker = "NVDA"

a = yfinance.download(ticker, start_date, end_date, interval = "1d")
print(a)