from telegram import InlineKeyboardButton, InlineKeyboardMarkup

class AnalysisKeyboards:
    @staticmethod
    def get_main_menu():
        """Create main menu keyboard"""
        keyboard = [
            [
                InlineKeyboardButton("📊 Analysis", callback_data="menu_analysis"),
                InlineKeyboardButton("📈 Charts", callback_data="menu_charts")
            ],
            [
                InlineKeyboardButton("📚 Help", callback_data="menu_help"),
                InlineKeyboardButton("⚙️ Settings", callback_data="menu_settings")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def get_analysis_menu():
        """Create analysis selection keyboard"""
        keyboard = [
            [InlineKeyboardButton("📊 Quick Analysis", callback_data="analysis_quick")],
            [InlineKeyboardButton("📈 Full Analysis", callback_data="analysis_full")],
            [InlineKeyboardButton("🛰️ News Analysis", callback_data="analysis_news")],
            [InlineKeyboardButton("🔍 Custom Charts", callback_data="analysis_custom")],
            [InlineKeyboardButton("↩️ Back to Menu", callback_data="back_main")]
        ]
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def get_timeframe_selection():
        """Create timeframe selection keyboard"""
        keyboard = [
            [
                InlineKeyboardButton("1D", callback_data="timeframe_1d"),
                InlineKeyboardButton("1W", callback_data="timeframe_1w"),
                InlineKeyboardButton("1M", callback_data="timeframe_1m"),
                InlineKeyboardButton("3M", callback_data="timeframe_3m")
            ],
            [InlineKeyboardButton("↩️ Back", callback_data="back_analysis")]
        ]
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def get_chart_types():
        """Create chart type selection keyboard"""
        keyboard = [
            [InlineKeyboardButton("📊 Price Chart", callback_data="chart_price")],
            [InlineKeyboardButton("📈 Moving Averages", callback_data="chart_ma")],
            [InlineKeyboardButton("📉 MACD", callback_data="chart_macd")],
            [InlineKeyboardButton("📊 RSI", callback_data="chart_rsi")],
            [InlineKeyboardButton("📊 Volume", callback_data="chart_volume")],
            [InlineKeyboardButton("↩️ Back", callback_data="back_analysis")]
        ]
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def get_settings_menu():
        """Create settings menu keyboard"""
        keyboard = [
            [InlineKeyboardButton("🌐 Language", callback_data="settings_language")],
            [InlineKeyboardButton("⏰ Default Timeframe", callback_data="settings_timeframe")],
            [InlineKeyboardButton("📊 Default Chart Type", callback_data="settings_chart")],
            [InlineKeyboardButton("↩️ Back to Menu", callback_data="back_main")]
        ]
        return InlineKeyboardMarkup(keyboard)