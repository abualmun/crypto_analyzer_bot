from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.schema import HumanMessage, SystemMessage
from typing import Dict, Optional, Tuple
import pandas as pd
from dotenv import load_dotenv
import os
import requests

class CryptoSentimentAnalyzer:
    def __init__(self, google_api_key: Optional[str] = None):
        """Initialize the sentiment analyzer with Google's Gemini model."""
        if google_api_key:
            self.api_key = google_api_key
        else:
            load_dotenv()
            self.api_key = os.getenv("GOOGLE_API_KEY")
            
        if not self.api_key:
            raise ValueError("Google API key is required.")

        try:
            self.llm = ChatGoogleGenerativeAI(
                model="gemini-2.0-flash-exp", 
                google_api_key=self.api_key
            )
        except Exception as e:
            print(f"Error initializing Gemini model: {str(e)}")
            raise

    def analyze_sentiment(self, title: str, body: str) -> str:
        """
        Analyze the sentiment of a crypto news article.
        Returns: 'positive', 'negative', or 'neutral'
        """
        combined_text = f"Title: {title}\n\nBody: {body}"
        
        messages = [
            SystemMessage(content="You are a crypto market sentiment analyzer. Analyze the given text and return only 'positive', 'negative', or 'neutral'."),
            HumanMessage(content=f"""
            Analyze the sentiment of this crypto news article and return only one word (positive, negative, or neutral):

            {combined_text}
            """)
        ]
        
        try:
            response = self.llm.invoke(messages)
            sentiment = response.content.strip().lower()
            
            # Ensure valid response
            if sentiment not in ['positive', 'negative', 'neutral']:
                return 'neutral'
                
            return sentiment
        except Exception as e:
            print(f"Error analyzing sentiment: {str(e)}")
            return 'neutral'

    def batch_analyze_articles(self, df: pd.DataFrame) -> pd.DataFrame:
        """Analyze sentiment for multiple articles in a DataFrame."""
        df = df.copy()
        sentiments = []
        
        for _, row in df.iterrows():
            sentiment = self.analyze_sentiment(row['title'], row['body'])
            sentiments.append(sentiment)
            
        df['sentiment'] = sentiments
        return df
