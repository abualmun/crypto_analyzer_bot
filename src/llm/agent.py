from langchain.agents.structured_chat.base import create_structured_chat_agent
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.tools import StructuredTool
from langchain.agents import AgentExecutor
from src.data.cc_news import CryptoNewsFetcher
from src.data.processor import DataProcessor
from src.utils.news_formatters import NewsFormatter
from src.utils.formatters import TelegramFormatter
from src.analysis.technical import TechnicalAnalyzer
import asyncio
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import initialize_agent, Tool
from langchain_core.tools import tool
from langchain.agents import AgentType
from langchain.schema import HumanMessage, SystemMessage
from typing import Dict, Optional
from dotenv import load_dotenv
import sys
import os
from telegram import Update
from telegram.ext import ContextTypes

from src.services.database_manager import DatabaseManager
sys.path.append(os.path.abspath(os.path.join(
    os.path.dirname(__file__), '..', '..')))


from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import AgentExecutor
from langchain.tools import StructuredTool
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.agents.structured_chat.base import create_structured_chat_agent
from langchain.schema import HumanMessage, SystemMessage
from typing import Dict, Optional
from dotenv import load_dotenv
import sys
import os

class CryptoAnalysisAgent:
    def __init__(self, google_api_key: str = None):
        """Initialize the Crypto Analysis Agent."""
        # Initialize all your existing components
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

        # Initialize LLM
        if google_api_key:
            self.api_key = google_api_key
        else:
            load_dotenv()
            self.api_key = os.getenv("GOOGLE_API_KEY")
            
        if not self.api_key:
            raise ValueError("Google API key is required.")

        try:
            self.llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash-exp", google_api_key=self.api_key)
        except Exception as e:
            print(f"Gemini 1.5 not available: {e}")
            self.llm = ChatGoogleGenerativeAI(model="gemini-pro", google_api_key=self.api_key)

        # Define tools with improved structure
        self.tools = [
            StructuredTool.from_function(
                name="QuickAnalysis",
                func=self._quick_analysis,
                description="Performs technical analysis of cryptocurrencies. Input format: {'coin': 'string', 'timeframe': 'string'}. coin example: bitcoin, ethereum. Valid timeframes: 1d, 1w, 1m, 3m"
            ),
            StructuredTool.from_function(
                name="NewsAnalysis",
                func=self._news_analysis,
                description="Analyzes news and sentiment about cryptocurrencies. Input format: {'coin': 'string'} coin example: bitcoin, ethereum."
            ),
            StructuredTool.from_function(
                name="ExplainIndicator",
                func=self._explain_indicator,
                description="Explains technical indicators. Input format: {'indicator': 'string'}"
            )
        ]

        # Create structured chat prompt with improved system message and output format
        system_template = """You are a cryptocurrency expert who provides data-based responses. The language of your response MUST EXACTLY MATCH the language of the user's input message - this is CRITICAL.

Available Tools:
{tools}

When using tools, format your output as. Your response MUST be in this exact JSON format:
{{
    "action": $TOOL_NAME,
    "action_input": $INPUT
}}

When providing final answers, use ONLY this format. Your response MUST be in this exact JSON format:
{{
    "action": "Final Answer",
    "action_input": "Your answer here"
}}

Valid actions: "Final Answer" or {tool_names}

CRITICAL LANGUAGE RULE:
- You MUST RESPOND IN THE EXACT SAME LANGUAGE AS THE INPUT MESSAGE
- Example: If user asks in Arabic, respond in Arabic
- Example: If user asks in English, respond in English

QUERY TYPE IDENTIFICATION:

1. PRICE CHECK QUERIES:
   When user asks questions like:
   - "What's the current price of Bitcoin?"
   - "ما هو سعر البيتكوين الحالي؟"
   - "¿Cuál es el precio actual de Bitcoin?"
   
   DO THIS:
   1. Use QuickAnalysis tool to get current data
   2. Extract ONLY the current price
   3. Respond with ONLY the price in a simple sentence
   4. DO NOT provide analysis, signals, or other information
   
   Example Response Format:
   - English: "Bitcoin's current price is $52,340."
   - Arabic: "سعر البيتكوين الحالي هو 52,340 دولار."
   - Spanish: "El precio actual de Bitcoin es $52,340."

2. ANALYSIS REQUESTS:
   When user explicitly asks for analysis/opinion/trends, then provide full analysis:

   A. POSITION STATEMENT:
      Start with "I am [BULLISH/BEARISH] on [COIN] because..."

   B. KEY SIGNALS (Minimum 3):
      - List strongest signals with numbers
      - Explain signal importance

   C. ENTRY/EXIT LEVELS:
      - Entry price range
      - Stop-loss level
      - Take-profit targets
      - Risk/reward ratio

   D. TIMEFRAME & RISK ASSESSMENT:
      - Expected timeframe
      - Invalidation points

CRITICAL RULES:
1. For price questions: ONLY give current price, nothing else
2. For analysis requests: Provide full structured analysis
3. ALWAYS match input language exactly
4. ALWAYS use tools to get real data
5. NEVER provide analysis unless specifically requested

Remember: 
- Simple price questions = Simple price answers
- Analysis only when explicitly requested
- Final answer MUST match input language exactly"""
        human_template = """{input}
{agent_scratchpad}"""

        self.prompt = ChatPromptTemplate.from_messages([
            ("system", system_template),
            # MessagesPlaceholder(variable_name="chat_history", optional=True),
            ("human", human_template),
        ])

        # Initialize structured chat agent
        agent = create_structured_chat_agent(
            llm=self.llm,
            tools=self.tools,
            prompt=self.prompt
        )

        # Create agent executor
        self.agent_executor = AgentExecutor(
            agent=agent,
            tools=self.tools,
            verbose=True,
            handle_parsing_errors=True,
            max_iterations=5
        )

    def _format_analysis_response(self, analysis_text: str) -> str:
        """Format the analysis response to ensure it's a simple string."""
        return f"""ANALYSIS SUMMARY:
{analysis_text}

Note: This analysis is for informational purposes only and does not constitute financial advice."""

    def _quick_analysis(self, coin: str, timeframe: str) -> str:
        """Perform technical analysis with structured input."""
        if timeframe not in self.timeframes:
            return self.formatter._t('invalid_timeframe_prompt')

        try:
            if not self.data_processor.validate_coin_id(coin):
                return f"❌ {self.formatter._t('invalid_symbol_prompt')}: {coin}"

            days = self.timeframes[timeframe]
            analysis = self.analyzer.analyze_coin(coin, days=days)
            
            analysis_prompt = f"""Based on the technical analysis for {coin} over {timeframe}:
{analysis}

Provide a concise analysis including:
1. Current trend direction
2. Key support/resistance levels
3. Trading signals
4. Price targets
5. Risk levels"""

            response = self.llm.invoke([HumanMessage(content=analysis_prompt)])
            return self._format_analysis_response(response.content)

        except Exception as e:
            return self.formatter._t('analysis_error').format(error=str(e))

    def _news_analysis(self, coin: str) -> str:
        """Analyze news with structured input."""
        news_df, success = self.news_fetcher.get_news_by_coin(
            categories=coin,
            limit=10,
            lang="EN"
        )
        
        if not success or news_df.empty:
            return self.formatter._t('no_news_found').format(symbol=coin)

        formatted_news = self.news_formatter.format_news(news_df, coin)
        news_prompt = f"""Analyze the following news for {coin}:
{formatted_news}

Provide a concise summary of:
1. Market sentiment
2. Key events
3. Potential price impact
4. Risks and opportunities"""

        response = self.llm.invoke([HumanMessage(content=news_prompt)])
        return self._format_analysis_response(response.content)

    def _explain_indicator(self, indicator: str) -> str:
        """Explain technical indicators with structured input."""
        indicator_prompt = f"""Explain {indicator} clearly and concisely:
1. Purpose
2. Key signals
3. Trading applications
4. Common pitfalls"""

        response = self.llm.invoke([HumanMessage(content=indicator_prompt)])
        return self._format_analysis_response(response.content)

    async def process_query(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Process Telegram queries."""
        text = context.args[0]
        loading_message = await update.message.reply_text(
            self.formatter.format_loading_message()
        )

        try:
            result = await asyncio.to_thread(self.agent_executor.invoke, {"input": text})
            await loading_message.edit_text(result['output'])
        except Exception as e:
            await loading_message.edit_text(
                self.formatter._t('query_error').format(error=str(e))
            )