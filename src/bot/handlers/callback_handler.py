from telegram import Update
from telegram.ext import ContextTypes
from ..keyboards.reply_keyboards import AnalysisKeyboards
from .analysis_handlers import AnalysisHandler
from ...utils.formatters import TelegramFormatter

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