# test_analysis_agent.py

import pytest
import requests
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient # For testing FastAPI endpoints directly
from agents.analysis_agent import app, RawMarketData, StockDataInput, EarningsDataInput, AnalysisRequest, AnalyticalInsights
from typing import List, Dict, Any, Optional

# Create a TestClient for your FastAPI app
client = TestClient(app)

def test_analyze_market_data_success():
    """
    Tests the /analyze_market_data endpoint with successful, complete data.
    """
    print("\n" + "="*80)
    print("Testing Analysis Agent: Successful Market Data Analysis")
    print("="*80)

    # Simulate raw data from the API Agent
    simulated_raw_data = RawMarketData(
        stocks=[
            StockDataInput(symbol="TSM", name="TSMC", date="2025-05-29", price=150.00),
            StockDataInput(symbol="005930.KS", name="Samsung Electronics", date="2025-05-29", price=75000.00)
        ],
        earnings_surprises=[
            EarningsDataInput(
                symbol="TSM", name="TSMC", date="2025-04-25",
                actual_eps=1.55, estimated_eps=1.49, surprise_percent=((1.55-1.49)/1.49)*100 # Approx 4% beat
            ),
            EarningsDataInput(
                symbol="005930.KS", name="Samsung Electronics", date="2025-04-30",
                actual_eps=1.20, estimated_eps=1.22, surprise_percent=((1.20-1.22)/1.22)*100 # Approx -2% miss
            )
        ]
    )

    # Create the request payload
    request_payload = AnalysisRequest(
        raw_data=simulated_raw_data,
        asia_tech_aum_today_percent=22.0, # Directly from assignment example
        asia_tech_aum_yesterday_percent=18.0 # Directly from assignment example
    )

    print("Analysis Agent Test: Sending simulated raw market data to /analyze_market_data endpoint...")
    response = client.post("/analyze_market_data", json=request_payload.dict())

    print(f"Analysis Agent Test: Received response status code: {response.status_code}")
    assert response.status_code == 200
    
    insights = AnalyticalInsights(**response.json()) # Parse response into Pydantic model
    print("Analysis Agent Test: Successfully parsed response into AnalyticalInsights.")

    # --- Assertions for Portfolio Allocation ---
    print("\n--- Verifying Portfolio Allocation Insight ---")
    assert insights.portfolio_allocation is not None
    assert insights.portfolio_allocation.sector == "Asia tech"
    assert insights.portfolio_allocation.current_percentage == 22.0
    assert insights.portfolio_allocation.previous_percentage == 18.0
    assert insights.portfolio_allocation.change_points == 4.0
    print("Portfolio Allocation Insight: OK")

    # --- Assertions for Earnings Summaries ---
    print("\n--- Verifying Earnings Summaries ---")
    assert len(insights.earnings_summaries) == 2

    tsmc_summary = next((e for e in insights.earnings_summaries if e.symbol == "TSM"), None)
    assert tsmc_summary is not None
    assert tsmc_summary.company_name == "TSMC"
    assert tsmc_summary.surprise_type == "beat"
    assert tsmc_summary.percentage == pytest.approx(4.02, rel=0.01) # Use approx for float comparisons
    assert tsmc_summary.reason_keywords == "strong AI accelerator demand"
    print("TSMC Earnings Summary: OK")

    samsung_summary = next((e for e in insights.earnings_summaries if e.symbol == "005930.KS"), None)
    assert samsung_summary is not None
    assert samsung_summary.company_name == "Samsung Electronics Co., Ltd." # Check actual name
    assert samsung_summary.surprise_type == "miss"
    assert samsung_summary.percentage == pytest.approx(1.64, rel=0.01) # Use approx for float comparisons
    assert samsung_summary.reason_keywords == "weaker memory chip and consumer electronics sales"
    print("Samsung Earnings Summary: OK")

    # --- Assertions for Market Sentiment ---
    print("\n--- Verifying Market Sentiment Insight ---")
    assert insights.market_sentiment is not None
    assert insights.market_sentiment.sentiment == "neutral"
    assert insights.market_sentiment.tilt == "cautionary tilt"
    assert insights.market_sentiment.reason == "rising global bond yields impacting growth stock valuations"
    print("Market Sentiment Insight: OK")

    print("\n" + "="*80)
    print("Analysis Agent Test: ALL SUCCESSFUL SCENARIOS PASSED!")
    print("="*80)


def test_analyze_market_data_no_earnings():
    """
    Tests the /analyze_market_data endpoint when no earnings surprises are provided.
    """
    print("\n" + "="*80)
    print("Testing Analysis Agent: No Earnings Data Scenario")
    print("="*80)

    simulated_raw_data = RawMarketData(
        stocks=[
            StockDataInput(symbol="TSM", name="TSMC", date="2025-05-29", price=150.00)
        ],
        earnings_surprises=[] # Empty list
    )

    request_payload = AnalysisRequest(
        raw_data=simulated_raw_data,
        asia_tech_aum_today_percent=20.0,
        asia_tech_aum_yesterday_percent=21.0
    )

    response = client.post("/analyze_market_data", json=request_payload.dict())

    assert response.status_code == 200
    insights = AnalyticalInsights(**response.json())

    assert insights.portfolio_allocation is not None
    assert len(insights.earnings_summaries) == 0 # No earnings summaries expected
    assert insights.market_sentiment is not None
    print("Analysis Agent Test: No Earnings Data Scenario Passed.")


def test_analyze_market_data_empty_input():
    """
    Tests the /analyze_market_data endpoint with completely empty raw data.
    Should raise a 404 HTTP exception as no insights can be generated.
    """
    print("\n" + "="*80)
    print("Testing Analysis Agent: Empty Input Scenario")
    print("="*80)

    simulated_raw_data = RawMarketData(stocks=[], earnings_surprises=[])

    request_payload = AnalysisRequest(
        raw_data=simulated_raw_data,
        asia_tech_aum_today_percent=0.0, # No allocation possible
        asia_tech_aum_yesterday_percent=0.0
    )

    response = client.post("/analyze_market_data", json=request_payload.dict())

    print(f"Analysis Agent Test: Received response status code: {response.status_code} for empty input.")
    assert response.status_code == 404 # Expecting 404 Not Found as no insights
    assert "No analytical insights could be generated" in response.json()["detail"]
    print("Analysis Agent Test: Empty Input Scenario Passed.")


# Entry point for running tests with pytest
if __name__ == "__main__":
    # You typically run pytest from your terminal:
    # 1. Save this file as test_analysis_agent.py in your tests/ directory.
    # 2. Make sure you have pytest and httpx installed: pip install pytest httpx
    # 3. From your project's root directory, run: pytest tests/test_analysis_agent.py
    #    or simply: pytest (if you want to run all tests in the 'tests/' directory)

    # For direct execution and immediate feedback without full pytest framework:
    print("Running tests directly (use 'pytest' for full testing capabilities).")
    test_analyze_market_data_success()
    test_analyze_market_data_no_earnings()
    test_analyze_market_data_empty_input()