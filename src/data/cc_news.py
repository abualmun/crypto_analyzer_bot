import requests
import pandas as pd
from datetime import datetime
from typing import Dict, List, Tuple, Optional
import time

class CryptoNewsFetcher:    
    def __init__(self, api_key: str):
        """
        Initialize the CryptoCompare News API client.
        
        Args:
            api_key (str): CryptoCompare API key
        """
        self.api_key = api_key
        self.base_url = "https://min-api.cryptocompare.com/data/v2"
        self.headers = {
            'authorization': f'Apikey {self.api_key}'
        }
        
    def get_news_by_coin(self, 
                        coin: str,
                        limit: int = 50,
                        categories: Optional[str] = None) -> Tuple[pd.DataFrame, bool]:
        """
        Get news articles related to a specific cryptocurrency.
        
        Args:
            coin (str): Cryptocurrency symbol (e.g., 'BTC', 'ETH')
            limit (int): Maximum number of news articles to fetch (max 50)
            categories (str, optional): News categories to filter by (e.g., 'Trading,Business')
            
        Returns:
            Tuple[pd.DataFrame, bool]: (DataFrame containing news articles, success status)
        """
        endpoint = f"{self.base_url}/news/"
        
        params = {
            'categories': categories if categories else 'ALL',
            'excludeCategories': 'Sponsored',
            'feeds': 'ALL',
            'limit': min(limit, 50),  # API max is 50
        }
        
        try:
            response = requests.get(
                endpoint,
                headers=self.headers,
                params=params
            )
            
            if response.status_code != 200:
                print(f"Error: API returned status code {response.status_code}")
                return pd.DataFrame(), False
                
            data = response.json()
            
            if not data.get('Data'):
                print("No news articles found")
                return pd.DataFrame(), False
            
            # Filter articles related to the specified coin
            coin = coin.upper()
            articles = []
            
            for article in data['Data']:
                # Check if article is related to the specified coin
                if (coin in article.get('categories', '').upper() or
                    coin in article.get('title', '').upper() or
                    coin in article.get('body', '').upper()):
                    
                    articles.append({
                        'id': article.get('id'),
                        'title': article.get('title'),
                        'body': article.get('body'),
                        'published_at': datetime.fromtimestamp(article.get('published_on', 0)),
                        'url': article.get('url'),
                        'source': article.get('source'),
                        'categories': article.get('categories'),
                        'upvotes': article.get('upvotes', 0),
                        'downvotes': article.get('downvotes', 0),
                        'source_info': {
                            'name': article.get('source_info', {}).get('name'),
                            'lang': article.get('source_info', {}).get('lang'),
                            'img': article.get('source_info', {}).get('img'),
                        }
                    })
            
            if not articles:
                print(f"No articles found specifically about {coin}")
                return pd.DataFrame(), False
            
            return pd.DataFrame(articles), True
            
        except Exception as e:
            print(f"Error fetching news: {str(e)}")
            return pd.DataFrame(), False
    
    def save_news(self, df: pd.DataFrame, filename: str) -> bool:
        """
        Save news DataFrame to CSV file.
        
        Args:
            df (pd.DataFrame): DataFrame containing news articles
            filename (str): Name of the file to save
            
        Returns:
            bool: True if save was successful, False otherwise
        """
        try:
            df.to_csv(filename, index=False, encoding='utf-8')
            print(f"Successfully saved news articles to {filename}")
            return True
        except Exception as e:
            print(f"Error saving news to CSV: {str(e)}")
            return False
            
    def get_coin_news_stats(self, df: pd.DataFrame) -> Dict:
        """
        Get basic statistics about the news articles.
        
        Args:
            df (pd.DataFrame): DataFrame containing news articles
            
        Returns:
            Dict: Dictionary containing news statistics
        """
        if df.empty:
            return {}
            
        return {
            'total_articles': len(df),
            'unique_sources': df['source'].nunique(),
            'most_common_source': df['source'].mode().iloc[0],
            'earliest_article': df['published_at'].min(),
            'latest_article': df['published_at'].max(),
            'avg_upvotes': df['upvotes'].mean(),
            'total_upvotes': df['upvotes'].sum(),
            'categories': ', '.join(sorted(set(
                cat for cats in df['categories'].dropna() 
                for cat in cats.split('|')
            )))
        }