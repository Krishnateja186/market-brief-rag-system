# data_ingestion/preprocess.py
from typing import List, Dict, Any

def format_market_data_for_retrieval(market_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Takes structured market data and formats it into documents for retrieval.
    Each item in the list will be a document for the Retriever Agent.
    """
    documents = []
    # Example: Convert stock data into a retrievable document
    for stock in market_data.get("stocks", []):
        doc_content = (
            f"{stock['name']} ({stock['symbol']}) closed at ${stock['price']:.2f} "
            f"on {stock['date']}."
        )
        documents.append({"content": doc_content, "metadata": {"type": "stock_price", "symbol": stock['symbol']}})

    # Example: Convert earnings surprises into a retrievable document
    for earnings in market_data.get("earnings_surprises", []):
        surprise_type = "beat" if earnings.get('surprise_percent', 0) >= 0 else "missed"
        doc_content = (
            f"{earnings['name']} ({earnings['symbol']}) reported earnings on {earnings['date']}, "
            f"with an actual EPS of {earnings['actual_eps']} vs estimated {earnings['estimated_eps']}. "
            f"This was a {surprise_type} of {abs(earnings.get('surprise_percent', 0)):.2f}%."
        )
        if earnings.get('reason_keywords'):
             doc_content += f" Reason: {earnings['reason_keywords']}."
        documents.append({"content": doc_content, "metadata": {"type": "earnings_surprise", "symbol": earnings['symbol']}})

    # Add logic to process scraped filings here too when you implement Scraping Agent
    print(f"DataIngestion: Preprocessed {len(documents)} documents for retrieval from raw market data.")
    return documents