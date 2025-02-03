# src/bot/handlers/callback_handler.py
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
        self.user_states = {}
    async def handle_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle callback queries from inline keyboards"""
        query = update.callback_query
        user_id = str(update.effective_user.username)
        data = query.data
        
        if 'language' not in context.user_data:
            context.user_data['language'] =  self.db_manager.get_user_by_telegram_id(user_id)['language'] # Default to 'en'
        
        # Set formatter language based on context
        self.formatter.set_language(context.user_data['language'])
        
        try:
            # Handle main menu callbacks
            if data.startswith("menu_"):
                await self._handle_menu_selection(query, user_id,context)
            
            # Handle analysis callbacks
            elif data.startswith("analysis_"):
                await self._handle_analysis_selection(query, context,user_id)

            # Handle timeframe callbacks
            elif data.startswith("timeframe_"):
                await self._handle_timeframe_selection(query, user_id)
            
            # Handle chart callbacks
            elif data.startswith("chart_"):
                await self._handle_chart_selection(query,context, user_id)
            
            # Handle settings callbacks
            elif data.startswith("settings_"):
                await self._handle_settings_selection(query, user_id,context)
            
            # Handle back buttons
            elif data.startswith("back_"):
                await self._handle_back_button(query, user_id)
            
            elif data.startswith("admin_"):
                await self._handle_admin_selection(query, user_id)
            elif data.startswith("tracking_"):
                await self._handle_tracking_selection(query, user_id)
            elif data.startswith("users_"):
                await self._handle_users_action(query, context,user_id)
            elif data.startswith("back_"):
                await self._handle_back_button(query, user_id)
            elif data.startswith("adminsconf_"):
                await self._handle_admins_action(query, context,user_id)
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

                                
            elif data.startswith("help_"):
                await self._handle_help_selection(query, user_id)
                
            elif data.startswith("education_"):
                await self._handle_education_selection(query, user_id)


        except Exception as e:
            await query.answer(f"{self.formatter._t('error')}: {str(e)}")

    # Existing methods: _handle_menu_selection, _handle_analysis_selection,
    # _handle_timeframe_selection, _handle_chart_selection, _handle_settings_selection
    # _handle_back_button, _handle_help_selection.
    async def _handle_menu_selection(self, query, user_id,context):
        user = self.db_manager.get_user_by_telegram_id(user_id)
        if user["user_type"] == UserType.BANNED:
            return await query.edit_message_text(
            self.formatter._t('error_no_permission'))
        

      # Existing method, no changes
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
            await query.edit_message_text(
                self.formatter._t('help_menu'),
                reply_markup=self.keyboards.get_help_menu()
            )
            
        elif action == "settings":
            await query.edit_message_text(
                self.formatter._t('select_settings'),
                reply_markup=self.keyboards.get_settings_menu()
            )
        elif action == "education":
             await query.edit_message_text(
                self.formatter._t('education_menu'),
                reply_markup=self.keyboards.get_education_menu()
            )
             
        elif action == "ai":
            context.user_data["action"] = "ai_analysis"
            await query.edit_message_text(
                self.formatter._t('ai_menu')
            )

    async def _handle_analysis_selection(self, query,context, user_id):
        user = self.db_manager.get_user_by_telegram_id(user_id)
        if user["user_type"] == UserType.BANNED:
            return await query.edit_message_text(
            self.formatter._t('error_no_permission'))
        
        """Handle analysis type selections"""
        action = query.data.split("_")[1]
        
        if action == "quick":
            context.user_data["action"] = "quick_analysis"
            await query.edit_message_text(
                self.formatter._t('provide_symbol_prompt')
            )
        
        elif action == "news":
            context.user_data["action"] = "news_analysis"
            await query.edit_message_text(
                self.formatter._t('provide_symbol_prompt')
            )
            
        elif action == "full":
            context.user_data["action"] =  "full_analysis"
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
        
      # Existing method, no changes
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

    async def _handle_chart_selection(self, query,context, user_id):
      # Existing method, no changes
        """Handle chart type selections"""
        chart_type = query.data.split("_")[1]
        context.user_data["action"] = "chart"
        context.user_data["type"] = chart_type
        
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
        elif destination == "help":
            await query.edit_message_text(
                self.formatter._t('help_menu'),
                reply_markup=self.keyboards.get_help_menu()
            )

    async def _handle_admin_selection(self, query, user_id):
        
        admin = self.db_manager.get_admin_by_user_id(user_id)
        if not admin:
            return await query.edit_message_text(
                    self.formatter._t('error_no_permission'))
        """Handle admin menu selections"""
        action = query.data.split("_")[1]
        try:
            admin_role = self.db_manager.get_admin_by_user_id(user_id=user_id)['role']
        except Exception as e:
            return await query.edit_message_text(
                self.formatter._t('error'),
                reply_markup=self.keyboards.get_admin_menu()
            )
        if action == "tracking":
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
                    f"{self.formatter._t('not_authorized')}.",
                    reply_markup=self.keyboards.get_admin_menu()
                )

    async def _handle_tracking_selection(self, query, user_id):
        admin = self.db_manager.get_admin_by_user_id(user_id)
        if not admin:
            return await query.edit_message_text(
                    self.formatter._t('error_no_permission'))
        """Handle user tracking selections"""
        action = query.data.split("_")[1]
        try:
            if action == "searched":
                searched_data = await self._get_most_searched_data()
                await query.edit_message_text(
                    f"{self.formatter._t('most_searched_stats')}\n{self.formatter.format_popular_results([{'coin': r['coin'], 'count': r['count']} for r in searched_data], headers=('coin', 'count'))}",
                    reply_markup=self.keyboards.get_user_tracking_menu()
                )
            elif action == "analysis":
                analysis_data = await self._get_popular_analysis_data()
                await query.edit_message_text(
                    f"{self.formatter._t('popular_analysis_stats')}\n{self.formatter.format_popular_results(analysis_data, ('analysis_type', 'count'))}",
                    reply_markup=self.keyboards.get_user_tracking_menu()
                )
        except Exception as e:
            await query.edit_message_text(self.formatter._t('error'))

    async def _handle_users_action(self, query,context, user_id):
        admin = self.db_manager.get_admin_by_user_id(user_id)
        if not admin:
            return await query.edit_message_text(
                    self.formatter._t('error_no_permission'))
        """Handle various user management actions"""
        action = query.data.split("_")[1]
        try:
            if action == "subscribe":
                context.user_data["action"] = "awaiting_subscription_change"
                await query.edit_message_text(
                    self.formatter._t('provide_user_id_for_subscription')
                )
            elif action == "ban":
                context.user_data["action"] = "awaiting_user_ban"
                await query.edit_message_text(
                    self.formatter._t('provide_user_id_for_ban')
                )
        except Exception as e:
            await query.edit_message_text(self.formatter._t('error'))


    async def _get_most_searched_data(self):
        try:
            return self.db_manager.get_most_popular_coins(10)
            
        except Exception as e:
            return str(e)

    async def _get_popular_analysis_data(self):
        try:

            return self.db_manager.get_most_popular_analysis_types(10)
        except Exception as e:
            return await str(e)

 
    async def _handle_admins_action(self, query,context, user_id):
        admin = self.db_manager.get_admin_by_user_id(user_id)
        if not admin:
            return await query.edit_message_text(
                    self.formatter._t('error_no_permission'))
        """Handle admin management actions"""
        action = query.data.split("_")[1]
        
        try:
            if action == "new":
                # Set state to await new admin ID
                context.user_data["action"] =  "awaiting_new_admin_id"
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
                context.user_data["action"] ="awaiting_role_change_id"
                
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
                context.user_data["action"] ="awaiting_delete_admin_id"
                
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
            
            admin = self.db_manager.get_admin_by_user_id(user_id)
            if not admin or admin['role'] == AdminTypes.WATCHER:
                return await query.edit_message_text(
                        self.formatter._t('error_no_permission'))
            target_id = str(context.user_data["target_id"])

            user = self.db_manager.get_user_by_telegram_id(str(target_id))
            if user:
                success = self.db_manager.update_user_type(target_id,new_type=UserType.BANNED,admin_id=user_id)
                if success:
                    await query.edit_message_text(
                    f"{self.formatter._t('success_user_banned')}",
                    reply_markup=self.keyboards.get_admin_menu()
                    )
                else:
                    await query.edit_message_text(
                    self.formatter._t('error'))
            else:

                    await query.edit_message_text(
                    self.formatter._t('error_user_not_found'))
    async def _handle_change_user_subscrption(self,query,context,user_id):
        admin = self.db_manager.get_admin_by_user_id(user_id)
        if not admin or admin['role'] == AdminTypes.WATCHER:
            return await query.edit_message_text(
                    self.formatter._t('error_no_permission'))
        subscription = query.data.split("_")[-1]
        if subscription == 'premium':
            subscription = UserType.PREMIUM
        if subscription == 'guest':
            subscription = UserType.GUEST
        target_id = str(context.user_data["target_id"])
        user = self.db_manager.get_user_by_telegram_id(target_id)
        if user:
            success = self.db_manager.update_user_type(target_id,new_type=subscription,admin_id=user_id)
            if success:
                    await query.edit_message_text(
                    f"{self.formatter._t('subscription_was_changed')}",
                    reply_markup=self.keyboards.get_admin_menu()
                    )
            else:
                await query.edit_message_text(
                self.formatter._t('error'))
        else:
            await query.edit_message_text(
                    self.formatter._t('error_user_not_found'))

    async def _handle_admin_remove(self,query,context,user_id):
            admin = self.db_manager.get_admin_by_user_id(user_id)
            if not admin or admin['role'] != AdminTypes.MASTER:
                return await query.edit_message_text(
                        self.formatter._t('error_no_permission'))
            
            target_id = str(context.user_data["target_id"])
            check_admin = self.db_manager.get_admin_by_user_id(target_id)
            if check_admin:
                success = self.db_manager.remove_admin(admin_id=target_id,removed_by=user_id)
                if success:
                    await query.edit_message_text(
                    f"{self.formatter._t('success_admin_removed')}",
                    reply_markup=self.keyboards.get_admin_menu()
                    )
                else:
                    await query.edit_message_text(
                    self.formatter._t('error'))
            else:
                    await query.edit_message_text(
                        self.formatter._t('error_user_not_found'))

    async def _handle_admin_add(self,query,context,user_id):
            admin = self.db_manager.get_admin_by_user_id(user_id)
            if not admin or admin['role'] != AdminTypes.MASTER:
                return await query.edit_message_text(
                        self.formatter._t('error_no_permission'))
            

            target_id = str(context.user_data["target_id"])
            check_admin = self.db_manager.get_admin_by_user_id(target_id)
            if not check_admin:
                success = self.db_manager.create_admin({'user_id' : target_id,"role":AdminTypes.NORMAL,"created_by":user_id})
                if success:
                    await query.edit_message_text(
                    f"{self.formatter._t('success_admin_added')}",
                    reply_markup=self.keyboards.get_admin_menu()
                    )
                else:
                    await query.edit_message_text(
                    self.formatter._t('error'))
            else:
                    await query.edit_message_text(
                        self.formatter._t('error_admin_exist'))
    async def _handle_change_admin_role(self,query,context,user_id):
        role = query.data.split("_")[-1]
        if role == 'master':
            role = AdminTypes.MASTER
        if role == 'normal':
            role = AdminTypes.NORMAL
        if role == "watcher":
            role = AdminTypes.WATCHER
        # check if the chager has authoroity to do this
        admin = self.db_manager.get_admin_by_user_id(user_id)
        if admin['role'] != AdminTypes.MASTER:
            return await query.edit_message_text(
            f"{self.formatter._t('not_authorized')}")
        
        target_id = str(context.user_data["target_id"])
        check_admin = self.db_manager.get_admin_by_user_id(target_id)
        if check_admin:
            success = self.db_manager.update_admin_role(target_id,new_role=role,updated_by=user_id)
            if success:
                    await query.edit_message_text(
                    f"{self.formatter._t('role_has_changed')}",
                    reply_markup=self.keyboards.get_admin_menu()
                    )
            else:
                await query.edit_message_text(
                self.formatter._t('error'))
        else:
            await query.edit_message_text(
                self.formatter._t('error_user_not_found'))          
        
            
    async def _handle_help_selection(self, query, user_id):
         """Handle help menu selections"""
         section = query.data.split("_")[1]
         
         if section == "intro":
             await query.edit_message_text(
                 self._get_help_intro_text(),
                 reply_markup=self.keyboards.get_help_sub_menu()
             )
         elif section == "commands":
             await query.edit_message_text(
                 self._get_help_commands_text(),
                 reply_markup=self.keyboards.get_help_sub_menu()
             )
         elif section == "navigation":
             await query.edit_message_text(
                 self._get_help_navigation_text(),
                 reply_markup=self.keyboards.get_help_sub_menu()
             )
         elif section == "analysis":
             await query.edit_message_text(
                 self._get_help_analysis_text(),
                 reply_markup=self.keyboards.get_help_sub_menu()
             )
         elif section == "charts":
             await query.edit_message_text(
                 self._get_help_charts_text(),
                reply_markup=self.keyboards.get_help_sub_menu()
             )
         elif section == "news":
            await query.edit_message_text(
                self._get_help_news_text(),
                reply_markup=self.keyboards.get_help_sub_menu()
             )
         elif section == "agent":
             await query.edit_message_text(
                 self._get_help_agent_text(),
                 reply_markup=self.keyboards.get_help_sub_menu()
             )
         elif section == "troubleshooting":
            await query.edit_message_text(
                 self._get_help_troubleshooting_text(),
                reply_markup=self.keyboards.get_help_sub_menu()
             )
         elif section == "settings":
             await query.edit_message_text(
                 self._get_help_settings_text(),
                 reply_markup=self.keyboards.get_help_sub_menu()
             )
         elif section == "feedback":
            await query.edit_message_text(
                 self._get_help_feedback_text(),
                reply_markup=self.keyboards.get_help_sub_menu()
             )
    
    async def _handle_education_selection(self, query, user_id):
        """Handle education-related selections"""
        data = query.data
        sections = data.split("_")[1:]  # Remove 'education' prefix
        
        try:
            # Handle back to education menu
            if sections[0] == "back":
                await query.edit_message_text(
                    self.formatter._t('education_menu'),
                    reply_markup=self.keyboards.get_education_menu()
                )
                return

            # Handle main category selection (e.g., basic_concepts, technical_analysis)
            if len(sections) == 1:
                category = sections[0]
                message_text = ""
                
                # Get all topics for this category
                topic_keys = []
                for key in self.formatter.languages[self.formatter.current_language].keys():
                    if key.startswith(f"education_topic_{category}") and key.endswith("_title"):
                        base_key = key.rsplit('_title', 1)[0]
                        topic_keys.append(base_key)

                message_text = self.formatter._t(f'education_{category}')
                
                await query.edit_message_text(
                    message_text,
                    reply_markup=self.keyboards.get_education_sub_menu(category),
                    parse_mode="Markdown"
                )
                return

            # Handle specific topic selection
            category = sections[0]
            topic = "_".join(sections[1:])  # Handle multi-part topic names
            
            # Build full message with title, content, and links
            message_text = ""
            
            # Get title
            title_key = f"education_topic_{category}_{topic}_title"
            title = self.formatter._t(title_key)
            if title:
                message_text += f"*{title}*\n\n"
            
            # Get main content
            text_key = f"education_topic_{category}_{topic}_text"
            text = self.formatter._t(text_key)
            if text:
                message_text += f"{text}\n\n"
            
            # Add any associated links
            link_counter = 1
            while True:
                link_text_key = f"education_topic_{category}_{topic}_link_{link_counter}_text"
                link_url_key = f"education_topic_{category}_{topic}_link_{link_counter}_url"
                
                link_text = self.formatter._t(link_text_key)
                link_url = self.formatter._t(link_url_key)
                
                if not (link_text and link_url):
                    break
                    
                message_text += f"[{link_text}]({link_url})\n"
                link_counter += 1
            
            # Show the content with a back button
            await query.edit_message_text(
                message_text,
                reply_markup=self.keyboards.get_education_sub_menu(category),
                parse_mode="Markdown",
                disable_web_page_preview=True
            )

        except Exception as e:
            print(f"Error in education handler: {str(e)}")
            await query.edit_message_text(
                f"{self.formatter._t('error')}: {str(e)}",
                reply_markup=self.keyboards.get_education_menu()
            )
        finally:
            await query.answer()
    # Existing helper methods: _get_help_intro_text, _get_help_commands_text
    # _get_help_navigation_text, _get_help_analysis_text, _get_help_charts_text
    # _get_help_news_text ,_get_help_agent_text , _get_help_troubleshooting_text,
    # _get_help_settings_text,  _get_help_feedback_text
    def _get_help_intro_text(self):
        """Returns the help intro text."""
        return self.formatter._t("help_intro_text")
    
    def _get_help_commands_text(self):
        """Returns the help commands text."""
        return self.formatter._t("help_commands_text")
    
    def _get_help_navigation_text(self):
        """Returns the help navigation text."""
        return self.formatter._t("help_navigation_text")

    def _get_help_analysis_text(self):
         """Returns the help analysis text."""
         return self.formatter._t("help_analysis_text")
    
    def _get_help_charts_text(self):
        """Returns the help charts text."""
        return self.formatter._t("help_charts_text")
    
    def _get_help_news_text(self):
         """Returns the help news text."""
         return self.formatter._t("help_news_text")
    
    def _get_help_agent_text(self):
        """Returns the help ai agent text."""
        return self.formatter._t("help_agent_text")
    
    def _get_help_troubleshooting_text(self):
        """Returns the help troubleshooting text."""
        return self.formatter._t("help_troubleshooting_text")

    def _get_help_settings_text(self):
        """Returns the help settings text."""
        return self.formatter._t("help_settings_text")
    
    def _get_help_feedback_text(self):
        """Returns the help feedback text."""
        return self.formatter._t("help_feedback_text")