# test_fetch_news.py

from data_ingestion.fetch_data import fetch_earnings_news

def test_news_fetch():
    stock_name = "TSMC"
    news = fetch_earnings_news(stock_name)

    print(f"\nEarnings News for {stock_name.upper()}:\n" + "-"*40)
    
    if isinstance(news, list):
        for article in news:
            print(f"📰 {article['title']}\n🔗 {article['url']}\n")
    else:
        print("❌ Error:", news.get("error", "Unknown error"))

if __name__ == "__main__":
    test_news_fetch()
