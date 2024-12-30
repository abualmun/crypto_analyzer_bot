# src/bot/handlers/callback_handler.py
from telegram import Update
from telegram.ext import ContextTypes
from ..keyboards.reply_keyboards import AnalysisKeyboards
from .analysis_handlers import AnalysisHandler
from ...utils.formatters import TelegramFormatter
from ...education.content import educational_content, get_module_by_key

class CallbackHandler:
    def __init__(self):
        self.keyboards = AnalysisKeyboards()
        self.analysis_handler = AnalysisHandler()
        self.formatter = TelegramFormatter()  # Add formatter
        self.user_states = {'language':'en'}  # Store user states

    async def handle_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle callback queries from inline keyboards"""
        query = update.callback_query
        user_id = update.effective_user.id
        data = query.data
        
        if 'language' not in context.user_data:
            context.user_data['language'] = 'en'  # Default to 'en'
        
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
                
            elif data.startswith("help_"):
                await self._handle_help_selection(query, user_id)
                
            elif data.startswith("education_"):
                await self._handle_education_selection(query, user_id)

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
                context.user_data['language'] = new_lang
                self.formatter.set_language(new_lang)
                
                await query.edit_message_text(
                    self.formatter._t('language_updated'),
                    reply_markup=self.keyboards.get_main_menu()
                )
            except Exception as e:
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
        elif destination == "help":
            await query.edit_message_text(
                self.formatter._t('help_menu'),
                reply_markup=self.keyboards.get_help_menu()
            )
            
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
        """Handle education menu selections"""
        section = query.data.split("_")[1]
         
        if section == "back":
            await query.edit_message_text(
               self.formatter._t('education_menu'),
                reply_markup=self.keyboards.get_education_menu()
            )
        else:
            module = get_module_by_key(section)
            if module:
                text = f"*{module.get('title','')}*\n\n{module.get('text','')}\n\n"
                links = module.get('links',[])
                for link in links:
                    text += f"[{link[0]}]({link[1]})\n"
                
                await query.edit_message_text(
                   text,
                   reply_markup=self.keyboards.get_education_sub_menu(),
                    parse_mode="Markdown",
                    disable_web_page_preview=True
                )
            
    
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