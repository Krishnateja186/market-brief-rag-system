# scripts/retrieve_market_data.py

import requests
import json
import os
import time # For a small delay if running right after indexing

# --- IMPORTANT: Replace with your actual Render service URL for the Retriever Agent ---
RETRIEVER_AGENT_URL = "https://your-retriever-agent-service.onrender.com" 

RETRIEVE_ENDPOINT = f"{RETRIEVER_AGENT_URL}/retrieve_chunks"

print(f"--- RETRIEVAL SCRIPT ---")
print(f"Targeting Retriever Agent URL: {RETRIEVER_AGENT_URL}")

# Example queries that your RAG system might receive from users or the orchestrator
# These queries are related to the sample data indexed in the previous script.
project_queries = [
    "Tell me about Apple's latest financial performance.",
    "What are the Federal Reserve's plans regarding interest rates?",
    "Where is Tesla expanding its production?",
    "Why are oil prices going up globally?",
    "What's the current outlook for global economic growth according to the IMF?",
    "How is Amazon's cloud business performing?",
    "What is the current status of gold prices?"
]

# Optional: Add a small delay if you run this immediately after indexing
# time.sleep(5) 

for query_text in project_queries:
    retrieve_payload = {
        "query": query_text,
        "k": 2 # Retrieve the top 2 most relevant chunks for each query
    }

    print(f"\n--- Retrieving chunks for query: '{query_text}' ---")
    try:
        response = requests.post(RETRIEVE_ENDPOINT, json=retrieve_payload)
        response.raise_for_status() # Raise HTTPError for bad responses (4xx or 5xx)

        retrieved_data = response.json()
        chunks = retrieved_data.get("chunks", [])

        if chunks:
            print("Successfully retrieved chunks:")
            for i, chunk in enumerate(chunks):
                print(f"  Chunk {i+1}:")
                # Print first 200 characters for brevity if chunks are long
                print(f"  '{chunk[:200]}{'...' if len(chunk) > 200 else ''}'") 
        else:
            print(f"  No chunks retrieved for '{query_text}'.")
            print("  Consider checking if relevant data was indexed or if query needs refinement.")

    except requests.exceptions.RequestException as e:
        print(f"  Error during retrieval for query '{query_text}': {e}")
        if response and hasattr(response, 'status_code') and hasattr(response, 'text'):
            print(f"  Response status: {response.status_code}")
            print(f"  Response body: {response.text}")
        else:
            print("No response object available or attributes missing.")