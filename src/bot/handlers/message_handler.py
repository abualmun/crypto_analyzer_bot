from telegram import Update
from telegram.ext import ContextTypes

from src.bot.keyboards.reply_keyboards import AnalysisKeyboards
from src.services.database_manager import DatabaseManager
from .analysis_handlers import AnalysisHandler
from ...llm.agent import CryptoAnalysisAgent
from ...utils.formatters import TelegramFormatter


class CustomMessageHandler:  # Renamed from MessageHandler to CustomMessageHandler
    def __init__(self):
        self.analysis_handler = AnalysisHandler()
        self.agent = CryptoAnalysisAgent()
        self.formatter = TelegramFormatter()
        self.db_manager = DatabaseManager()
        self.keyboards = AnalysisKeyboards()
        self.user_states = {}

    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle text messages"""
        user_id = update.effective_user.id
        text = update.message.text.lower()

        # Set language from context
        if 'language' in context.user_data:
            self.formatter.set_language(context.user_data['language'])
        
        # Get user's current state
        state = self.user_states.get(user_id, {})
        
        if not state:
            # No active state, ignore the message or provide guidance
            loading_message = await update.message.reply_text(
            self.formatter._t('loading'))

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
            elif action == 'awaiting_user_ban':
                
                target_id = int(text)
                context.args = [target_id]
                user = self.db_manager.get_user_by_telegram_id(target_id)
                if user:
                    await update.message.reply_text(
                        f"{self.formatter._t('proceed with banning user: ')} {target_id}",
                        reply_markup=self.keyboards.get_user_ban_menu()
                    )
                else:
                    await update.message.reply_text(
                        f"{self.formatter._t('can not find user with user id: ')} {target_id}",
                        reply_markup=self.keyboards.get_admin_menu()
                    )
            elif action == 'awaiting_subscription_change':
                target_id = int(text)
                context.args = [target_id,]
                user = self.db_manager.get_user_by_telegram_id(target_id)
                if user:
                    await update.message.reply_text(
                        f"{self.formatter._t('user current subscription is')} {user['type']}\n {self.formatter._t('do you want to change it?')}",
                        reply_markup=self.keyboards.get_change_user_subscrption_menu()
                    )
                else:
                    await update.message.reply_text(
                        f"{self.formatter._t('can not find user with user id: ')} {target_id}",
                        reply_markup=self.keyboards.get_admin_menu()
                    )
            elif action == 'awaiting_delete_admin_id':
                target_id = int(text)
                context.args = [target_id]
                user = self.db_manager.get_admin_by_user_id(target_id)
                if user:
                    await update.message.reply_text(
                        f"{self.formatter._t('proceed with removing admin: ')} {target_id}",
                        reply_markup=self.keyboards.get_admin_remove_menu()
                    )
                else:
                    await update.message.reply_text(
                        f"{self.formatter._t('can not find admin with user id: ')} {target_id}",
                        reply_markup=self.keyboards.get_admin_menu()
                    )
            elif action == 'awaiting_new_admin_id':
                target_id = int(text)
                context.args = [target_id]
                user = self.db_manager.get_admin_by_user_id(target_id)
                if user:
                    await update.message.reply_text(
                        f"{self.formatter._t('proceed with adding admin: ')} {target_id}",
                        reply_markup=self.keyboards.get_admin_add_menu()
                    )
                else:
                    await update.message.reply_text(
                        f"{self.formatter._t('can not find user with user id: ')} {target_id}",
                        reply_markup=self.keyboards.get_admin_menu()
                    )
            elif action == 'awaiting_role_change_id':
                target_id = int(text)
                context.args = [target_id,]
                user = self.db_manager.get_admin_by_user_id(target_id)
                if user:
                    await update.message.reply_text(
                        f"{self.formatter._t('admin current subscribtion is')} {user['type']}\n {self.formatter._t('do you want to change it?')}",
                        reply_markup=self.keyboards.get_change_admin_role_menu()
                    )
                else:
                    await update.message.reply_text(
                        f"{self.formatter._t('can not find admin with user id: ')} {target_id}",
                        reply_markup=self.keyboards.get_change_admin_role_menu()
                    )
            # Clear the state after processing
            self.user_states.pop(user_id, None)

        except Exception as e:
            await update.message.reply_text(
                  f"{self.formatter._t('error_processing')}: {str(e)}"
            )
            self.user_states.pop(user_id, None)