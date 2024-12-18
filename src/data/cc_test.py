
from cc_news import CryptoNewsFetcher
def test_crypto_news_fetcher():
    try:
        # Initialize with your API key
        api_key = ""
        fetcher = CryptoNewsFetcher(api_key)
        
        # Test fetching Bitcoin and Ethereum news
        print("Fetching BTC and ETH news...")
        news_df, success = fetcher.get_news_by_coin(
            categories="BTC",
            limit=10,
            lang="EN"
        )
        
        if success and not news_df.empty:
            print(f"\nFound {len(news_df)} news articles")
            
            # Save to CSV
            if fetcher.save_news(news_df, 'crypto_news.csv'):
                print("News saved successfully")
            
            # Get and print statistics
            stats = fetcher.get_news_stats(news_df)
            if stats:
                print("\nNews Statistics:")
                for key, value in stats.items():
                    print(f"{key}: {value}")
            
            # Print latest article details
            if not news_df.empty:
                latest_article = news_df.iloc[0]
                print("\nLatest Article:")
                print(f"Title: {latest_article['title']}")
                print(f"Source: {latest_article['source_name']}")
                print(f"Published: {latest_article['published_on']}")
                print(f"URL: {latest_article['url']}")
                print(f"Categories: {latest_article['categories']}")
                print(f"Sentiment: {latest_article['sentiment']}")
        else:
            print("No news articles were retrieved")
            
    except Exception as e:
        print(f"Error in test script: {str(e)}")

if __name__ == "__main__":
    test_crypto_news_fetcher()