from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional

app = FastAPI(
    title="API Agent Microservice",
    description="Polls real-time & historical market data via Yahoo Finance for Asia Tech stocks."
)

# --- Configuration for Asia Tech companies to track ---
ASIA_TECH_COMPANIES = {
    "TSM": "Taiwan Semiconductor Manufacturing Company", # TSMC (NYSE)
    "005930.KS": "Samsung Electronics Co., Ltd.", # Samsung (Korean Stock Exchange)
    "BABA": "Alibaba Group Holding Limited", # Alibaba (NYSE)
    "TCEHY": "Tencent Holdings Ltd.", # Tencent (OTC/ADR)
    "2330.TW": "Taiwan Semiconductor Manufacturing Co.", # TSMC (Taiwan Stock Exchange)
    "0700.HK": "Tencent Holdings Ltd.", # Tencent (Hong Kong Stock Exchange)
    # Add more Asia tech companies relevant to your analysis
    # e.g., JD.com (JD), Baidu (BIDU), Netease (NTES), etc.
}

# --- Pydantic Models for API Agent's Responses and Requests ---

class StockDataResponse(BaseModel):
    """Represents daily closing price data for a single stock."""
    symbol: str
    name: str
    date: str
    price: float

class EarningsDataItem(BaseModel):
    """Represents a recent earnings surprise for a company."""
    symbol: str
    name: str
    date: str
    actual_eps: Optional[float] = None
    estimated_eps: Optional[float] = None
    surprise_percent: Optional[float] = None

class MarketBriefData(BaseModel):
    """Aggregated market data including stock prices and earnings surprises."""
    stocks: List[StockDataResponse]
    earnings_surprises: List[EarningsDataItem]

# NEW: Request model for /get_daily_asia_tech_market_data endpoint
class GetMarketDataRequest(BaseModel):
    """
    Request model for fetching daily market data.
    Allows specifying a list of symbols or fetches all predefined if None.
    """
    request_symbols: Optional[List[str]] = None


# --- FastAPI Endpoints ---

@app.get("/")
def root():
    """Root endpoint for API Agent."""
    return {"message": "API Agent is running. Visit /docs for API documentation."}

@app.post("/get_daily_asia_tech_market_data", response_model=MarketBriefData)
def get_daily_asia_tech_market_data(
    request: GetMarketDataRequest # <--- CHANGED: Now expects this Pydantic model
):
    """
    Fetches daily stock prices and attempts to find recent earnings surprises
    for a predefined list of Asia tech companies (or specified symbols).
    """
    # <--- CHANGED: Access symbols via the request object
    symbols_to_fetch = request.request_symbols if request.request_symbols else list(ASIA_TECH_COMPANIES.keys())
    print(f"API Agent: Receiving request for daily market data for symbols: {symbols_to_fetch}")

    all_stock_data: List[StockDataResponse] = []
    all_earnings_surprises: List[EarningsDataItem] = []
    today_str = datetime.now().strftime("%Y-%m-%d")

    for symbol in symbols_to_fetch:
        company_name = ASIA_TECH_COMPANIES.get(symbol, symbol)
        print(f"API Agent: Fetching data for {company_name} ({symbol})...")

        try:
            stock_ticker = yf.Ticker(symbol)

            # 1. Fetch Daily Price Data
            daily_data = stock_ticker.history(period="1d")

            if not daily_data.empty:
                current_price = daily_data["Close"].iloc[-1]
                all_stock_data.append(StockDataResponse(
                    symbol=symbol,
                    name=company_name,
                    date=today_str,
                    price=round(current_price, 2)
                ))
                print(f"API Agent: Fetched current price for {symbol}: {round(current_price, 2)}")
            else:
                print(f"API Agent: No daily price data found for {symbol} for today.")

            # 2. Attempt to get Recent Earnings Surprises
            try:
                earnings_df = stock_ticker.earnings_history
                if earnings_df is not None and not earnings_df.empty:
                    earnings_df.index = pd.to_datetime(earnings_df.index)
                    recent_earnings = earnings_df[
                        earnings_df.index > (datetime.now() - timedelta(days=90))
                    ].sort_values(by=earnings_df.index.name, ascending=False)

                    if not recent_earnings.empty:
                        latest_earning_report = recent_earnings.iloc[0]

                        actual_eps = latest_earning_report.get('Reported EPS')
                        estimated_eps = latest_earning_report.get('Estimated EPS')

                        if actual_eps is not None and estimated_eps is not None and estimated_eps != 0:
                            surprise_percent = ((actual_eps - estimated_eps) / estimated_eps) * 100
                            all_earnings_surprises.append(EarningsDataItem(
                                symbol=symbol,
                                name=company_name,
                                date=latest_earning_report.name.strftime("%Y-%m-%d"),
                                actual_eps=round(float(actual_eps), 2),
                                estimated_eps=round(float(estimated_eps), 2),
                                surprise_percent=round(float(surprise_percent), 2)
                            ))
                            print(f"API Agent: Found recent earnings for {symbol}: Actual={actual_eps}, Est={estimated_eps}, Surprise={surprise_percent:.2f}%")
                        else:
                            print(f"API Agent: Recent earnings data for {symbol} lacks complete actual/estimated EPS values needed for surprise calculation.")
                    else:
                        print(f"API Agent: No recent earnings reports (last 90 days) found for {symbol}.")
                else:
                    print(f"API Agent: No earnings history found for {symbol} via yfinance.")
            except Exception as e:
                print(f"API Agent: Error processing earnings history for {symbol}: {e}")

        except Exception as e:
            print(f"API Agent: Failed to fetch any data for {symbol} due to an error: {e}")

    if not all_stock_data and not all_earnings_surprises:
        raise HTTPException(status_code=404, detail="No relevant Asia tech market data or earnings surprises found for the specified symbols.")

    print(f"API Agent: Finished fetching daily market data. Found {len(all_stock_data)} stock prices and {len(all_earnings_surprises)} earnings surprises.")
    return MarketBriefData(
        stocks=all_stock_data,
        earnings_surprises=all_earnings_surprises
    )

# To run this API Agent as a microservice:
# 1. Make sure you have FastAPI, Uvicorn, and yfinance installed:
#    pip install fastapi uvicorn yfinance pandas
# 2. Save this code as `api_agent.py` inside your `agents/` directory.
# 3. From your project's root directory (raga assignment/), run:
#    uvicorn agents.api_agent:app --reload --port 8001
# 4. Access it in your browser at http://127.0.0.1:8001/docs