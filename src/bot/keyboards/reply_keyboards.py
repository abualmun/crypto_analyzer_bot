# src/bot/keyboards/reply_keyboards.py
from ...utils.formatters import TelegramFormatter
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

class AnalysisKeyboards:
    def __init__(self):
        self.formatter = TelegramFormatter()

    def get_main_menu(self):
        """Create main menu keyboard"""
        keyboard = [
            [
                InlineKeyboardButton(text=self.formatter._t('analysis_button'), callback_data="menu_analysis"),
                InlineKeyboardButton(text=self.formatter._t('charts_button'), callback_data="menu_charts")
            ],
            [
                InlineKeyboardButton(text=self.formatter._t('help_button'), callback_data="menu_help"),
                InlineKeyboardButton(text=self.formatter._t('settings_button'), callback_data="menu_settings")
            ]
            ,
            [
                InlineKeyboardButton(text=self.formatter._t('education_button'), callback_data="menu_education")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    def get_analysis_menu(self):
        """Create analysis selection keyboard"""
        keyboard = [
            [InlineKeyboardButton(text=self.formatter._t('quick_analysis_button'), callback_data="analysis_quick")],
            [InlineKeyboardButton(text=self.formatter._t('full_analysis_button'), callback_data="analysis_full")],
            [InlineKeyboardButton(text=self.formatter._t('news_analysis_button'), callback_data="analysis_news")],
            [InlineKeyboardButton(text=self.formatter._t('custom_charts_button'), callback_data="analysis_custom")],
            [InlineKeyboardButton(text=self.formatter._t('back_button'), callback_data="back_main")]
        ]
        return InlineKeyboardMarkup(keyboard)

    def get_timeframe_selection(self):
        """Create timeframe selection keyboard"""
        keyboard = [
            [
                InlineKeyboardButton(text=self.formatter._t('time_1d'), callback_data="timeframe_1d"),
                InlineKeyboardButton(text=self.formatter._t('time_1w'), callback_data="timeframe_1w"),
                InlineKeyboardButton(text=self.formatter._t('time_1m'), callback_data="timeframe_1m"),
                InlineKeyboardButton(text=self.formatter._t('time_3m'), callback_data="timeframe_3m")
            ],
            [InlineKeyboardButton(text=self.formatter._t('back_button'), callback_data="back_analysis")]
        ]
        return InlineKeyboardMarkup(keyboard)

    def get_chart_types(self):
        """Create chart type selection keyboard"""
        keyboard = [
            [InlineKeyboardButton(text=self.formatter._t('price_chart'), callback_data="chart_price")],
            [InlineKeyboardButton(text=self.formatter._t('moving_averages'), callback_data="chart_ma")],
            [InlineKeyboardButton(text=self.formatter._t('macd'), callback_data="chart_macd")],
            [InlineKeyboardButton(text=self.formatter._t('rsi'), callback_data="chart_rsi")],
            [InlineKeyboardButton(text=self.formatter._t('volume_chart'), callback_data="chart_volume")],
            [InlineKeyboardButton(text=self.formatter._t('back_button'), callback_data="back_analysis")]
        ]
        return InlineKeyboardMarkup(keyboard)

    def get_settings_menu(self):
        """Create settings menu keyboard"""
        keyboard = [
            [InlineKeyboardButton(text=self.formatter._t('language_button'), callback_data="settings_language")],
            [InlineKeyboardButton(text=self.formatter._t('timeframe_button'), callback_data="settings_timeframe")],
            [InlineKeyboardButton(text=self.formatter._t('chart_type_button'), callback_data="settings_chart")],
            [InlineKeyboardButton(text=self.formatter._t('back_button'), callback_data="back_main")]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    def get_help_menu(self):
        """Create help menu keyboard"""
        keyboard = [
            [InlineKeyboardButton(text=self.formatter._t('help_intro_button'), callback_data="help_intro")],
             [InlineKeyboardButton(text=self.formatter._t('help_commands_button'), callback_data="help_commands")],
           [InlineKeyboardButton(text=self.formatter._t('help_navigation_button'), callback_data="help_navigation")],
            [InlineKeyboardButton(text=self.formatter._t('help_analysis_button'), callback_data="help_analysis")],
           [InlineKeyboardButton(text=self.formatter._t('help_charts_button'), callback_data="help_charts")],
            [InlineKeyboardButton(text=self.formatter._t('help_news_button'), callback_data="help_news")],
           [InlineKeyboardButton(text=self.formatter._t('help_agent_button'), callback_data="help_agent")],
            [InlineKeyboardButton(text=self.formatter._t('help_troubleshooting_button'), callback_data="help_troubleshooting")],
           [InlineKeyboardButton(text=self.formatter._t('help_settings_button'), callback_data="help_settings")],
           [InlineKeyboardButton(text=self.formatter._t('help_feedback_button'), callback_data="help_feedback")],
           [InlineKeyboardButton(text=self.formatter._t('back_button'), callback_data="back_main")]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    def get_help_sub_menu(self):
        """Create help sub-menu keyboard"""
        keyboard = [
             [InlineKeyboardButton(text=self.formatter._t('back_button'), callback_data="back_help")]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    def get_education_menu(self):
        """Create education menu keyboard"""
        keyboard = [
            [InlineKeyboardButton(text=self.formatter._t('education_basic_concepts'), callback_data="education_basic_concepts")],
            [InlineKeyboardButton(text=self.formatter._t('education_technical_analysis'), callback_data="education_technical_analysis")],
            [InlineKeyboardButton(text=self.formatter._t('education_trading_strategies'), callback_data="education_trading_strategies")],
             [InlineKeyboardButton(text=self.formatter._t('education_defi_nfts'), callback_data="education_defi_nfts")],
              [InlineKeyboardButton(text=self.formatter._t('education_security'), callback_data="education_security")],
            [InlineKeyboardButton(text=self.formatter._t('back_button'), callback_data="back_main")]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    def get_education_sub_menu(self, category_identifier):
        """Create education sub-menu keyboard for a specific category"""
        keyboard = []
        
        # Get all available keys that start with "education_[category_identifier]_" and ends with `_title`
        all_keys = self.formatter.languages[self.formatter.current_language].keys()
        module_keys = [key for key in all_keys if key.startswith(f"education_{category_identifier}_") and key.endswith("_title")]
        
        for key in module_keys:
            module_title = self.formatter._t(key)
            module_id = key.replace("_title", "") # get the full key up to the title
            keyboard.append([InlineKeyboardButton(text=module_title, callback_data=module_id)])
        
        # Add the back button
        keyboard.append([InlineKeyboardButton(text=self.formatter._t('back_button'), callback_data="back_education")])
        
        return InlineKeyboardMarkup(keyboard)