from reddit_news import RedditCryptoScraper
import datetime
# Initialize the scraper
scraper = RedditCryptoScraper(
    client_id='fsd5mS2MEyEUCaHy32G3uQ',
    client_secret='QRGXUcADTr4qDQIiyu_n2PJZHIyQGA',
    user_agent='news/1.0'
)

# Define parameters
crypto_name = "bitcoin"
subreddits = ["bitcoin", "cryptocurrency", "CryptoMarkets"]
start_date = datetime(2024, 1, 1)  # Posts from January 1, 2024

# Get posts
posts_df = scraper.get_crypto_posts(
    crypto_name=crypto_name,
    subreddits=subreddits,
    start_date=start_date
)

# Get comments for a specific post
comments_df = scraper.get_post_comments(posts_df['post_id'].iloc[0])

# Add sentiment analysis
posts_with_sentiment = scraper.analyze_sentiment(posts_df, 'text')
comments_with_sentiment = scraper.analyze_sentiment(comments_df, 'text')