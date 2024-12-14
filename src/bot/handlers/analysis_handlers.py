from telegram import Update
from telegram.ext import ContextTypes
from ...analysis.technical import TechnicalAnalyzer
from ...utils.formatters import TelegramFormatter
from ...data.processor import DataProcessor

class AnalysisHandler:
    def __init__(self):
        self.analyzer = TechnicalAnalyzer()
        self.formatter = TelegramFormatter()
        self.data_processor = DataProcessor()

    async def cmd_analyze(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handler for /analyze command"""
        if not context.args:
            await update.message.reply_text(
                "Please provide a cryptocurrency symbol.\n"
                "Example: /analyze btc"
            )
            return

        coin_id = context.args[0].lower()
        
        # Show loading message
        loading_message = await update.message.reply_text(
            self.formatter.format_loading_message()
        )

        # Validate coin
        if not self.data_processor.validate_coin_id(coin_id):
            await loading_message.edit_text(
                f"❌ Invalid cryptocurrency symbol: {coin_id}\n"
                "Please try again with a valid symbol."
            )
            return

        try:
            # Get full analysis
            analysis = self.analyzer.analyze_coin(coin_id)
            formatted_message = self.formatter.format_full_analysis(analysis, coin_id)
            
            # Update loading message with analysis
            await loading_message.edit_text(formatted_message)

        except Exception as e:
            await loading_message.edit_text(
                self.formatter.format_error_message(str(e))
            )

    async def cmd_quick(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handler for /quick command"""
        if not context.args:
            await update.message.reply_text(
                "Please provide a cryptocurrency symbol.\n"
                "Example: /quick btc"
            )
            return

        coin_id = context.args[0].lower()
        
        # Show loading message
        loading_message = await update.message.reply_text(
            self.formatter.format_loading_message()
        )

        try:
            # Get quick analysis
            analysis = self.analyzer.get_quick_analysis(coin_id)
            formatted_message = self.formatter.format_quick_analysis(analysis, coin_id)
            
            # Update loading message with analysis
            await loading_message.edit_text(formatted_message)

        except Exception as e:
            await loading_message.edit_text(
                self.formatter.format_error_message(str(e))
            )

    async def handle_text_analysis(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handler for natural language analysis requests"""
        text = update.message.text.lower()
        
        # Extract coin from text (simple implementation)
        common_coins = {
            "bitcoin": "bitcoin",
            "btc": "bitcoin",
            "ethereum": "ethereum",
            "eth": "ethereum",
            # Add more common coins
        }
        
        found_coin = None
        for key, value in common_coins.items():
            if key in text:
                found_coin = value
                break
                
        if not found_coin:
            await update.message.reply_text(
                "I couldn't identify which cryptocurrency you want to analyze.\n"
                "Try using /analyze btc or /quick eth instead."
            )
            return
            
        # Show loading message
        loading_message = await update.message.reply_text(
            self.formatter.format_loading_message()
        )

        try:
            if "quick" in text or "fast" in text:
                analysis = self.analyzer.get_quick_analysis(found_coin)
                formatted_message = self.formatter.format_quick_analysis(analysis, found_coin)
            else:
                analysis = self.analyzer.analyze_coin(found_coin)
                formatted_message = self.formatter.format_full_analysis(analysis, found_coin)
            
            await loading_message.edit_text(formatted_message)

        except Exception as e:
            await loading_message.edit_text(
                self.formatter.format_error_message(str(e))
            )