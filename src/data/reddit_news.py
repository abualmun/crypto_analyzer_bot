import praw
from datetime import datetime
import pandas as pd
from typing import List, Dict, Optional

class RedditCryptoScraper:
    def __init__(self, client_id: str, client_secret: str, user_agent: str):
        """
        Initialize the Reddit API client.
        
        Args:
            client_id (str): Reddit API client ID
            client_secret (str): Reddit API client secret
            user_agent (str): User agent string for API requests
        """
        self.reddit = praw.Reddit(
            client_id=client_id,
            client_secret=client_secret,
            user_agent=user_agent
        )
        
    def get_crypto_posts(self, 
                        crypto_name: str, 
                        subreddits: List[str], 
                        start_date: datetime,
                        limit: int = 10) -> pd.DataFrame:
        """
        Get posts related to a specific cryptocurrency from given subreddits.
        
        Args:
            crypto_name (str): Name of the cryptocurrency (e.g., "bitcoin", "ethereum")
            subreddits (List[str]): List of subreddit names to search
            start_date (datetime): Start date for post collection
            limit (int): Maximum number of posts to fetch per subreddit
            
        Returns:
            pd.DataFrame: DataFrame containing post information
        """
        posts_data = []
        
        for subreddit_name in subreddits:
            subreddit = self.reddit.subreddit(subreddit_name)
            
            # Search for posts containing the crypto name
            for post in subreddit.search(crypto_name, limit=limit):
                post_date = datetime.fromtimestamp(post.created_utc)
                
                if post_date >= start_date:
                    posts_data.append({
                        'post_id': post.id,
                        'title': post.title,
                        'text': post.selftext,
                        'score': post.score,
                        'url': post.url,
                        'created_utc': post_date,
                        'author': str(post.author),
                        'num_comments': post.num_comments,
                        'subreddit': subreddit_name,
                        'upvote_ratio': post.upvote_ratio
                    })
        
        return pd.DataFrame(posts_data)
    
    def get_post_comments(self, post_id: str, limit: Optional[int] = None) -> pd.DataFrame:
        """
        Get comments for a specific post.
        
        Args:
            post_id (str): Reddit post ID
            limit (int, optional): Maximum number of comments to fetch
            
        Returns:
            pd.DataFrame: DataFrame containing comment information
        """
        comments_data = []
        submission = self.reddit.submission(id=post_id)
        
        # Replace MoreComments objects with actual comments
        submission.comments.replace_more(limit=limit)
        
        for comment in submission.comments.list():
            comments_data.append({
                'comment_id': comment.id,
                'post_id': post_id,
                'text': comment.body,
                'score': comment.score,
                'created_utc': datetime.fromtimestamp(comment.created_utc),
                'author': str(comment.author),
                'is_submitter': comment.is_submitter,
                'parent_id': comment.parent_id
            })
            
        return pd.DataFrame(comments_data)
    
    def analyze_sentiment(self, df: pd.DataFrame, text_column: str) -> pd.DataFrame:
        """
        Add basic sentiment analysis to the DataFrame.
        
        Args:
            df (pd.DataFrame): DataFrame containing text data
            text_column (str): Name of the column containing text to analyze
            
        Returns:
            pd.DataFrame: DataFrame with added sentiment columns
        """
        try:
            from textblob import TextBlob
        except ImportError:
            raise ImportError("Please install textblob package: pip install textblob")
            
        df = df.copy()
        
        def get_sentiment(text):
            if pd.isna(text) or text == '':
                return 0
            return TextBlob(text).sentiment.polarity
            
        df['sentiment'] = df[text_column].apply(get_sentiment)
        return df