import tweepy
import pandas as pd
from datetime import datetime, timezone
from typing import List, Dict, Optional, Tuple

class TwitterCryptoScraper:
    def __init__(self, bearer_token: str):
        """
        Initialize the Twitter API client.
        
        Args:
            bearer_token (str): Twitter API Bearer Token
        """
        if not bearer_token:
            raise ValueError("Bearer token must be provided")
            
        try:
            self.client = tweepy.Client(
                bearer_token=bearer_token,
                wait_on_rate_limit=True
            )
        except Exception as e:
            raise ValueError(f"Failed to initialize Twitter client: {str(e)}")
    
    def get_crypto_tweets(self, 
                         crypto_name: str,
                         start_time: datetime,
                         max_results: int = 100,
                         include_cashtags: bool = True) -> Tuple[pd.DataFrame, bool]:
        """
        Get tweets related to a specific cryptocurrency.
        
        Args:
            crypto_name (str): Name of the cryptocurrency (e.g., "bitcoin", "ethereum")
            start_time (datetime): Start time for tweet collection
            max_results (int): Maximum number of tweets to fetch (default: 100)
            include_cashtags (bool): Whether to include cashtag search (e.g., $BTC)
            
        Returns:
            Tuple[pd.DataFrame, bool]: (DataFrame containing tweet information, success status)
        """
        if not crypto_name:
            raise ValueError("crypto_name must be provided")
            
        tweets_data = []
        success = False
        
        try:
            # Prepare search query
            query_parts = [crypto_name]
            
            # Add cashtag if requested
            if include_cashtags:
                # Common cashtag mappings
                cashtag_map = {
                    'bitcoin': 'BTC',
                    'ethereum': 'ETH',
                    'binance': 'BNB',
                    'cardano': 'ADA',
                    'solana': 'SOL',
                    'ripple': 'XRP',
                    'dogecoin': 'DOGE',
                    'polkadot': 'DOT'
                }
                if crypto_name.lower() in cashtag_map:
                    query_parts.append(f"${cashtag_map[crypto_name.lower()]}")
            
            # Combine query parts
            query = " OR ".join(query_parts)
            
            # Add filters for better quality tweets
            query += " -is:retweet lang:en"
            
            # Search tweets
            tweets = self.client.search_recent_tweets(
                query=query,
                start_time=start_time,
                max_results=max_results,
                tweet_fields=['created_at', 'public_metrics', 'lang', 'source'],
                user_fields=['username', 'name', 'public_metrics'],
                expansions=['author_id']
            )
            
            if not tweets.data:
                print(f"No tweets found for {crypto_name}")
                return pd.DataFrame(), success
            
            # Create user lookup dictionary
            users = {user.id: user for user in tweets.includes['users']}
            
            # Process tweets
            for tweet in tweets.data:
                user = users.get(tweet.author_id)
                if user:
                    tweets_data.append({
                        'tweet_id': tweet.id,
                        'text': tweet.text,
                        'created_at': tweet.created_at,
                        'retweet_count': tweet.public_metrics['retweet_count'],
                        'reply_count': tweet.public_metrics['reply_count'],
                        'like_count': tweet.public_metrics['like_count'],
                        'quote_count': tweet.public_metrics['quote_count'],
                        'source': tweet.source,
                        'lang': tweet.lang,
                        'author_id': tweet.author_id,
                        'author_username': user.username,
                        'author_name': user.name,
                        'author_followers': user.public_metrics['followers_count'],
                        'author_following': user.public_metrics['following_count'],
                        'author_tweet_count': user.public_metrics['tweet_count']
                    })
            
            success = True
            
        except Exception as e:
            print(f"Error fetching tweets: {str(e)}")
            return pd.DataFrame(), success
        
        return pd.DataFrame(tweets_data), success
    
    def save_tweets(self, df: pd.DataFrame, filename: str) -> bool:
        """
        Save tweets DataFrame to CSV file.
        
        Args:
            df (pd.DataFrame): DataFrame containing tweets
            filename (str): Name of the file to save
            
        Returns:
            bool: True if save was successful, False otherwise
        """
        try:
            df.to_csv(filename, index=False, encoding='utf-8')
            print(f"Successfully saved tweets to {filename}")
            return True
        except Exception as e:
            print(f"Error saving tweets to CSV: {str(e)}")
            return False