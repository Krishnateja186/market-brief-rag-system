# test_preprocess.py

import yfinance as yf
from data_ingestion.preprocess import preprocess_stock_data

def test_preprocessing():
    ticker = "TSM"  # You can change to "AAPL", "MSFT", etc.
    df = yf.Ticker(ticker).history(period="5d")

    if df.empty:
        print(" No data found for", ticker)
        return

    print(f"\nRaw Data for {ticker}:\n" + "-"*30)
    print(df[['Close']])

    cleaned_df = preprocess_stock_data(df)

    print(f"\nProcessed Data with Daily Returns:\n" + "-"*40)
    print(cleaned_df[['Close', 'Daily_Return']])

if __name__ == "__main__":
    test_preprocessing()
