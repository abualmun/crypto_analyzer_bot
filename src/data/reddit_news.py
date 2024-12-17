import praw
from datetime import datetime
import pandas as pd
from typing import List, Dict, Optional, Tuple
from prawcore.exceptions import ResponseException, OAuthException

class RedditCryptoScraper:
    def __init__(self, client_id: str, client_secret: str, user_agent: str):
        """
        Initialize the Reddit API client in read-only mode.
        
        Args:
            client_id (str): Reddit API client ID
            client_secret (str): Reddit API client secret
            user_agent (str): User agent string for API requests
        """
        if not all([client_id, client_secret, user_agent]):
            raise ValueError("All credentials (client_id, client_secret, user_agent) must be provided")
            
        try:
            self.reddit = praw.Reddit(
                client_id=client_id,
                client_secret=client_secret,
                user_agent=user_agent,
                check_for_async=False,
                read_only=True  # Set to read-only mode
            )
        except Exception as e:
            raise ValueError(f"Failed to initialize Reddit client: {str(e)}")
        
    def get_crypto_posts(self, 
                        crypto_name: str, 
                        subreddits: List[str], 
                        start_date: datetime,
                        limit: int = 100) -> Tuple[pd.DataFrame, bool]:
        """
        Get posts related to a specific cryptocurrency from given subreddits.
        
        Args:
            crypto_name (str): Name of the cryptocurrency (e.g., "bitcoin", "ethereum")
            subreddits (List[str]): List of subreddit names to search
            start_date (datetime): Start date for post collection
            limit (int): Maximum number of posts to fetch per subreddit
            
        Returns:
            Tuple[pd.DataFrame, bool]: (DataFrame containing post information, success status)
        """
        if not crypto_name or not subreddits:
            raise ValueError("Both crypto_name and subreddits must be provided")
            
        posts_data = []
        success = False
        
        for subreddit_name in subreddits:
            try:
                subreddit = self.reddit.subreddit(subreddit_name)
                
                # Test if we can access the subreddit
                subreddit.created_utc
                
                # Search for posts containing the crypto name
                for post in subreddit.search(crypto_name, sort='new', time_filter='all', limit=limit):
                    post_date = datetime.fromtimestamp(post.created_utc)
                    
                    if post_date >= start_date:
                        try:
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
                            success = True
                        except AttributeError as e:
                            print(f"Warning: Skipping post due to missing attribute: {e}")
                            continue
                            
            except Exception as e:
                print(f"Warning: Failed to fetch posts from r/{subreddit_name}: {str(e)}")
                continue
                
        if not posts_data:
            print(f"Warning: No posts found for {crypto_name} in the specified subreddits")
            return pd.DataFrame(), success
            
        return pd.DataFrame(posts_data), success
    
    def get_post_comments(self, post_id: str, limit: Optional[int] = None) -> pd.DataFrame:
        """
        Get comments for a specific post.
        
        Args:
            post_id (str): Reddit post ID
            limit (int, optional): Maximum number of comments to fetch
            
        Returns:
            pd.DataFrame: DataFrame containing comment information
        """
        if not post_id:
            raise ValueError("post_id must be provided")
            
        comments_data = []
        
        try:
            submission = self.reddit.submission(id=post_id)
            
            # Replace MoreComments objects with actual comments
            submission.comments.replace_more(limit=limit)
            
            for comment in submission.comments.list():
                try:
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
                except AttributeError as e:
                    print(f"Warning: Skipping comment due to missing attribute: {e}")
                    continue
                    
        except Exception as e:
            print(f"Error fetching comments: {str(e)}")
            return pd.DataFrame()
            
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