# data_ingestion/fetch_data.py

import requests
from typing import List, Dict, Any, Optional

# Assume your API Agent is running on localhost:8001
API_AGENT_URL = "http://localhost:8001/get_daily_asia_tech_market_data"
# Assume your Scraping Agent (if implemented as a service) is on localhost:8004
SCRAPING_AGENT_URL = "http://localhost:8004/scrape_data"

def get_daily_market_data_from_api_agent(symbols: Optional[List[str]] = None) -> Dict[str, Any]:
    """
    Calls the API Agent microservice to get daily market data for specified symbols.

    Args:
        symbols (Optional[List[str]]): A list of stock symbols to fetch data for.
                                        If None, the API Agent will use its default list.

    Returns:
        Dict[str, Any]: The JSON response from the API Agent containing market data.

    Raises:
        requests.exceptions.RequestException: If an HTTP error occurs (e.g., 4xx, 5xx).
    """
    print(f"DataIngestion: Fetching daily market data from API Agent at {API_AGENT_URL}...")
    # THIS LINE HAS BEEN CHANGED:
    payload = {"request_symbols": symbols or []} # <--- CHANGED THIS LINE!
    response = requests.post(API_AGENT_URL, json=payload)
    response.raise_for_status() # Raise an exception for HTTP errors (4xx or 5xx)
    data = response.json()
    print(f"DataIngestion: Received market data: {len(data.get('stocks', []))} stocks, {len(data.get('earnings_surprises', []))} earnings surprises.")
    return data

def get_filings_from_scraping_agent(query: str, limit: int = 5) -> List[Dict[str, Any]]:
    """
    Calls the Scraping Agent microservice to get relevant filings or news.

    Args:
        query (str): The query for relevant filings or news.
        limit (int): The maximum number of documents to retrieve.

    Returns:
        List[Dict[str, Any]]: A list of dictionaries, each representing a scraped document.

    Raises:
        requests.exceptions.RequestException: If an HTTP error occurs (e.g., 4xx, 5xx).
    """
    print(f"DataIngestion: Fetching filings/news from Scraping Agent at {SCRAPING_AGENT_URL} for query: '{query}'...")
    payload = {"query": query, "limit": limit}
    response = requests.post(SCRAPING_AGENT_URL, json=payload)
    response.raise_for_status()
    data = response.json()
    scraped_documents = data.get("documents", [])
    print(f"DataIngestion: Received {len(scraped_documents)} documents from Scraping Agent.")
    return scraped_documents

# You can add other raw data fetching functions here as needed for different sources.