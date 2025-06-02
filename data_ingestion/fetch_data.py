# data_ingestion/fetch_data.py

import requests
from typing import List, Dict, Any, Optional
# Removed: import os (no longer needed here for API_AGENT_BASE_URL)

# Removed: Global API_AGENT_BASE_URL and API_AGENT_URL variables.
# These will now be passed as arguments to the functions.

def get_daily_market_data_from_api_agent(
    api_agent_base_url: str, # NEW: Accept base URL as argument
    symbols: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Calls the API Agent microservice to get daily market data for specified symbols.

    Args:
        api_agent_base_url (str): The base URL of the deployed API Agent microservice.
        symbols (Optional[List[str]]): A list of stock symbols to fetch data for.
                                        If None, the API Agent will use its default list.

    Returns:
        Dict[str, Any]: The JSON response from the API Agent containing market data.

    Raises:
        requests.exceptions.RequestException: If an HTTP error occurs (e.g., 4xx, 5xx).
    """
    # Construct the full URL using the passed base_url
    api_agent_full_url = f"{api_agent_base_url}/get_daily_asia_tech_market_data"
    print(f"DataIngestion: Fetching daily market data from API Agent at {api_agent_full_url}...")
    payload = {"request_symbols": symbols or []}
    response = requests.post(api_agent_full_url, json=payload) # Use the new full URL
    response.raise_for_status() # Raise an exception for HTTP errors (4xx or 5xx)
    data = response.json()
    print(f"DataIngestion: Received market data: {len(data.get('stocks', []))} stocks, {len(data.get('earnings_surprises', []))} earnings surprises.")
    return data

def get_filings_from_scraping_agent(
    scraping_agent_base_url: str, # NEW: Accept base URL as argument
    query: str, 
    limit: int = 5
) -> List[Dict[str, Any]]:
    """
    Calls the Scraping Agent microservice to get relevant filings or news.

    Args:
        scraping_agent_base_url (str): The base URL of the deployed Scraping Agent microservice.
        query (str): The query for relevant filings or news.
        limit (int): The maximum number of documents to retrieve.

    Returns:
        List[Dict[str, Any]]: A list of dictionaries, each representing a scraped document.

    Raises:
        requests.exceptions.RequestException: If an HTTP error occurs (e.g., 4xx, 5xx).
    """
    # Construct the full URL using the passed base_url
    scraping_agent_full_url = f"{scraping_agent_base_url}/scrape_data"
    print(f"DataIngestion: Fetching filings/news from Scraping Agent at {scraping_agent_full_url} for query: '{query}'...")
    payload = {"query": query, "limit": limit}
    response = requests.post(scraping_agent_full_url, json=payload) # Use the new full URL
    response.raise_for_status()
    data = response.json()
    scraped_documents = data.get("documents", [])
    print(f"DataIngestion: Received {len(scraped_documents)} documents from Scraping Agent.")
    return scraped_documents

# You can add other raw data fetching functions here as needed for different sources.

# Note: The content for data_ingestion/preprocess.py should be in its own file
# if you intend to keep your project structure clean.