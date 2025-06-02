# orchestrator/main.py

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import requests
from typing import List, Dict, Any, Optional
import asyncio

# Import agent classes directly if they are not exposed as microservices (e.g., LanguageAgent)
from agents.language_agent import LanguageAgent # LanguageAgent will be instantiated directly

# Import helper functions from data_ingestion
from data_ingestion.fetch_data import get_daily_market_data_from_api_agent
from data_ingestion.preprocess import format_market_data_for_retrieval

app = FastAPI(
    title="Stock Orchestrator Microservice",
    description="Coordinates all agents to deliver the Morning Market Brief."
)

# --- Configure URLs for other microservices ---
API_AGENT_BASE_URL = "https://market-brief-rag-system-1.onrender.com"
RETRIEVER_AGENT_BASE_URL = "https://market-brief-rag-system-retriever-agent.onrender.com"
ANALYSIS_AGENT_BASE_URL = "https://market-brief-rag-system-analysis-agent.onrender.com"
STT_AGENT_BASE_URL = "https://market-brief-rag-system-sst-agent.onrender.com"
TTS_AGENT_BASE_URL = "https://market-brief-rag-system-tts-agent.onrender.com"

# Initialize LanguageAgent (as it's directly imported)
try:
    language_agent_instance = LanguageAgent()
except Exception as e:
    print(f"CRITICAL ERROR: Orchestrator failed to initialize LanguageAgent: {e}")
    language_agent_instance = None

class BriefRequest(BaseModel):
    text_query: str

# NEW: Pydantic models to mirror API Agent's MarketBriefData response
# These should match the models defined in your API Agent's api_agent.py
class StockDataResponse(BaseModel):
    symbol: str
    name: str
    date: str
    price: float

class EarningsDataItem(BaseModel):
    symbol: str
    name: str
    date: str
    actual_eps: Optional[float] = None
    estimated_eps: Optional[float] = None
    surprise_percent: Optional[float] = None

class OrchestratorResponse(BaseModel):
    """
    Response model for the Orchestrator, now including raw market data.
    """
    market_brief_text: str
    raw_stock_prices: List[StockDataResponse]
    raw_earnings_surprises: List[EarningsDataItem]

@app.get("/")
def root():
    return {"message": "Orchestrator is running. Go to /docs for usage."}

@app.post("/generate_market_brief", response_model=OrchestratorResponse) # <--- MODIFIED: Use new response_model
async def generate_market_brief_endpoint(request: BriefRequest):
    print(f"\nOrchestrator: Received request to generate market brief for query: '{request.text_query}'")

    if language_agent_instance is None:
        raise HTTPException(status_code=500, detail="Orchestrator: Language Agent not initialized.")

    # --- Step 1: Get Raw Market Data (from API Agent) ---
    print("Orchestrator: Calling API Agent to get daily market data...")
    try:
        raw_market_data = get_daily_market_data_from_api_agent(api_agent_base_url=API_AGENT_BASE_URL)
        print(f"Orchestrator: API Agent returned data for {len(raw_market_data.get('stocks',[]))} stocks and {len(raw_market_data.get('earnings_surprises',[]))} earnings surprises.")
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=503, detail=f"Failed to connect to API Agent: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching data from API Agent: {e}")

    # --- Step 2: Preprocess Data for Retrieval (using data_ingestion/preprocess.py) ---
    print("Orchestrator: Preprocessing raw market data for retrieval...")
    documents_for_retrieval = format_market_data_for_retrieval(raw_market_data)
    print(f"Orchestrator: Prepared {len(documents_for_retrieval)} documents for indexing.")

    # --- Step 3: Index Data (via Retriever Agent Microservice) ---
    print("Orchestrator: Calling Retriever Agent to index data...")
    try:
        index_payload = {
            "documents": [d["content"] for d in documents_for_retrieval],
            "metadata": [d["metadata"] for d in documents_for_retrieval]
        }
        index_response = requests.post(f"{RETRIEVER_AGENT_BASE_URL}/index_data", json=index_payload)
        index_response.raise_for_status()
        indexed_count = index_response.json().get("indexed_count", 0)
        print(f"Orchestrator: Retriever Agent indexed {indexed_count} documents.")
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=503, detail=f"Failed to connect to Retriever Agent for indexing: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error indexing data via Retriever Agent: {e}")

    # --- Step 4: Analyze Data (via Analysis Agent Microservice) ---
    print("Orchestrator: Calling Analysis Agent to derive insights...")
    try:
        analysis_payload = {"raw_data": raw_market_data}
        analysis_response = requests.post(f"{ANALYSIS_AGENT_BASE_URL}/analyze_market_data", json=analysis_payload)
        analysis_response.raise_for_status()
        analytical_insights = analysis_response.json()
        print("Orchestrator: Analysis Agent returned insights.")
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=503, detail=f"Failed to connect to Analysis Agent: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error analyzing data via Analysis Agent: {e}")

    # --- Step 5: Retrieve Relevant Chunks (via Retriever Agent Microservice) ---
    retrieval_query = request.text_query
    print(f"Orchestrator: Calling Retriever Agent to retrieve chunks for query: '{retrieval_query}'...")
    try:
        retrieve_payload = {"query": retrieval_query, "k": 5}
        retrieve_response = requests.post(f"{RETRIEVER_AGENT_BASE_URL}/retrieve_chunks", json=retrieve_payload)
        retrieve_response.raise_for_status()
        retrieved_chunks = retrieve_response.json().get("chunks", [])
        print(f"Orchestrator: Retriever Agent returned {len(retrieved_chunks)} chunks.")
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=503, detail=f"Failed to connect to Retriever Agent for retrieval: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving chunks via Retriever Agent: {e}")

    # --- Step 6: Synthesize Narrative (via Language Agent) ---
    final_context_for_llm = retrieved_chunks
    if analytical_insights.get("portfolio_allocation"):
        alloc = analytical_insights["portfolio_allocation"]
        final_context_for_llm.append(
            f"Portfolio: Asia tech allocation is {alloc['current_percentage']}% of AUM, "
            f"up {alloc['change_points']}% from {alloc['previous_percentage']}% yesterday."
        )
    for earnings_sum in analytical_insights.get("earnings_summaries", []):
        final_context_for_llm.append(
            f"Earnings: {earnings_sum['company_name']} ({earnings_sum['symbol']}) "
            f"{earnings_sum['surprise_type']} estimates by {earnings_sum['percentage']}%. "
            f"Reason: {earnings_sum.get('reason_keywords', 'No specific reason provided')}."
        )
    if analytical_insights.get("market_sentiment"):
        sentiment = analytical_insights["market_sentiment"]
        final_context_for_llm.append(
            f"Sentiment: Regional sentiment is {sentiment['sentiment']} with a {sentiment.get('tilt', '')} "
            f"due to {sentiment.get('reason', 'unspecified reasons')}."
        )

    print("Orchestrator: Calling Language Agent to synthesize market brief...")
    try:
        synthesized_brief = language_agent_instance.synthesize_market_brief(request.text_query, final_context_for_llm)
        print("Orchestrator: Market brief synthesized by Language Agent.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error synthesizing brief with Language Agent: {e}")

    print("Orchestrator: Market brief generation complete.")
    # <--- MODIFIED: Return both brief and raw data
    return OrchestratorResponse(
        market_brief_text=synthesized_brief,
        raw_stock_prices=raw_market_data.get("stocks", []),
        raw_earnings_surprises=raw_market_data.get("earnings_surprises", [])
    )