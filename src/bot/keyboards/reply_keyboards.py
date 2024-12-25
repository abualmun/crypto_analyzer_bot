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