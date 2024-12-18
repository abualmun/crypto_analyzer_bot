from telegram import Update
from telegram.ext import ContextTypes
from ..keyboards.reply_keyboards import AnalysisKeyboards
from .analysis_handlers import AnalysisHandler

class CallbackHandler:
    def __init__(self):
        self.keyboards = AnalysisKeyboards()
        self.analysis_handler = AnalysisHandler()
        self.user_states = {'language':'en'}  # Store user states

    async def handle_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle callback queries from inline keyboards"""
        query = update.callback_query
        user_id = update.effective_user.id
        data = query.data
        
        if 'language' not in context.user_data:
                    context.user_data['language'] = 'en'  # Default to 'en'
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
                await self._handle_settings_selection(query, user_id,context)
            
            # Handle back buttons
            elif data.startswith("back_"):
                await self._handle_back_button(query, user_id)

        except Exception as e:
            await query.answer(f"Error: {str(e)}")

    async def _handle_menu_selection(self, query, user_id):
        """Handle main menu selections"""
        action = query.data.split("_")[1]
        
        if action == "analysis":
            await query.edit_message_text(
                "Select analysis type:",
                reply_markup=self.keyboards.get_analysis_menu()
            )
            
        elif action == "charts":
            await query.edit_message_text(
                "Select chart type:",
                reply_markup=self.keyboards.get_chart_types()
            )
            
        elif action == "help":
            help_text = (
                "🤖 *CryptoAnalyst Bot Help*\n\n"
                "*Analysis Commands:*\n"
                "/analyze [symbol] - Full analysis\n"
                "/quick [symbol] - Quick analysis\n"
                "/chart [symbol] [type] - Specific chart\n\n"
                "*Available Chart Types:*\n"
                "• price - OHLC chart\n"
                "• ma - Moving averages\n"
                "• macd - MACD indicator\n"
                "• rsi - RSI indicator\n"
                "• volume - Volume analysis"
            )
            await query.edit_message_text(
                help_text,
                parse_mode='Markdown',
                reply_markup=self.keyboards.get_main_menu()
            )
            
        elif action == "settings":
            await query.edit_message_text(
                "Select setting to modify:",
                reply_markup=self.keyboards.get_settings_menu()
            )

    async def _handle_analysis_selection(self, query, user_id):
        """Handle analysis type selections"""
        action = query.data.split("_")[1]
        
        if action == "quick":
            self.user_states[user_id] = {"action": "quick_analysis"}
            await query.edit_message_text(
                "Please enter the cryptocurrency symbol (e.g., btc):"
            )
        
        elif action == "news":
            self.user_states[user_id] = {"action": "news_analysis"}
            await query.edit_message_text(
                "Please enter the cryptocurrency symbol (e.g., btc):"
            )
            
        elif action == "full":
            self.user_states[user_id] = {"action": "full_analysis"}
            await query.edit_message_text(
                "Please enter the cryptocurrency symbol (e.g., btc):",
                reply_markup=self.keyboards.get_timeframe_selection()
            )
            
        elif action == "custom":
            await query.edit_message_text(
                "Select chart type:",
                reply_markup=self.keyboards.get_chart_types()
            )

    async def _handle_timeframe_selection(self, query, user_id):
        """Handle timeframe selections"""
        timeframe = query.data.split("_")[1]
        state = self.user_states.get(user_id, {})
        state["timeframe"] = timeframe
        self.user_states[user_id] = state
        
        await query.edit_message_text(
            f"Timeframe set to {timeframe.upper()}\n"
            "Please enter the cryptocurrency symbol (e.g., btc):"
        )

    async def _handle_chart_selection(self, query, user_id):
        """Handle chart type selections"""
        chart_type = query.data.split("_")[1]
        self.user_states[user_id] = {"action": "chart", "type": chart_type}
        
        await query.edit_message_text(
            f"Selected {chart_type} chart\n"
            "Please enter the cryptocurrency symbol (e.g., btc):",
            reply_markup=self.keyboards.get_timeframe_selection()
        )

    async def _handle_settings_selection(self, query, user_id,context):
        """Handle settings selections"""
        setting = query.data.split("_")[1]
        
        if setting == "language":
            try:    
                if 'language' not in context.user_data:
                    context.user_data['language'] = 'en'  # Default to 'en'
                if context.user_data['language'] == 'ar':
                    print("h1")
                    context.user_data['language'] = 'en'
                    
                    await query.edit_message_text(
                    context.user_data['language'])
                else:
                    print("h2")
                    context.user_data['language'] = 'ar'
                    await query.edit_message_text(
                    context.user_data['language'])
            except Exception as e :
                print(e)
            
        elif setting == "timeframe":
            await query.edit_message_text(
                "Select default timeframe:",
                reply_markup=self.keyboards.get_timeframe_selection()
            )
        elif setting == "chart":
            await query.edit_message_text(
                "Select default chart type:",
                reply_markup=self.keyboards.get_chart_types()
            )

    async def _handle_back_button(self, query, user_id):
        """Handle back button presses"""
        destination = query.data.split("_")[1]
        
        if destination == "main":
            await query.edit_message_text(
                "Main Menu:",
                reply_markup=self.keyboards.get_main_menu()
            )
        elif destination == "analysis":
            await query.edit_message_text(
                "Select analysis type:",
                reply_markup=self.keyboards.get_analysis_menu()
            )