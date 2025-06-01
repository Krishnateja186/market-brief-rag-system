# scripts/index_market_data.py

import requests
import json
import os

# --- IMPORTANT: Replace with your actual Render service URL for the Retriever Agent ---
# Example: "https://my-retriever-agent-xyz.onrender.com"
RETRIEVER_AGENT_URL = "https://your-retriever-agent-service.onrender.com" 

INDEX_ENDPOINT = f"{RETRIEVER_AGENT_URL}/index_data"

print(f"--- INDEXING SCRIPT ---")
print(f"Targeting Retriever Agent URL: {RETRIEVER_AGENT_URL}")

# These are sample "market brief" type documents that your web scraper 
# or data pipeline might feed into the Retriever Agent.
documents_for_indexing = [
    "Apple Inc. reported strong Q3 earnings, surpassing analyst expectations with iPhone sales leading the growth. The stock (AAPL) saw a 2% increase in after-hours trading, pushing its valuation higher.",
    "The Federal Reserve hinted at potential interest rate hikes in the upcoming quarter, citing persistent inflation concerns and a robust job market. This news caused a slight dip in technology stocks and a surge in bond yields.",
    "Tesla announced plans for a new gigafactory in Texas, aiming to significantly boost EV production capacity. This expansion could help them meet global demand and impact their market share in the next two years, despite supply chain challenges.",
    "Global oil prices surged following geopolitical tensions in the Middle East, with Brent crude reaching $90 a barrel. Analysts expect continued volatility, which will benefit energy sector stocks like ExxonMobil.",
    "The S&P 500 closed higher today, driven by strong performance in the consumer discretionary sector, particularly retail and e-commerce companies, despite mixed signals from the manufacturing industry PMI.",
    "A recent report from the International Monetary Fund (IMF) projects global economic growth to slow down in the next fiscal year due to persistent inflationary pressures and tighter monetary policies across major economies.",
    "Amazon's cloud division, AWS, continues to be a major revenue driver, with strong growth reported in enterprise adoption. The company is investing heavily in AI infrastructure to support new generative AI services.",
    "Gold prices remained stable amid global uncertainties, serving as a safe-haven asset. Demand from central banks continues to provide a floor to the market."
]

# Optional metadata for each document (useful for tracking source, date, etc.)
metadata_for_indexing = [
    {"source": "Financial News Digest", "date": "2024-05-15", "company": "Apple"},
    {"source": "Economic Analyst Brief", "date": "2024-05-20", "topic": "Monetary Policy"},
    {"source": "TechCrunch Article", "date": "2024-05-22", "company": "Tesla"},
    {"source": "Reuters Market Report", "date": "2024-05-25", "commodity": "Oil"},
    {"source": "Daily Market Summary", "date": "2024-05-28", "index": "S&P 500"},
    {"source": "IMF Global Outlook", "date": "2024-05-30", "organization": "IMF"},
    {"source": "Cloud Computing Insights", "date": "2024-06-01", "company": "Amazon"},
    {"source": "Precious Metals Update", "date": "2024-06-01", "commodity": "Gold"}
]

index_payload = {
    "documents": documents_for_indexing,
    "metadata": metadata_for_indexing
}

print(f"\nAttempting to index {len(documents_for_indexing)} sample documents...")
try:
    response = requests.post(INDEX_ENDPOINT, json=index_payload)
    response.raise_for_status() # Raise HTTPError for bad responses (4xx or 5xx)
    print("Indexing successful!")
    print("Response from server:", response.json())
except requests.exceptions.RequestException as e:
    print(f"CRITICAL ERROR: Failed to index documents: {e}")
    if response and hasattr(response, 'status_code') and hasattr(response, 'text'):
        print(f"Response status: {response.status_code}")
        print(f"Response body: {response.text}")
    else:
        print("No response object available or attributes missing.")