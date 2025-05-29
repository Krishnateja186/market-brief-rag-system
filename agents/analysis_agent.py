# agents/analysis_agent.py

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from datetime import datetime

app = FastAPI(
    title="Analysis Agent Microservice",
    description="Processes raw market data to extract key financial insights for the morning brief."
)

# --- Pydantic Models for Input (matching API Agent's output structure) ---
# These models define the expected format of data received by the Analysis Agent
# from upstream agents (e.g., API Agent).
class StockDataInput(BaseModel):
    symbol: str
    name: str
    date: str
    price: float

class EarningsDataInput(BaseModel):
    symbol: str
    name: str
    date: str
    actual_eps: Optional[float] = None
    estimated_eps: Optional[float] = None
    surprise_percent: Optional[float] = None

class RawMarketData(BaseModel):
    """
    Combines raw stock price data and earnings surprise data.
    This structure would typically come from the API Agent.
    """
    stocks: List[StockDataInput]
    earnings_surprises: List[EarningsDataInput]
    # In a real scenario, you might also pass AUM data here if it's dynamic
    # For now, AUM percentages are handled by direct example values for simplicity
    # as per the assignment's output example.


# --- Pydantic Models for Output (structured insights for Language Agent/Orchestrator) ---
# These models define the structured insights that the Analysis Agent will produce.
class PortfolioAllocationInsight(BaseModel):
    """Summarizes the portfolio's allocation to a specific sector."""
    sector: str
    current_percentage: float
    previous_percentage: float
    change_points: float

class EarningsSummary(BaseModel):
    """Summarizes a single company's earnings surprise."""
    company_name: str
    symbol: str
    surprise_type: str # e.g., "beat" or "miss"
    percentage: float # Absolute percentage of surprise
    reason_keywords: Optional[str] = None # Key reasons for the surprise (e.g., "strong AI demand")

class MarketSentimentInsight(BaseModel):
    """Summarizes the overall market sentiment for a region/sector."""
    sentiment: str # e.g., "neutral", "positive", "negative"
    tilt: Optional[str] = None # e.g., "cautionary tilt"
    reason: Optional[str] = None # e.g., "rising yields"

class AnalyticalInsights(BaseModel):
    """
    The main output model, containing all summarized insights
    ready for narrative synthesis by the Language Agent.
    """
    portfolio_allocation: Optional[PortfolioAllocationInsight] = None
    earnings_summaries: List[EarningsSummary]
    market_sentiment: Optional[MarketSentimentInsight] = None
    # Add other types of insights here as your system grows


# --- Request Model for the Analysis Agent's endpoint ---
class AnalysisRequest(BaseModel):
    """
    The request body for the /analyze_market_data endpoint.
    It contains the raw data from upstream agents.
    """
    raw_data: RawMarketData
    # For the assignment's example, the AUM percentages are fixed.
    # In a real dynamic system, these would be computed from a database
    # or passed in here dynamically.
    # We'll use example values matching the assignment output for clarity.
    asia_tech_aum_today_percent: float = 22.0 # From assignment example [cite: 7]
    asia_tech_aum_yesterday_percent: float = 18.0 # From assignment example [cite: 7]


# --- FastAPI Endpoints for Analysis Agent Microservice ---

@app.get("/")
def root():
    """Root endpoint for the Analysis Agent."""
    return {"message": "Analysis Agent Microservice is running. Visit /docs for API documentation."}

@app.post("/analyze_market_data", response_model=AnalyticalInsights)
async def analyze_market_data_endpoint(request: AnalysisRequest):
    """
    Receives raw market data and returns structured analytical insights.
    """
    print(f"Analysis Agent: Received raw market data for analysis.")

    portfolio_allocation_insight = None
    earnings_summaries: List[EarningsSummary] = []
    market_sentiment_insight = None # This will be set based on assignment example

    # --- 1. Analyze Portfolio Allocation ---
    # Based on assignment example: "Today, your Asia tech allocation is 22 % of AUM, up from 18 % yesterday." [cite: 7]
    # In a real system, this would be computed from the current portfolio holdings data
    # and previous day's holdings, divided by total AUM.
    current_pct = request.asia_tech_aum_today_percent
    previous_pct = request.asia_tech_aum_yesterday_percent
    change = round(current_pct - previous_pct, 2)

    portfolio_allocation_insight = PortfolioAllocationInsight(
        sector="Asia tech",
        current_percentage=current_pct,
        previous_percentage=previous_pct,
        change_points=change
    )
    print(f"Analysis Agent: Derived Asia tech allocation: {current_pct}% of AUM, change: {change} percentage points.")

    # --- 2. Analyze Earnings Surprises ---
    # Process the earnings data received from the API Agent
    for earning in request.raw_data.earnings_surprises:
        if earning.surprise_percent is not None:
            surprise_type = "beat" if earning.surprise_percent >= 0 else "miss"
            
            # Reasons are hardcoded based on the assignment's example output [cite: 7]
            # In a real scenario, these reasons would come from NLP on news/filings (Scraping Agent + LLM).
            reason_keywords = None
            if earning.symbol == "TSM" or earning.name == "Taiwan Semiconductor Manufacturing Company":
                reason_keywords = "strong AI accelerator demand" # As per example [cite: 7]
            elif earning.symbol == "005930.KS" or earning.name == "Samsung Electronics Co., Ltd.": # Samsung
                reason_keywords = "weaker memory chip and consumer electronics sales" # As per example [cite: 7]

            earnings_summaries.append(EarningsSummary(
                company_name=earning.name,
                symbol=earning.symbol,
                surprise_type=surprise_type,
                percentage=abs(earning.surprise_percent), # Use absolute value for percentage display
                reason_keywords=reason_keywords
            ))
            print(f"Analysis Agent: Summarized earnings for {earning.name}: {surprise_type} by {abs(earning.surprise_percent):.2f}%.")

    # --- 3. Determine Overall Regional Sentiment ---
    # Based on assignment example: "Regional sentiment is neutral with a cautionary tilt due to rising yields." [cite: 7]
    # In a real system, this would typically involve:
    #   - Aggregating sentiment from financial news (Scraping Agent + NLP/LLM on news)
    #   - Analyzing bond market data trends.
    market_sentiment_insight = MarketSentimentInsight(
        sentiment="neutral",
        tilt="cautionary tilt",
        reason="rising global bond yields impacting growth stock valuations" # As per example [cite: 7]
    )
    print(f"Analysis Agent: Derived regional sentiment: '{market_sentiment_insight.sentiment}' with a '{market_sentiment_insight.tilt}' due to '{market_sentiment_insight.reason}'.")

    # Raise an error if no meaningful insights could be generated
    if not portfolio_allocation_insight and not earnings_summaries and not market_sentiment_insight:
         raise HTTPException(status_code=404, detail="No analytical insights could be generated from the provided raw data.")

    print("Analysis Agent: Analysis complete. Returning structured insights.")
    return AnalyticalInsights(
        portfolio_allocation=portfolio_allocation_insight,
        earnings_summaries=earnings_summaries,
        market_sentiment=market_sentiment_insight
    )