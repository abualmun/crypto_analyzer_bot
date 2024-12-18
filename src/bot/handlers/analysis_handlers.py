from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from ...analysis.technical import TechnicalAnalyzer
from ...utils.formatters import TelegramFormatter
from ...utils.news_formatters import NewsFormatter
from ...data.processor import DataProcessor
from ...data.cc_news import CryptoNewsFetcher
from ...analysis.plot_charts import (
    create_plot_style,
    save_charts_to_pdf
)
import tempfile
import os

class AnalysisHandler:
    def __init__(self):
        self.analyzer = TechnicalAnalyzer()
        self.formatter = TelegramFormatter()
        self.data_processor = DataProcessor()
        self.news_fetcher = CryptoNewsFetcher(os.getenv("CRYPTO_NEWS_TOKEN"))
        self.news_formatter = NewsFormatter()
        # Default timeframes
        self.timeframes = {
            '1d': 1,
            '1w': 7,
            '1m': 30,
            '3m': 90
        }

    async def cmd_news(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handler for /news command"""
        if not context.args:
            await update.message.reply_text(
                "Please provide a cryptocurrency symbol.\n"
                "Example: /news btc"
            )
            return

        coin_symbol = context.args[0].upper()
        
        # Show loading message
        loading_message = await update.message.reply_text(
            self.formatter.format_loading_message()
        )

        try:
            # Get news articles
            news_df, success = self.news_fetcher.get_news_by_coin(
                categories=coin_symbol,
                limit=10,
                lang="EN"
            )
            
            if not success or news_df.empty:
                await loading_message.edit_text(
                    f"❌ No news found for {coin_symbol}\n"
                    "Please try again with a different symbol."
                )
                return

            # Get formatted message
            formatted_message = self.news_formatter.format_news(news_df, coin_symbol)
            
            # Send news summary
            await loading_message.edit_text(
                formatted_message,
                disable_web_page_preview=True  # Prevent URL previews from cluttering the message
            )

        except Exception as e:
            await loading_message.edit_text(
                self.formatter.format_error_message(str(e))
            )

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
            # await self._send_analysis_charts(update, analysis, coin_id,formatted_message)
            await self._generate_and_send_chart( 
        update=update, 
        coin_id= coin_id, 
        chart_type= 'full', 
        days=days,
        loading_message = update.message,
        intro_text=formatted_message
    )
        except Exception as e:
            print(str(e))
            # await loading_message.edit_text(
            #     self.formatter.format_error_message(str(e))
            # )

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
            analysis = self.analyzer.analyze_coin(coin_id=coin_id,days=1)
            formatted_message = self.formatter._format_summary(analysis['summary'])
            
            # Send text analysis
            await loading_message.edit_text(formatted_message)

            # Send basic price chart
            # await self._send_price_chart(update, analysis, coin_id,formatted_message)
            await self._generate_and_send_chart(
        update= update, 
        coin_id=coin_id, 
        chart_type = 'price',
        days=1, 
        loading_message=update.message,
        intro_text=formatted_message
    )
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

    async def _generate_and_send_chart(
        self, 
        update: Update, 
        coin_id: str, 
        chart_type: str, 
        days: int,
        loading_message: Update.message,
        intro_text = None
    ):
        """Generate and send specific chart type"""
        # coin_id = DataProcessor.symbol_mapping[coin_id]
        try:
            df = self.data_processor.get_ohlcv_data(coin_id = DataProcessor.symbol_mapping[coin_id], days=days)
            analysis = self.analyzer.analyze_coin(coin_id, days=days)

            with tempfile.TemporaryDirectory() as temp_dir:
                chart_path = os.path.join(temp_dir, f'{chart_type}_chart.pdf')

                if chart_type == 'price':
                    save_charts_to_pdf(filename=chart_path, df=df, style=create_plot_style(color_up='blue', color_down='orange', bgcolor='lightgray'), charts_to_include=['price'])
                elif chart_type == 'ma':
                    ma_data = analysis['trend_indicators']['moving_averages']
                    save_charts_to_pdf(filename=chart_path, df=df,ma_data=ma_data, style=create_plot_style(color_up='blue', color_down='orange', bgcolor='lightgray'), charts_to_include=['moving_averages'])
                elif chart_type == 'macd':
                    macd_data = analysis['trend_indicators']['macd']
                    save_charts_to_pdf(filename=chart_path, df=df,macd_data=macd_data, style=create_plot_style(color_up='blue', color_down='orange', bgcolor='lightgray'), charts_to_include=['macd'])
                elif chart_type == 'rsi':
                    rsi_data = analysis['momentum_indicators']['rsi']['all']
                    save_charts_to_pdf(filename=chart_path, df=df,rsi_data=rsi_data, style=create_plot_style(color_up='blue', color_down='orange', bgcolor='lightgray'), charts_to_include=['rsi'])
                elif chart_type == 'volume':
                    save_charts_to_pdf(filename=chart_path, df=df, style=create_plot_style(color_up='blue', color_down='orange', bgcolor='lightgray'), charts_to_include=['volume'])
                elif chart_type == 'full':
                    ma_data = analysis['trend_indicators']['moving_averages']  
                    macd_data = analysis['trend_indicators']['macd']
                    rsi_data = analysis['momentum_indicators']['rsi']['all']    
                    save_charts_to_pdf(filename=chart_path, df=df,ma_data=ma_data,macd_data=macd_data,rsi_data=rsi_data, style=create_plot_style(color_up='blue', color_down='orange', bgcolor='lightgray'), charts_to_include=['price','moving_averages','macd','rsi','volume'],intro_text=intro_text)

                else:
                    await loading_message.edit_text(
                        "Invalid chart type. Available types: price, ma, macd, rsi, volume"
                    )
                    return
        
                if os.path.exists(chart_path):
                    await loading_message.delete()
                    await update.message.reply_document(
                       document=open(chart_path, 'rb'),
                        caption=f"{coin_id.upper()} {chart_type.upper()} Chart ({days}d)"
                    )

        except Exception as e:
            await loading_message.edit_text(
                f"⚠️ Error generating {chart_type} chart: {str(e)}"
            )
    # async def _send_analysis_charts(self, update: Update, analysis: dict, coin_id: str,message: str):
    #     """Generate and send multiple charts for full analysis"""
    #     coin_id = DataProcessor.symbol_mapping[coin_id]
    #     try:
    #         message = 'yo'
    #         df = self.data_processor.get_ohlcv_data(coin_id)
    #         filename='selected_charts.pdf'
    #         # Generate charts in temp files
    #         with tempfile.TemporaryDirectory() as temp_dir:
    #             # Price and MA chart
    #             ma_data = analysis['trend_indicators']['moving_averages']
                
                
    #             # MACD chart
    #             macd_data = analysis['trend_indicators']['macd']
                
    #             # RSI chart
    #             rsi_data = analysis['momentum_indicators']['rsi']['all']
                

    #             await save_charts_to_pdf(filename=temp_dir+filename, df=df, ma_data=ma_data, macd_data=macd_data, rsi_data=rsi_data, style=create_plot_style(color_up='blue', color_down='orange', bgcolor='lightgray'), charts_to_include=['moving_averages','rsi', 'macd'],labels=[message,'',''])
    #             # Send charts
    #             if os.path.exists(temp_dir+filename):
    #                 await update.message.reply_document(
    #                 document=open(temp_dir+filename, 'rb'),
    #                 filename="Analysis_Charts.pdf"
    #         )

    #     except Exception as e:
    #         await update.message.reply_text(
    #             f"⚠️ Error generating charts: {str(e)}"
    #         )

    # async def _send_price_chart(self, update: Update, analysis: dict, coin_id: str,message:str):
    #     """Send basic price chart for quick analysis"""
    #     coin_id = DataProcessor.symbol_mapping[coin_id]

    #     try:
    #         df = self.data_processor.get_ohlcv_data(coin_id)
    #         filename='Price_Charts.pdf'
    #         with tempfile.TemporaryDirectory() as temp_dir:                
    #             await save_charts_to_pdf(filename=temp_dir+filename, df=df, style=create_plot_style(color_up='blue', color_down='orange', bgcolor='lightgray'), charts_to_include=['price'],labels=[message])
    #             # Send charts
    #             if os.path.exists(temp_dir+filename):
    #                 await update.message.reply_document(
    #                 document=open(temp_dir+filename, 'rb'),
    #                 filename="Price_Charts.pdf"
    #         )

    #     except Exception as e:
    #         await update.message.reply_text(
    #             f"⚠️ Error generating price chart: {str(e)}"
    #         )
