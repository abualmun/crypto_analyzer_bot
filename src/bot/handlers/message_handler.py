from telegram import Update
from telegram.ext import ContextTypes

from src.bot.handlers.callback_handler import CallbackHandler
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
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle text messages"""
        user_id = str(update.effective_user.username)
        text = update.message.text.lower()

        # Set language from context
        if 'language' in context.user_data:
            self.formatter.set_language(context.user_data['language'])

        # Get user's current state
        state = context.user_data

        if not state:
            # No active state, ignore the message or provide guidance
            context.args = [text]
            await self.agent.process_query(update, context)

        try:
            action = state.get('action')
            if action == 'quick_analysis':
                context.args = [text]
                await self.analysis_handler.cmd_quick(update, context)

            elif action == 'news_analysis':
                context.args = [text]
                await self.analysis_handler.cmd_news(update, context)

            elif action == 'full_analysis':
                context.args = [text]
                if 'timeframe' in state:
                    context.args.append(state['timeframe'])
                await self.analysis_handler.cmd_analyze(update, context)

            elif action == 'chart':
                context.args = [
                    text,
                    state.get('type', 'price'),
                    state.get('timeframe', '1d'),
                ]
                await self.analysis_handler.cmd_chart(update, context)

            elif action == 'awaiting_user_ban':
                target_id = int(text)
                context.user_data["target_id"] = target_id
                user = self.db_manager.get_user_by_telegram_id(target_id)
                if user:
                    await update.message.reply_text(
                        f"{self.formatter._t('proceed_with_banning_user')} {target_id}",
                        reply_markup=self.keyboards.get_user_ban_menu()
                    )
                else:
                    await update.message.reply_text(
                        f"{self.formatter._t('error_user_not_found')} {target_id}",
                        reply_markup=self.keyboards.get_admin_menu()
                    )

            elif action == 'awaiting_subscription_change':
                target_id = text
                context.user_data["target_id"] = target_id
                user = self.db_manager.get_user_by_telegram_id(target_id)
                if user:
                    await update.message.reply_text(
                        f"{self.formatter._t('user_current_subscription')} {user['user_type']}\n"
                        f"{self.formatter._t('do_you_want_to_change_it')}",
                        reply_markup=self.keyboards.get_change_user_subscrption_menu()
                    )
                else:
                    await update.message.reply_text(
                        f"{self.formatter._t('error_user_not_found')} {target_id}",
                        reply_markup=self.keyboards.get_admin_menu()
                    )

            elif action == 'awaiting_delete_admin_id':
                target_id = text
                context.user_data["target_id"] = target_id

                user = self.db_manager.get_admin_by_user_id(target_id)
                if user:
                    await update.message.reply_text(
                        f"{self.formatter._t('proceed_with_removing_admin')} {target_id}",
                        reply_markup=self.keyboards.get_admin_remove_menu()
                    )
                else:
                    await update.message.reply_text(
                        f"{self.formatter._t('error_invalid_id')} {target_id}",
                        reply_markup=self.keyboards.get_admin_menu()
                    )

            elif action == 'awaiting_new_admin_id':
                target_id = text
                context.user_data["target_id"] = target_id
                user = self.db_manager.get_user_by_telegram_id(target_id)
                if user:
                    await update.message.reply_text(
                        f"{self.formatter._t('proceed_with_adding_admin')} {target_id}",
                        reply_markup=self.keyboards.get_admin_add_menu()
                    )
                else:
                    await update.message.reply_text(
                        f"{self.formatter._t('error_invalid_id')} {target_id}",
                        reply_markup=self.keyboards.get_admin_menu()
                    )

            elif action == 'awaiting_role_change_id':
                target_id = text
                check_admin = self.db_manager.get_admin_by_user_id(target_id)
                if check_admin:
                    
                    context.user_data["target_id"] = target_id
                    user = self.db_manager.get_admin_by_user_id(target_id)
                    if user:
                        await update.message.reply_text(
                            f"{self.formatter._t('admin_current_role_is')} {check_admin['role']}\n"
                            f"{self.formatter._t('do_you_want_to_change_it')}",
                            reply_markup=self.keyboards.get_change_admin_role_menu()
                        )
                    else:
                        await update.message.reply_text(
                            f"{self.formatter._t('error_invalid_id')} {target_id}",
                            reply_markup=self.keyboards.get_admin_menu()
                        )
                else:
                    await update.message.reply_text(
                        self.formatter._t('error_user_not_found'))


            # Clear the state after processing
            self.user_states.pop(user_id, None)

        except Exception as e:
            await update.message.reply_text(
                f"{self.formatter._t('error_processing')}: {str(e)}"
            )
            self.user_states.pop(user_id, None)
