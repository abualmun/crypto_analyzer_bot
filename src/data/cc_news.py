import requests
import pandas as pd
from datetime import datetime
from typing import Dict, List, Tuple, Optional

from ..llm.sentimnet import CryptoSentimentAnalyzer

class CryptoNewsFetcher:
    def __init__(self, api_key: str, google_api_key: Optional[str] = None):
        """
        Initialize the CryptoCompare News API client.
        
        Args:
            api_key (str): CryptoCompare API key
        """
        self.api_key = api_key
        self.base_url = "https://data-api.cryptocompare.com/news/v1/article"
        if google_api_key:
            self.sentiment_analyzer = CryptoSentimentAnalyzer(google_api_key)
    
    def _safe_timestamp_to_datetime(self, timestamp) -> Optional[datetime]:
        """
        Safely convert timestamp to datetime.
        
        Args:
            timestamp: Unix timestamp or None
            
        Returns:
            datetime or None if conversion fails
        """
        try:
            return datetime.fromtimestamp(timestamp) if timestamp else None
        except (TypeError, ValueError):
            return None
    
    def get_news_by_coin(self, 
                        categories: str,
                        limit: int = 10,
                        lang: str = "EN") -> Tuple[pd.DataFrame, bool]:
        """
        Get news articles related to specific cryptocurrency categories.
        
        Args:
            categories (str): Cryptocurrency categories (e.g., 'BTC,ETH')
            limit (int): Maximum number of news articles to fetch
            lang (str): Language of articles (default: 'EN')
            
        Returns:
            Tuple[pd.DataFrame, bool]: (DataFrame containing news articles, success status)
        """
        params = {
            'categories': categories,
            'lang': lang,
            'limit': limit,
            'api_key': self.api_key
        }
        
        headers = {
            'Content-type': 'application/json; charset=UTF-8'
        }
        
        try:
            response = requests.get(
                f"{self.base_url}/list",
                params=params,
                headers=headers
            )
            
            if response.status_code != 200:
                print(f"Error: API returned status code {response.status_code}")
                return pd.DataFrame(), False
                
            data = response.json()
            
            if not data.get('Data'):
                print("No news articles found")
                return pd.DataFrame(), False
            
            articles = []
            
            for article in data['Data']:
                try:
                    # Extract categories safely
                    category_data = article.get('CATEGORY_DATA', [])
                    categories = [cat.get('NAME', '') for cat in category_data if cat.get('NAME')]
                    
                    # Extract source data safely
                    source_data = article.get('SOURCE_DATA', {})
                    
                    articles.append({
                        'id': article.get('ID'),
                        'guid': article.get('GUID'),
                        'published_on': self._safe_timestamp_to_datetime(article.get('PUBLISHED_ON')),
                        'title': article.get('TITLE', ''),
                        'url': article.get('URL', ''),
                        'image_url': article.get('IMAGE_URL', ''),
                        'body': article.get('BODY', ''),
                        'tags': article.get('KEYWORDS', ''),
                        'categories': '|'.join(categories) if categories else '',
                        'language': article.get('LANG', ''),
                        'source_name': source_data.get('NAME', ''),
                        'source_url': source_data.get('URL', ''),
                        'upvotes': article.get('UPVOTES', 0),
                        'downvotes': article.get('DOWNVOTES', 0),
                        'sentiment': article.get('SENTIMENT', ''),
                        'created_on': self._safe_timestamp_to_datetime(article.get('CREATED_ON')),
                        'updated_on': self._safe_timestamp_to_datetime(article.get('UPDATED_ON'))
                    })
                except Exception as e:
                    print(f"Warning: Error processing article: {str(e)}")
                    continue
            
            if not articles:
                print("No valid articles found after processing")
                return pd.DataFrame(), False
            articles = pd.DataFrame(articles)
            
            if self.sentiment_analyzer:
                articles = self.sentiment_analyzer.batch_analyze_articles(pd.DataFrame(articles))
            
            return articles, True
            
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
    
    def get_news_stats(self, df: pd.DataFrame) -> Dict:
        """
        Get basic statistics about the news articles.
        
        Args:
            df (pd.DataFrame): DataFrame containing news articles
            
        Returns:
            Dict: Dictionary containing news statistics
        """
        if df.empty:
            return {}
        
        try:
            # Get all categories (split the '|' separated strings)
            all_categories = [
                cat for cats in df['categories'].dropna() 
                for cat in cats.split('|') if cats
            ]
            
            return {
                'total_articles': len(df),
                'unique_sources': df['source_name'].nunique(),
                'most_common_source': df['source_name'].mode().iloc[0] if not df['source_name'].empty else None,
                'earliest_article': df['published_on'].min(),
                'latest_article': df['published_on'].max(),
                'avg_upvotes': df['upvotes'].mean(),
                'total_upvotes': df['upvotes'].sum(),
                'sentiment_distribution': df['sentiment'].value_counts().to_dict(),
                'top_categories': pd.Series(all_categories).value_counts().head(5).to_dict() if all_categories else {}
            }
        except Exception as e:
            print(f"Error calculating statistics: {str(e)}")
            return {}