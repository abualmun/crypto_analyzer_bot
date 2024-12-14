# src/bot/handlers/analysis_handlers.py

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from src.data.crypto_data import CryptoDataClient
from src.data.market_data import MarketDataProcessor
from src.analysis.technical import TechnicalAnalyzer

class AnalysisHandlers:
    def __init__(self):
        self.crypto_client = CryptoDataClient()
        self.market_processor = MarketDataProcessor(self.crypto_client)
        self.analyzer = TechnicalAnalyzer()

    async def quick_analysis(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle quick analysis command"""
        try:
            # Get coin symbol from command
            message = update.message.text.lower()
            parts = message.split()
            
            if len(parts) < 2:
                await update.message.reply_text(
                    "Please provide a coin symbol. Example: /analyze btc"
                )
                return

            coin_symbol = parts[1]
            
            # Show processing message
            processing_message = await update.message.reply_text(
                "🔄 Processing analysis... Please wait."
            )

            # Search for coin
            coins = await self.crypto_client.search_coin(coin_symbol)
            if not coins:
                await processing_message.edit_text(
                    "❌ Coin not found. Please check the symbol and try again."
                )
                return

            coin_id = coins[0]['id']  # Use first match

            # Get market data
            ohlcv_data = await self.market_processor.get_ohlcv_data(coin_id, '30')
            if ohlcv_data is None:
                await processing_message.edit_text(
                    "❌ Error fetching market data. Please try again later."
                )
                return

            # Generate analysis
            analysis = await self.analyzer.generate_analysis_report(ohlcv_data)
            
            # Format report
            report = self._format_analysis_report(coin_symbol.upper(), analysis)
            
            # Create keyboard for detailed analysis
            keyboard = [[
                InlineKeyboardButton("📊 Detailed Analysis", callback_data=f"detailed_{coin_id}")
            ]]

            await processing_message.edit_text(
                report,
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode='HTML'
            )

        except Exception as e:
            await update.message.reply_text(
                f"❌ An error occurred: {str(e)}"
            )

    def _format_analysis_report(self, symbol: str, analysis: dict) -> str:
        """Format analysis results into readable message"""
        trend = analysis['trend']
        momentum = analysis['momentum']
        volatility = analysis['volatility']
        sr = analysis['support_resistance']

        report = f"""
<b>📊 Analysis Report for {symbol}</b>

<b>🎯 Overall Trend:</b> {trend['trend']}
• SMA20: {trend['price_vs_sma20']} from price
• SMA50: {trend['price_vs_sma50']} from price

<b>📈 Momentum:</b> {momentum['momentum']}
• RSI: {momentum['rsi']:.2f}
• MACD: {momentum['macd']:.2f}

<b>📊 Volatility:</b> {volatility['volatility']}
• ATR: {volatility['atr']:.2f}

<b>🔍 Key Levels:</b>
• Support: {sr['price_to_support']} below price
• Resistance: {sr['price_to_resistance']} above price

<i>Analysis timestamp: {analysis['timestamp']}</i>
"""
        return report

