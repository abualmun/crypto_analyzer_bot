# Test script
from datetime import datetime, timedelta
from cc_news import CryptoNewsFetcher

def test_crypto_news_fetcher():
    # Initialize with your API key
    api_key = "db3e71ff9c89b30641c901d715dc720228f1495e77e1795dc16e77b946dcfea6"
    fetcher = CryptoNewsFetcher(api_key)
    
    # Test fetching Bitcoin news
    print("Fetching Bitcoin news...")
    btc_news_df, btc_success = fetcher.get_news_by_coin(
        coin='BTC',
        limit=20,
        categories='Trading,Business'
    )
    
    if btc_success:
        print(f"Found {len(btc_news_df)} Bitcoin news articles")
        
        # Save to CSV
        fetcher.save_news(btc_news_df, 'bitcoin_news.csv')
        
        # Get and print statistics
        stats = fetcher.get_coin_news_stats(btc_news_df)
        print("\nNews Statistics:")
        for key, value in stats.items():
            print(f"{key}: {value}")
        
        # Print first article details
        if not btc_news_df.empty:
            first_article = btc_news_df.iloc[0]
            print("\nLatest Article:")
            print(f"Title: {first_article['title']}")
            print(f"Source: {first_article['source']}")
            print(f"Published: {first_article['published_at']}")
            print(f"URL: {first_article['url']}")
    
    # Test fetching Ethereum news
    print("\nFetching Ethereum news...")
    eth_news_df, eth_success = fetcher.get_news_by_coin('ETH', limit=20)
    
    if eth_success:
        print(f"Found {len(eth_news_df)} Ethereum news articles")

if __name__ == "__main__":
    test_crypto_news_fetcher()