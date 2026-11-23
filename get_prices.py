
import pandas as pd
import yfinance as yf

tickers = ["VT", "BIL", "QQQ", "IEF"]

data = yf.download(
    tickers,
    start="2021-10-01",
    end="2026-10-01",
    interval="1d",
    auto_adjust=False,
    progress=False
)

prices = data["Adj Close"]
prices = prices.resample("ME").last()
prices = prices[tickers].dropna()

prices.index.name = "Date"

prices.to_csv("prices.csv", date_format="%Y-%m-%d")

print(prices.head())
print(f"Months of data: {len(prices)}")
print("Saved prices.csv")
