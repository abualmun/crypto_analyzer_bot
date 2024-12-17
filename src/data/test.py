from reddit_news import RedditCryptoScraper
from datetime import datetime, timedelta, timezone
import pandas as pd
from x_news import TwitterCryptoScraper
# Initialize the scraper with your Twitter API bearer token
scraper = TwitterCryptoScraper(
    bearer_token='AAAAAAAAAAAAAAAAAAAAAGxpxgEAAAAAvswnYGx52TllBHPvW%2BrBCcO%2BXiM%3DJejS5cVhUTSnegWyXRUwccr7a8fn4UKRdkoopMEPQnntjQft7l'
)

# Set parameters
crypto_name = "bitcoin"
start_time = datetime.now(timezone.utc) - timedelta(days=7)  # Last 7 days

# Get tweets
tweets_df, success = scraper.get_crypto_tweets(
    crypto_name=crypto_name,
    start_time=start_time,
    max_results=10
)

# Save tweets if successful
if success and not tweets_df.empty:
    scraper.save_tweets(tweets_df, 'bitcoin_tweets.csv')

# # Initialize the scraper
# scraper = RedditCryptoScraper(
#     client_id = "rPojxiOO1M1_1HVS31f-zg",
#     client_secret = "TPpmfycGPXS4vZnR9jJRORxbjvPXmQ",
#     user_agent = "python:mycryptoapp:v1.0 (by /u/Osman_Fox_1993)"
# )

# # Define parameters
# crypto_name = "BTC"
# subreddits = ["Altcoin", "CryptoCurrency", "CryptoMarkets"]
# start_date = datetime.now() - timedelta(days=7)

# # Get posts
# posts_df, success  = scraper.get_crypto_posts(
#     crypto_name=crypto_name,
#     subreddits=subreddits,
#     start_date=start_date
# )

# # Get comments for a specific post
# if success and not posts_df.empty:
#     comments_df = scraper.get_post_comments(posts_df['post_id'].iloc[0])
#     print(f"Found {len(comments_df)} comments")
# else:
#     print("No posts found to fetch comments from")

# # Add sentiment analysis
# posts_with_sentiment = scraper.analyze_sentiment(posts_df, 'text')
# comments_with_sentiment = scraper.analyze_sentiment(comments_df, 'text')
# posts_with_sentiment.to_csv('posts_sentiment.csv')
# comments_with_sentiment.to_csv('comments_sentiment.csv')
# print(posts_with_sentiment)
# print(comments_with_sentiment)