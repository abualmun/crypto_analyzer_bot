from telegram import Update
from telegram.ext import ContextTypes
from .analysis_handlers import AnalysisHandler
from ...llm.agent import CryptoAnalysisAgent
from ...utils.formatters import TelegramFormatter


class CustomMessageHandler:  # Renamed from MessageHandler to CustomMessageHandler
    def __init__(self):
        self.analysis_handler = AnalysisHandler()
        self.agent = CryptoAnalysisAgent()
        self.formatter = TelegramFormatter()
        self.user_states = {}

    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle text messages"""
        user_id = update.effective_user.id
        text = update.message.text.lower()

        # Get user's current state
        state = self.user_states.get(user_id, {})
        
        if not state:
            # No active state, ignore the message or provide guidance
            loading_message = await update.message.reply_text(
            self.formatter.format_loading_message())

            message = self.agent.process_query(text)
            print(message)
            await loading_message.edit_text(text=message['output'])
            return

        try:
            action = state.get('action')
            if action == 'quick_analysis':
                # Prepare context.args for quick analysis
                context.args = [text]
                await self.analysis_handler.cmd_quick(update, context)
            
            elif action == 'news_analysis':
                # Prepare context.args for quick analysis
                context.args = [text]
                await self.analysis_handler.cmd_news(update, context)
                
            elif action == 'full_analysis':
                # Create a context args list with symbol and timeframe
                context.args = [text]  # Symbol
                if 'timeframe' in state:
                    context.args.append(state['timeframe'])
                await self.analysis_handler.cmd_analyze(update, context)
                
            elif action == 'chart':
                # Create context args with symbol, chart type, and timeframe
                context.args = [
                    text,  # Symbol
                    state.get('type', 'price'),  # Chart type
                    state.get('timeframe', '1d')  # Timeframe
                ]
                await self.analysis_handler.cmd_chart(update, context)

            # Clear the state after processing
            self.user_states.pop(user_id, None)

        except Exception as e:
            await update.message.reply_text(f"Error processing request: {str(e)}")
            self.user_states.pop(user_id, None)