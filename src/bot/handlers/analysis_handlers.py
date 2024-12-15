from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from ...analysis.technical import TechnicalAnalyzer
from ...utils.formatters import TelegramFormatter
from ...data.processor import DataProcessor
from ...analysis.plot_charts import (
    plot_price_chart,
    plot_moving_averages,
    plot_macd,
    plot_rsi,
    plot_volume,
    plot_support_resistance
)
import tempfile
import os

class AnalysisHandler:
    def __init__(self):
        self.analyzer = TechnicalAnalyzer()
        self.formatter = TelegramFormatter()
        self.data_processor = DataProcessor()
        
        # Default timeframes
        self.timeframes = {
            '1d': 1,
            '1w': 7,
            '1m': 30,
            '3m': 90
        }

    async def cmd_analyze(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handler for /analyze command"""
        if not context.args:
            await update.message.reply_text(
                "Please provide a cryptocurrency symbol.\n"
                "Example: /analyze btc\n"
                "Optional: Add timeframe /analyze btc 1w"
            )
            return

        coin_id = context.args[0].lower()
        timeframe = context.args[1].lower() if len(context.args) > 1 else '1d'

        if timeframe not in self.timeframes:
            await update.message.reply_text(
                "Invalid timeframe. Please use: 1d, 1w, 1m, or 3m"
            )
            return

        # Show loading message
        loading_message = await update.message.reply_text(
            self.formatter.format_loading_message()
        )

        try:
            # Validate coin
            if not self.data_processor.validate_coin_id(coin_id):
                await loading_message.edit_text(
                    f"❌ Invalid cryptocurrency symbol: {coin_id}\n"
                    "Please try again with a valid symbol."
                )
                return

            # Get analysis
            days = self.timeframes[timeframe]
            analysis = self.analyzer.analyze_coin(coin_id, days=days)
            
            # Send text analysis
            formatted_message = self.formatter.format_full_analysis(analysis, coin_id)
            await loading_message.edit_text(formatted_message)

            # Generate and send charts
            await self._send_analysis_charts(update, analysis, coin_id)

        except Exception as e:
            await loading_message.edit_text(
                self.formatter.format_error_message(str(e))
            )

    async def cmd_quick(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handler for /quick command"""
        if not context.args:
            await update.message.reply_text(
                "Please provide a cryptocurrency symbol.\n"
                "Example: /quick btc"
            )
            return

        coin_id = context.args[0].lower()
        
        # Show loading message
        loading_message = await update.message.reply_text(
            self.formatter.format_loading_message()
        )

        try:
            # Validate coin
            if not self.data_processor.validate_coin_id(coin_id):
                await loading_message.edit_text(
                    f"❌ Invalid cryptocurrency symbol: {coin_id}\n"
                    "Please try again with a valid symbol."
                )
                return

            # Get quick analysis
            analysis = self.analyzer.get_quick_analysis(coin_id)
            formatted_message = self.formatter.format_quick_analysis(analysis, coin_id)
            
            # Send text analysis
            await loading_message.edit_text(formatted_message)

            # Send basic price chart
            await self._send_price_chart(update, analysis, coin_id)

        except Exception as e:
            await loading_message.edit_text(
                self.formatter.format_error_message(str(e))
            )

    async def cmd_chart(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handler for /chart command"""
        if len(context.args) < 2:
            await update.message.reply_text(
                "Please provide symbol and chart type.\n"
                "Example: /chart btc price\n"
                "Available types: price, ma, macd, rsi, volume"
            )
            return

        coin_id = context.args[0].lower()
        chart_type = context.args[1].lower()
        timeframe = context.args[2].lower() if len(context.args) > 2 else '1d'

        if timeframe not in self.timeframes:
            await update.message.reply_text(
                "Invalid timeframe. Please use: 1d, 1w, 1m, or 3m"
            )
            return

        # Show loading message
        loading_message = await update.message.reply_text(
            self.formatter.format_loading_message()
        )

        try:
            days = self.timeframes[timeframe]
            await self._generate_and_send_chart(
                update, 
                coin_id, 
                chart_type, 
                days,
                loading_message
            )

        except Exception as e:
            await loading_message.edit_text(
                self.formatter.format_error_message(str(e))
            )

    async def _send_analysis_charts(self, update: Update, analysis: dict, coin_id: str):
        """Generate and send multiple charts for full analysis"""
        try:
            df = self.data_processor.get_ohlcv_data(coin_id)
            
            # Generate charts in temp files
            with tempfile.TemporaryDirectory() as temp_dir:
                # Price and MA chart
                ma_data = analysis['trend_indicators']['moving_averages']
                ma_path = os.path.join(temp_dir, 'ma_chart.png')
                plot_moving_averages(df, ma_data)
                
                # MACD chart
                macd_data = analysis['trend_indicators']['macd']
                macd_path = os.path.join(temp_dir, 'macd_chart.png')
                plot_macd(macd_data, df)
                
                # RSI chart
                rsi_data = analysis['momentum_indicators']['rsi']['value']
                rsi_path = os.path.join(temp_dir, 'rsi_chart.png')
                plot_rsi(rsi_data, df)

                # Send charts
                for chart_path in [ma_path, macd_path, rsi_path]:
                    if os.path.exists(chart_path):
                        await update.message.reply_photo(
                            photo=open(chart_path, 'rb')
                        )

        except Exception as e:
            await update.message.reply_text(
                f"⚠️ Error generating charts: {str(e)}"
            )

    async def _send_price_chart(self, update: Update, analysis: dict, coin_id: str):
        """Send basic price chart for quick analysis"""
        try:
            df = self.data_processor.get_ohlcv_data(coin_id)
            
            with tempfile.TemporaryDirectory() as temp_dir:
                chart_path = os.path.join(temp_dir, 'price_chart.png')
                plot_price_chart(df)
                
                if os.path.exists(chart_path):
                    await update.message.reply_photo(
                        photo=open(chart_path, 'rb')
                    )

        except Exception as e:
            await update.message.reply_text(
                f"⚠️ Error generating price chart: {str(e)}"
            )

    async def _generate_and_send_chart(
        self, 
        update: Update, 
        coin_id: str, 
        chart_type: str, 
        days: int,
        loading_message: Update.message
    ):
        """Generate and send specific chart type"""
        try:
            df = self.data_processor.get_ohlcv_data(coin_id, days=days)
            analysis = self.analyzer.analyze_coin(coin_id, days=days)

            with tempfile.TemporaryDirectory() as temp_dir:
                chart_path = os.path.join(temp_dir, f'{chart_type}_chart.png')

                if chart_type == 'price':
                    plot_price_chart(df)
                elif chart_type == 'ma':
                    ma_data = analysis['trend_indicators']['moving_averages']
                    plot_moving_averages(df, ma_data)
                elif chart_type == 'macd':
                    macd_data = analysis['trend_indicators']['macd']
                    plot_macd(macd_data, df)
                elif chart_type == 'rsi':
                    rsi_data = analysis['momentum_indicators']['rsi']['value']
                    plot_rsi(rsi_data, df)
                elif chart_type == 'volume':
                    plot_volume(df)
                else:
                    await loading_message.edit_text(
                        "Invalid chart type. Available types: price, ma, macd, rsi, volume"
                    )
                    return

                if os.path.exists(chart_path):
                    await loading_message.delete()
                    await update.message.reply_photo(
                        photo=open(chart_path, 'rb'),
                        caption=f"{coin_id.upper()} {chart_type.upper()} Chart ({days}d)"
                    )

        except Exception as e:
            await loading_message.edit_text(
                f"⚠️ Error generating {chart_type} chart: {str(e)}"
            )