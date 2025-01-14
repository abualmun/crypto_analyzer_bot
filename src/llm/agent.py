from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import initialize_agent, Tool
from langchain_core.tools import tool
from langchain.agents import AgentType
from langchain.schema import HumanMessage, SystemMessage
from typing import Dict, Optional
from dotenv import load_dotenv
import sys
import os

from src.services.database_manager import DatabaseManager
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from src.analysis.technical import TechnicalAnalyzer
from src.utils.formatters import TelegramFormatter
from src.utils.news_formatters import NewsFormatter
from src.data.processor import DataProcessor
from src.data.cc_news import CryptoNewsFetcher

class CryptoAnalysisAgent:
    def __init__(self, google_api_key: str = None):
        """
        Initialize the Crypto Analysis Agent.
        
        Args:
            google_api_key (str, optional): Google API key. If not provided, will try to get from environment.
        """
        self.analyzer = TechnicalAnalyzer()
        self.formatter = TelegramFormatter()
        self.data_processor = DataProcessor()
        self.news_fetcher = CryptoNewsFetcher(os.getenv("CRYPTO_NEWS_TOKEN"))
        self.news_formatter = NewsFormatter()
        self.db_manager = DatabaseManager()

        self.timeframes = {
            '1d': 1,
            '1w': 7,
            '1m': 30,
            '3m': 90
        }
        # Load API key
        if google_api_key:
            self.api_key = google_api_key
        else:
            load_dotenv()
            self.api_key = os.getenv("GOOGLE_API_KEY")
            
        if not self.api_key:
            raise ValueError("Google API key is required. Either pass it to the constructor or set GOOGLE_API_KEY environment variable.")

        # Initialize Gemini model
        try:
            self.llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", google_api_key=self.api_key)
            print("Using Gemini 1.5")
        except Exception as e:
            print(f"Gemini 1.5 not available: {e}")
            self.llm = ChatGoogleGenerativeAI(model="gemini-pro", google_api_key=self.api_key)
            print("Falling back to Gemini Pro")

        # Initialize tools
        self.tools = [
            Tool(
                name="QuickAnalysis",
                func=self._quick_analysis,
                description="Useful for technical analysis of cryptocurrencies. Input should include coin symbol as first parameter and timeframe as second parameter (options: 1d, 1w, 1m, 3m). the Input should be (coin_symbol timeframe)"
            ),
            Tool(
                name="NewsAnalysis",
                func=self._news_analysis,
                description="Useful for analyzing news and sentiment about cryptocurrencies. Input should include coin symbol."
            ),
            Tool(
              name="ExplainIndicator",
              func=self._explain_indicator,
              description="Learn about a technical indicator. Input the indicator name."
            )
        ]
        
        # Initialize the agent
        self.agent = initialize_agent(
            self.tools,
            self.llm,
            agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
            verbose=True
        )

    def _quick_analysis(self, query: str) -> str:
        '''Perform a quick analysis of a cryptocurrency based on the given timeframe.'''
        coin_id, timeframe = query.split(" ", 1)
        print(f"coin_id: {coin_id}, timeframe: {timeframe}")
        if timeframe not in self.timeframes:
           return self.formatter._t('invalid_timeframe_prompt')

        try:
            # Validate coin
            if not self.data_processor.validate_coin_id(coin_id):
               return f"❌ {self.formatter._t('invalid_symbol_prompt')}: {coin_id}"

            # Get analysis
            days = self.timeframes[timeframe]
            analysis = self.analyzer.analyze_coin(coin_id, days=days)
             self.db_manager.log_user_activity({
                'user_id':user_id,
                'coin_id':coin_id,
                'activity_type':'full',
                'timestamp':days})             
            # Send text analysis
            # formatted_message = self.formatter.format_full_analysis(analysis, coin_id)
            print(f"formatted_message: {analysis}")
            # This is a placeholder - implement your actual analysis here
            analysis_prompt = self.formatter._t('analysis_prompt').format(
               coin_id=coin_id,
               timeframe=timeframe,
               analysis=analysis
            ) 
            response = self.llm.invoke([HumanMessage(content=analysis_prompt)])
            return response.content

        except Exception as e:
            print(str(e))
            return(self.formatter._t('analysis_error').format(error=str(e)))
        
    

    def _news_analysis(self, query: str) -> str:
        # Get news articles
        news_df, success = self.news_fetcher.get_news_by_coin(
            categories=query,
            limit=10,
            lang="EN"
        )
        
        if not success or news_df.empty:
            formatted_message= self.formatter._t('no_news_found').format(symbol=query)
        # Get formatted message
        formatted_message = self.news_formatter.format_news(news_df, query)
        # This is a placeholder - implement your actual analysis here
        news_prompt = self.formatter._t('news_analysis_prompt').format(
           query=query,
           news=formatted_message)
        response = self.llm.invoke([HumanMessage(content=news_prompt)])
        return response.content
    
    def _explain_indicator(self, query: str) -> str:
        """
        Explain a technical indicator based on user input.

        Args:
            query (str): Name of the technical indicator.

        Returns:
            str: Explanation of the indicator retrieved from the LLM.
        """
        indicator_name = query.strip()

        # If no external source, use a generic prompt
        indicator_prompt = self.formatter._t('indicator_explanation_prompt').format(
           indicator=indicator_name
       )
        response = self.llm.invoke([HumanMessage(content=indicator_prompt)])
        return response.content

    def process_query(self, text: str) -> str:
        """
        Process a user query and return the response.
        
        Args:
            text (str): The user's query text
            
        Returns:
            str: The processed response
            
        Raises:
            ValueError: If the query couldn't be processed
            Exception: For other unexpected errors
        """
        try:
            result = self.agent.invoke(text)
            return result
        except ValueError as e:
            if "Could not parse LLM output" in str(e):
                return {
                   'output': self.formatter._t('query_parse_error')
               }
            raise e
        except Exception as e:
           raise Exception(self.formatter._t('query_error').format(error=str(e)))

def main():
    """Example usage of the CryptoAnalysisAgent"""
    
    # Initialize the agent
    agent = CryptoAnalysisAgent()
    
    # Interactive loop
    print("Crypto Analysis Agent (type 'exit' to quit)")
    print("Example queries:")
    print("- Analyze BTC price for the next hour")
    print("- What's the latest news about ETH?")
    print("- Can you explain what RSI means?")
    
    while True:
        user_input = input("\nEnter your query: ")
        if user_input.lower() == 'exit':
            break
            
        try:
            result = agent.process_query(user_input)
            print(f"\nResponse: {result}")
        except Exception as e:
            print(f"\nError: {str(e)}")

if __name__ == "__main__":
    main()