# orchestrator/main.py

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import requests # For making HTTP requests to other microservices
from typing import List, Dict, Any, Optional
import asyncio # For async HTTP calls

# Import agent classes directly if they are not exposed as microservices (e.g., LanguageAgent)
from agents.language_agent import LanguageAgent # LanguageAgent will be instantiated directly
# from agents.voice_agent import VoiceAgent # Will import this when created

# Import helper functions from data_ingestion
# THIS IS THE LINE THAT MUST BE CORRECT:
from data_ingestion.fetch_data import get_daily_market_data_from_api_agent # <--- ENSURE THIS LINE IS EXACTLY AS SHOWN!
from data_ingestion.preprocess import format_market_data_for_retrieval

app = FastAPI(
    title="Stock Orchestrator Microservice",
    description="Coordinates all agents to deliver the Morning Market Brief."
)

# --- Configure URLs for other microservices ---
API_AGENT_BASE_URL = "https://market-brief-rag-system-1.onrender.com"
RETRIEVER_AGENT_BASE_URL = "http://localhost:8002"
ANALYSIS_AGENT_BASE_URL = "http://localhost:8003"
STT_AGENT_BASE_URL = "http://localhost:8004" # Assuming you create a voice_io/stt_service.py
TTS_AGENT_BASE_URL = "http://localhost:8005" # Assuming you create a voice_io/tts_service.py

# Initialize LanguageAgent (as it's directly imported)
try:
    language_agent_instance = LanguageAgent()
except Exception as e:
    print(f"CRITICAL ERROR: Orchestrator failed to initialize LanguageAgent: {e}")
    language_agent_instance = None


class BriefRequest(BaseModel):
    text_query: str # User's query in text format
    # audio_file: Optional[bytes] = None # For voice input, would be handled by Streamlit sending bytes

@app.get("/")
def root():
    return {"message": "Orchestrator is running. Go to /docs for usage."}

@app.post("/generate_market_brief")
async def generate_market_brief_endpoint(request: BriefRequest):
    print(f"\nOrchestrator: Received request to generate market brief for query: '{request.text_query}'")

    if language_agent_instance is None:
        raise HTTPException(status_code=500, detail="Orchestrator: Language Agent not initialized.")

    # --- Step 1: Get Raw Market Data (from API Agent) ---
    print("Orchestrator: Calling API Agent to get daily market data...")
    try:
        # You can specify symbols or let the API agent use its default
        # THIS IS WHERE THE CORRECTED FUNCTION IS USED:
        raw_market_data = get_daily_market_data_from_api_agent() 
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
    # This step would typically be run daily at 8 AM as a separate job,
    # or for new data. For continuous tracking, index whenever new data arrives.
    # For demonstration, we'll index every time.
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
        # print(f"Orchestrator: Insights: {analytical_insights}") # Uncomment for debugging
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=503, detail=f"Failed to connect to Analysis Agent: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error analyzing data via Analysis Agent: {e}")

    # --- Step 5: Retrieve Relevant Chunks (via Retriever Agent Microservice) ---
    # The query for retrieval should be derived from the user's brief request
    retrieval_query = request.text_query
    print(f"Orchestrator: Calling Retriever Agent to retrieve chunks for query: '{retrieval_query}'...")
    try:
        retrieve_payload = {"query": retrieval_query, "k": 5} # Retrieve top 5 relevant chunks
        retrieve_response = requests.post(f"{RETRIEVER_AGENT_BASE_URL}/retrieve_chunks", json=retrieve_payload)
        retrieve_response.raise_for_status()
        retrieved_chunks = retrieve_response.json().get("chunks", [])
        print(f"Orchestrator: Retriever Agent returned {len(retrieved_chunks)} chunks.")
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=503, detail=f"Failed to connect to Retriever Agent for retrieval: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving chunks via Retriever Agent: {e}")

    # --- Step 6: Synthesize Narrative (via Language Agent) ---
    # Combine raw data, analysis insights, and retrieved chunks for the Language Agent's context
    # We'll build the context string from retrieved chunks AND analytical insights
    final_context_for_llm = retrieved_chunks # Start with chunks from Retriever Agent

    # Add structured insights from Analysis Agent to the context
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
        # The LanguageAgent is imported directly, so we call its method
        synthesized_brief = language_agent_instance.synthesize_market_brief(request.text_query, final_context_for_llm)
        print("Orchestrator: Market brief synthesized by Language Agent.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error synthesizing brief with Language Agent: {e}")

    # --- Step 7: (Future) Convert Text to Speech (via TTS Agent Microservice) ---
    # This step will be added when you build the Voice Agent (TTS part)
    # print("Orchestrator: Calling TTS Agent to convert brief to speech...")
    # try:
    #     tts_payload = {"text": synthesized_brief}
    #     tts_response = requests.post(f"{TTS_AGENT_BASE_URL}/text_to_speech", json=tts_payload)
    #     tts_response.raise_for_status()
    #     audio_bytes = tts_response.content # Assuming it returns audio bytes
    #     print("Orchestrator: TTS Agent returned audio.")
    #     # Return audio or a link to audio
    #     return {"market_brief_text": synthesized_brief, "market_brief_audio": audio_bytes}
    # except requests.exceptions.RequestException as e:
    #     raise HTTPException(status_code=503, detail=f"Failed to connect to TTS Agent: {e}")
    # except Exception as e:
    #     raise HTTPException(status_code=500, detail=f"Error converting text to speech: {e}")

    print("Orchestrator: Market brief generation complete (text only for now).")
    return {"market_brief_text": synthesized_brief}

# To run this:
# 1. Ensure all other agents (API, Retriever, Analysis) are running as microservices on their designated ports.
# 2. pip install fastapi uvicorn requests
# 3. From your project root, run: uvicorn orchestrator.main:app --reload --port 8000
# 4. Access it in your browser at http://127.0.0.1:8000/docs