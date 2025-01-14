from src.bot import keyboards
from src.bot.keyboards import reply_keyboards
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from src.services.database_manager import DatabaseManager
from ...analysis.technical import TechnicalAnalyzer
from ...utils.formatters import TelegramFormatter
from ...utils.news_formatters import NewsFormatter
from ...data.processor import DataProcessor
import asyncio
from ...data.cc_news import CryptoNewsFetcher
from ...analysis.plot_charts_html import (
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
        self.keyboards = reply_keyboards.AnalysisKeyboards()
        self.db_manager = DatabaseManager()
        # Default timeframes
        self.timeframes = {
            '1d': 1,
            '1w': 7,
            '1m': 30,
            '3m': 90
        }

    async def cmd_news(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        self.formatter.set_language(context.user_data['language'])

        """Handler for /news command"""
        if not context.args:
            await update.message.reply_text(
                self.formatter._t('provide_symbol_news')
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
                         f"❌ {self.formatter._t('no_news_found')}: {coin_symbol}"
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
                f"{self.formatter._t('provide_symbol_prompt')}\n"
                f"{self.formatter._t('analyze_example')}\n"
                f"{self.formatter._t('timeframe_optional')}"
            )
            return
      
        coin_id = context.args[0].lower()       
        timeframe = context.args[1].lower() if len(context.args) > 1 else '1d'
        if timeframe not in self.timeframes:
            await update.message.reply_text(self.formatter._t('invalid_timeframe'))
            return

        # Show loading message
        loading_message = await update.message.reply_text(
            self.formatter._t('loading')
        )

        try:
            if not self.data_processor.validate_coin_id(coin_id):
                await loading_message.edit_text(
                    f"❌ {self.formatter._t('invalid_symbol')}: {coin_id}\n"
                    f"{self.formatter._t('provide_symbol_prompt')}"
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
            # log the activities in the database
            self.db_manager.log_user_activity({
                'user_id':update.message.from_user.id,
                'coin_id':coin_id,
                'activity_type':'full',
                'timestamp':days}) 
            self.db_manager.log_user_search({
                'user_id':update.message.from_user.id,
                'coin_id':coin_id,}) 
            
        except Exception as e:
            print(str(e))
            # await loading_message.edit_text(
            #     self.formatter.format_error_message(str(e))
            # )

    async def cmd_quick(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        self.formatter.set_language(context.user_data['language'])

        """Handler for /quick command"""
        if not context.args:
            await update.message.reply_text(
                f"{self.formatter._t('provide_symbol_prompt')}\n"
                f"{self.formatter._t('quick_example')}"
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
                     f"❌ {self.formatter._t('invalid_symbol')}: {coin_id}\n"
                    f"{self.formatter._t('try_different_symbol')}"
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
            # log the activities in the database

            self.db_manager.log_user_activity({
                'user_id':update.message.from_user.id,
                'coin_id':coin_id,
                'activity_type':'price',
                'timestamp':1})
            self.db_manager.log_user_search({
                'user_id':update.message.from_user.id,
                'coin_id':coin_id,})
        except Exception as e:
            await loading_message.edit_text(
                self.formatter.format_error_message(str(e))
            )

    async def cmd_chart(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        self.formatter.set_language(context.user_data['language'])
        """Handler for /chart command"""
        if len(context.args) < 2:
            await update.message.reply_text(
           f"{self.formatter._t('provide_symbol_and_chart')}\n"
           f"{self.formatter._t('chart_example')}\n"
           f"{self.formatter._t('available_chart_types')}"
            )
            return

        coin_id = context.args[0].lower()
        chart_type = context.args[1].lower()
        timeframe = context.args[2].lower() if len(context.args) > 2 else '1d'

        if timeframe not in self.timeframes:
            await update.message.reply_text(
                self.formatter._t('invalid_timeframe')           
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
            # log the activities in the database
            self.db_manager.log_user_activity({
                'user_id':update.message.from_user.id,
                'coin_id':coin_id,
                'activity_type':chart_type,
                'timestamp':days})
            
            self.db_manager.log_user_search({
                'user_id':update.message.from_user.id,
                'coin_id':coin_id,})

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
    intro_text=None
):
        """Generate and send specific chart type with progress bar."""
        try:
            # Initialize progress
            progress = 0
            progress_bar_template = self.formatter._t('generating_chart_progress')

            async def update_progress_bar(target_progress,loading_message):
                steps=3
                delay=0.1
                """
                Smoothly update the progress bar to the target percentage.
                
                Args:
                    target_progress (int): The target progress percentage (0 to 100).
                    steps (int): The number of smooth steps to reach the target.
                    delay (float): Time delay (in seconds) between steps.
                """
                nonlocal progress  # Use the outer `progress` variable
                increment = (target_progress - progress) / steps
                current_message = None  # Store the last sent message content

                for _ in range(steps):
                    progress += increment
                    filled_length = int(20 * progress / 100)  # Bar length: 20 chars
                    bar = "█" * filled_length + " " * (20 - filled_length)
                    new_message = progress_bar_template.format(bar, int(progress))

                    # Only update if the message content has changed
                    if new_message != current_message:
                        current_message = new_message
                        await loading_message.edit_text(new_message)

                    await asyncio.sleep(delay)
            # Step 1: Load OHLCV data
            loading_message = await update.message.reply_text(
            self.formatter.format_loading_message()
        )
            await update_progress_bar(progress,loading_message)
            df = self.data_processor.get_ohlcv_data(coin_id=coin_id, days=days)

            await update_progress_bar(progress+ 20,loading_message)

            # Step 2: Perform analysis
            analysis = self.analyzer.analyze_coin(coin_id, days=days)
            await update_progress_bar(progress+20,loading_message)

            with tempfile.TemporaryDirectory() as temp_dir:
                chart_path = os.path.join(temp_dir, f'{chart_type}_chart.html')

                # Step 3: Generate chart based on type
                if chart_type == 'price':
                    save_charts_to_pdf(filename=chart_path, df=df, style=create_plot_style(color_up='blue', color_down='orange', bgcolor='lightgray'), charts_to_include=['price'])
                elif chart_type == 'ma':
                    ma_data = analysis['trend_indicators']['moving_averages']
                    save_charts_to_pdf(filename=chart_path, df=df, ma_data=ma_data, style=create_plot_style(color_up='blue', color_down='orange', bgcolor='lightgray'), charts_to_include=['moving_averages'])
                elif chart_type == 'macd':
                    macd_data = analysis['trend_indicators']['macd']
                    save_charts_to_pdf(filename=chart_path, df=df, macd_data=macd_data, style=create_plot_style(color_up='blue', color_down='orange', bgcolor='lightgray'), charts_to_include=['macd'])
                elif chart_type == 'rsi':
                    rsi_data = analysis['momentum_indicators']['rsi']['all']
                    save_charts_to_pdf(filename=chart_path, df=df, rsi_data=rsi_data, style=create_plot_style(color_up='blue', color_down='orange', bgcolor='lightgray'), charts_to_include=['rsi'])
                elif chart_type == 'volume':
                    save_charts_to_pdf(filename=chart_path, df=df, style=create_plot_style(color_up='blue', color_down='orange', bgcolor='lightgray'), charts_to_include=['volume'])
                elif chart_type == 'full':
                    ma_data = analysis['trend_indicators']['moving_averages']  
                    macd_data = analysis['trend_indicators']['macd']
                    rsi_data = analysis['momentum_indicators']['rsi']['all']    
                    save_charts_to_pdf(
                        filename=chart_path,
                        df=df,
                        ma_data=ma_data,
                        macd_data=macd_data,
                        rsi_data=rsi_data,
                        style=create_plot_style(color_up='blue', color_down='orange', bgcolor='lightgray'),
                        charts_to_include=['price', 'moving_averages', 'macd', 'rsi', 'volume'],
                        intro_text=intro_text
                    )
                
                else:
                    await loading_message.edit_text(self.formatter._t('invalid_chart_type'))
                    return

                await update_progress_bar(progress+40,loading_message)

                # Step 4: Send the chart
                if os.path.exists(chart_path):
                    await loading_message.delete()
                    await update.message.reply_document(
                        document=open(chart_path, 'rb'),
                        caption=f"{coin_id.upper()} {chart_type.upper()} Chart ({days}d)"
                    )
                    

            # Final progress update
            await update.message.reply_text(self.formatter._t('chart_complete'),reply_markup=self.keyboards.get_main_menu())
            return
        except Exception as e:
            await loading_message.edit_text(f"{self.formatter._t('error_generating_chart')}: {str(e)}")
