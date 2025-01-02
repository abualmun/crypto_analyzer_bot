from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

from src.services.database import AdminTypes, UserType
from src.services.database_manager import DatabaseManager
from ..keyboards.reply_keyboards import AnalysisKeyboards
from .analysis_handlers import AnalysisHandler
from ...utils.formatters import TelegramFormatter

class CallbackHandler:
    def __init__(self):
        self.keyboards = AnalysisKeyboards()
        self.analysis_handler = AnalysisHandler()
        self.formatter = TelegramFormatter()  # Add formatter
        self.db_manager = DatabaseManager()
        self.user_states = {'language':'en'}  # Store user states

    async def handle_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle callback queries from inline keyboards"""
        query = update.callback_query
        user_id = update.effective_user.id
        data = query.data
        
        if 'language' not in context.user_data:
            context.user_data['language'] =  self.db_manager.get_user_by_telegram_id(user_id).language # Default to 'en'
        
        # Set formatter language based on context
        self.formatter.set_language(context.user_data['language'])
        
        try:
            # Handle main menu callbacks
            if data.startswith("menu_"):
                await self._handle_menu_selection(query, user_id)
            
            # Handle analysis callbacks
            elif data.startswith("analysis_"):
                await self._handle_analysis_selection(query, user_id)
            
            # Handle timeframe callbacks
            elif data.startswith("timeframe_"):
                await self._handle_timeframe_selection(query, user_id)
            
            # Handle chart callbacks
            elif data.startswith("chart_"):
                await self._handle_chart_selection(query, user_id)
            
            # Handle settings callbacks
            elif data.startswith("settings_"):
                await self._handle_settings_selection(query, user_id, context)
            
            # Handle back buttons
            elif data.startswith("back_"):
                await self._handle_back_button(query, user_id)
            
            elif data.startswith("admin_"):
                await self._handle_admin_selection(query, user_id)
            elif data.startswith("tracking_"):
                await self._handle_tracking_selection(query, user_id)
            elif data.startswith("users_"):
                await self._handle_users_action(query, user_id)
            elif data.startswith("back_"):
                await self._handle_back_button(query, user_id)
            elif data.startswith("adminsconf_"):
                await self._handle_admins_action(query, user_id)
            elif data.startswith('toggle_ban'):
                await self._handle_user_ban(query,context=context,user_id=user_id)
            elif data.startswith('change_user_subscrption'):
                await self._handle_change_user_subscrption(query,context=context,user_id=user_id)
            elif data.startswith('remove_admin'):
                await self._handle_admin_remove(query,context=context,user_id=user_id)
            elif data.startswith('add_admin'):
                await self._handle_admin_add(query,context=context,user_id=user_id)
            elif data.startswith('change_admin_'):
                await self._handle_change_admin_role(query,context=context,user_id=user_id)

                
        except Exception as e:
            await query.answer(f"{self.formatter._t('error')}: {str(e)}")

    async def _handle_menu_selection(self, query, user_id):
        """Handle main menu selections"""
        action = query.data.split("_")[1]
        
        if action == "analysis":
            await query.edit_message_text(
                self.formatter._t('select_analysis'),
                reply_markup=self.keyboards.get_analysis_menu()
            )
            
        elif action == "charts":
            await query.edit_message_text(
                self.formatter._t('select_chart_type'),
                reply_markup=self.keyboards.get_chart_types()
            )
            
        elif action == "help":
            help_text = (
                f"🤖 *{self.formatter._t('bot_help')}*\n\n"
                f"*{self.formatter._t('analysis_commands')}:*\n"
                f"/analyze [symbol] - {self.formatter._t('full_analysis')}\n"
                f"/quick [symbol] - {self.formatter._t('quick_analysis')}\n"
                f"/chart [symbol] [type] - {self.formatter._t('specific_chart')}\n\n"
                f"*{self.formatter._t('available_chart_types')}:*\n"
                f"• price - {self.formatter._t('price_chart')}\n"
                f"• ma - {self.formatter._t('moving_averages')}\n"
                f"• macd - {self.formatter._t('macd')}\n"
                f"• rsi - {self.formatter._t('rsi')}\n"
                f"• volume - {self.formatter._t('volume_chart')}"
            )
            await query.edit_message_text(
                help_text,
                parse_mode='Markdown',
                reply_markup=self.keyboards.get_main_menu()
            )
            
        elif action == "settings":
            await query.edit_message_text(
                self.formatter._t('select_settings'),
                reply_markup=self.keyboards.get_settings_menu()
            )

    async def _handle_analysis_selection(self, query, user_id):
        """Handle analysis type selections"""
        action = query.data.split("_")[1]
        
        if action == "quick":
            self.user_states[user_id] = {"action": "quick_analysis"}
            await query.edit_message_text(
                self.formatter._t('provide_symbol_prompt')
            )
        
        elif action == "news":
            self.user_states[user_id] = {"action": "news_analysis"}
            await query.edit_message_text(
                self.formatter._t('provide_symbol_prompt')
            )
            
        elif action == "full":
            self.user_states[user_id] = {"action": "full_analysis"}
            await query.edit_message_text(
                self.formatter._t('provide_symbol_prompt'),
                reply_markup=self.keyboards.get_timeframe_selection()
            )
            
        elif action == "custom":
            await query.edit_message_text(
                self.formatter._t('select_chart_type'),
                reply_markup=self.keyboards.get_chart_types()
            )

    async def _handle_timeframe_selection(self, query, user_id):
        """Handle timeframe selections"""
        timeframe = query.data.split("_")[1]
        state = self.user_states.get(user_id, {})
        state["timeframe"] = timeframe
        self.user_states[user_id] = state
        
        timeframe_display = self.formatter._t(f'time_{timeframe}')
        await query.edit_message_text(
            f"{self.formatter._t('timeframe_set')} {timeframe_display}\n"
            f"{self.formatter._t('provide_symbol_prompt')}"
        )

    async def _handle_chart_selection(self, query, user_id):
        """Handle chart type selections"""
        chart_type = query.data.split("_")[1]
        self.user_states[user_id] = {"action": "chart", "type": chart_type}
        
        chart_name = self.formatter._t(f'{chart_type}_chart')
        await query.edit_message_text(
            f"{self.formatter._t('selected_chart')} {chart_name}\n"
            f"{self.formatter._t('provide_symbol_prompt')}",
            reply_markup=self.keyboards.get_timeframe_selection()
        )

    async def _handle_settings_selection(self, query, user_id, context):
        """Handle settings selections"""
        setting = query.data.split("_")[1]
        
        if setting == "language":
            try:    
                if 'language' not in context.user_data:
                    context.user_data['language'] = 'en'

                new_lang = 'en' if context.user_data['language'] == 'ar' else 'ar'
                if self.db_manager.update_user_language(user_id=user_id,new_lang=new_lang):

                    context.user_data['language'] = new_lang

                    self.formatter.set_language(new_lang)
                    
                    await query.edit_message_text(
                        self.formatter._t('language_updated'),
                        reply_markup=self.keyboards.get_main_menu()
                    )
            except Exception as e:
                await query.edit_message_text(
                        self.formatter._t('error'),
                        reply_markup=self.keyboards.get_main_menu()
                    )
                print(e)
            
        elif setting == "timeframe":
            await query.edit_message_text(
                self.formatter._t('select_timeframe'),
                reply_markup=self.keyboards.get_timeframe_selection()
            )
        elif setting == "chart":
            await query.edit_message_text(
                self.formatter._t('select_chart_type'),
                reply_markup=self.keyboards.get_chart_types()
            )

    async def _handle_back_button(self, query, user_id):
        """Handle back button presses"""
        destination = query.data.split("_")[1]
        
        if destination == "main":
            await query.edit_message_text(
                self.formatter._t('main_menu'),
                reply_markup=self.keyboards.get_main_menu()
            )
        elif destination == "analysis":
            await query.edit_message_text(
                self.formatter._t('select_analysis'),
                reply_markup=self.keyboards.get_analysis_menu()
            )
        elif destination == "admin":
            # Back to admin main menu
            await query.edit_message_text(
                self.formatter._t('admin_menu'),
                reply_markup=self.keyboards.get_admin_menu()
            )
        elif destination == "tracking":
            # Back to user tracking menu
            await query.edit_message_text(
                self.formatter._t('select_tracking_option'),
                reply_markup=self.keyboards.get_user_tracking_menu()
            )
        elif destination == "users_managing":
            # Back to users managing menu
            await query.edit_message_text(
                self.formatter._t('select_user_management_option'),
                reply_markup=self.keyboards.get_users_managing_menu()
            )
        elif destination == "admins_managing":
            # Back to admins managing menu
            await query.edit_message_text(
                self.formatter._t('select_admin_management_option'),
                reply_markup=self.keyboards.get_admins_managing_menu()
            )

    async def _handle_admin_selection(self, query, user_id):
        """Handle admin menu selections"""
        action = query.data.split("_")[1]
        admin_role = self.db_manager.get_admin_by_user_id(user_id=user_id).role

        if action == "tracking":
            print("i gocha")
            await query.edit_message_text(
                self.formatter._t('select_tracking_option'),
                reply_markup=self.keyboards.get_user_tracking_menu()
            )
            
        elif action == "users":
            if admin_role == AdminTypes.WATCHER:

                await query.edit_message_text(
                    self.formatter._t('not_authorized'),
                    reply_markup=self.keyboards.get_admin_menu()
                )
            else:
                await query.edit_message_text(
                    self.formatter._t('select_user_management_option'),
                    reply_markup=self.keyboards.get_users_managing_menu()
                )
        elif action == "admins":
            if admin_role == AdminTypes.MASTER:
                await query.edit_message_text(
                    self.formatter._t('select_admin_management_option'),
                    reply_markup=self.keyboards.get_admins_managing_menu()
                )
                
            else:
                await query.edit_message_text(
                    self.formatter._t('not_authorized'),
                    reply_markup=self.keyboards.get_admin_menu()
                )

    async def _handle_tracking_selection(self, query, user_id):
        """Handle user tracking selections"""
        action = query.data.split("_")[1]
        
        if action == "searched":
            searched_data = await self._get_most_searched_data()
            await query.edit_message_text(
                f"{self.formatter._t('most_searched_stats')}\n{searched_data}",
                reply_markup=self.keyboards.get_user_tracking_menu()
            )
            
        elif action == "analysis":
            analysis_data = await self._get_popular_analysis_data()
            await query.edit_message_text(
                f"{self.formatter._t('popular_analysis_stats')}\n{analysis_data}",
                reply_markup=self.keyboards.get_user_tracking_menu()
            )

    async def _handle_users_action(self, query, user_id):
        """Handle various user management actions"""
        action = query.data.split("_")[1]
        
        if action == "subscribe":
            self.user_states[user_id] = {"action": "awaiting_subscription_change"}
            await query.edit_message_text(
                self.formatter._t('provide_user_id_for_subscription')
            )
            
        elif action == "ban":
            self.user_states[user_id] = {"action": "awaiting_user_ban"}
            await query.edit_message_text(
                self.formatter._t('provide_user_id_for_ban')
            )

    async def _handle_back_button(self, query, user_id):
        """Handle back button presses"""
        destination = query.data.split("_")[1]
        
        if destination == "main":
            await query.edit_message_text(
                self.formatter._t('main_menu'),
                reply_markup=self.keyboards.get_main_menu()
            )
        elif destination == "analysis":
            await query.edit_message_text(
                self.formatter._t('select_analysis'),
                reply_markup=self.keyboards.get_analysis_menu()
            )
        elif destination == "admin":
            await query.edit_message_text(
                self.formatter._t('admin_menu'),
                reply_markup=self.keyboards.get_admin_menu()
            )

    async def _get_most_searched_data(self):
        try:
            return self.db_manager.get_most_popular_searches(10)
        except Exception as e:
            return str(e)

    async def _get_popular_analysis_data(self):
        try:
            return self.db_manager.get_most_popular_analysis_types(10)
        except Exception as e:
            return await str(e)

    async def _get_users_list(self):
        """Retrieve list of users"""
        return "Users list placeholder"
    
    async def _handle_admins_action(self, query, user_id):
        """Handle admin management actions"""
        action = query.data.split("_")[1]
        
        try:
            if action == "new":
                # Set state to await new admin ID
                self.user_states[user_id] = {
                    "action": "awaiting_new_admin_id"
                }
                await query.edit_message_text(
                    self.formatter._t('provide_new_admin_id'),
                    reply_markup=InlineKeyboardMarkup([[
                        InlineKeyboardButton(
                            text=self.formatter._t('back_button'),
                            callback_data="back_admin"
                        )
                    ]])
                )
                
            elif action == "change":
                # Set state to await admin ID for role change
                self.user_states[user_id] = {
                    "action": "awaiting_role_change_id"
                }
                await query.edit_message_text(
                    self.formatter._t('provide_admin_id_for_role_change'),
                    reply_markup=InlineKeyboardMarkup([[
                        InlineKeyboardButton(
                            text=self.formatter._t('back_button'),
                            callback_data="back_admin"
                        )
                    ]])
                )
                
                
            elif action == "delete":
                # Set state to await admin ID for deletion
                self.user_states[user_id] = {
                    "action": "awaiting_delete_admin_id"
                }
                await query.edit_message_text(
                    self.formatter._t('provide_admin_id_for_removal'),
                    reply_markup=InlineKeyboardMarkup([[
                        InlineKeyboardButton(
                            text=self.formatter._t('back_button'),
                            callback_data="back_admin"
                        )
                    ]])
                )

        except Exception as e:
            await query.answer(
                f"{self.formatter._t('error')}: {str(e)}"
            )

    async def _handle_user_ban(self,query,context,user_id):
            success = self.db_manager.update_user_type(context.args[0],new_type=UserType.BANNED)
            if success:
                await query.edit_message_text(
                f"{self.formatter._t('user ')} {context.args[0]} {self.formatter._t('was banned')}",
                reply_markup=self.keyboards.get_admin_menu()
                )
            else:
                await query.edit_message_text(
                self.formatter._t('somthing went wrong'))

    async def _handle_change_user_subscrption(self,query,context,user_id):
        subscription = query.data.split("_")[-1]

        success = self.db_manager.update_user_type(context.args[0],new_type=subscription)
        if success:
                await query.edit_message_text(
                f"{self.formatter._t('user ')} {context.args[0]} {self.formatter._t('subscription was changed')}",
                reply_markup=self.keyboards.get_admin_menu()
                )
        else:
            await query.edit_message_text(
            self.formatter._t('somthing went wrong'))

    async def _handle_admin_remove(self,query,context,user_id):
            success = self.db_manager.remove_admin(admin_id=context.args[0],removed_by=user_id)
            if success:
                await query.edit_message_text(
                f"{self.formatter._t('admin ')} {context.args[0]} {self.formatter._t('was removed')}",
                reply_markup=self.keyboards.get_admin_menu()
                )
            else:
                await query.edit_message_text(
                self.formatter._t('somthing went wrong'))


    async def _handle_admin_add(self,query,context,user_id):
            success = self.db_manager.create_admin(context.args[0],user_id)
            if success:
                await query.edit_message_text(
                f"{self.formatter._t('admin ')} {context.args[0]} {self.formatter._t('was added')}",
                reply_markup=self.keyboards.get_admin_menu()
                )
            else:
                await query.edit_message_text(
                self.formatter._t('somthing went wrong'))

    async def _handle_change_admin_role(self,query,context,user_id):
        role = query.data.split("_")[-1]
        
        # check if the chager has authoroity to do this
        admin = self.db_manager.get_admin_by_user_id(self.user_states['user_id'])
        if admin['role'] != 'master':
            return await query.edit_message_text(
            "self.formatter._t('you do not have authorization to this proccess')")
        
        success = self.db_manager.update_admin_role(context.args[0],new_role=role,updated_by=user_id)
        if success:
                await query.edit_message_text(
                f"{self.formatter._t('user ')} {context.args[0]} {self.formatter._t('subscription was changed')}",
                reply_markup=self.keyboards.get_admin_menu()
                )
        else:
            await query.edit_message_text(
            self.formatter._t('somthing went wrong'))
                   