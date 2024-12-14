# main.py (updated)

import os
from dotenv import load_dotenv
from telegram.ext import Application, CommandHandler, CallbackQueryHandler
from src.bot.handlers.analysis_handlers import AnalysisHandlers

load_dotenv()

async def start(update, context):
    await update.message.reply_text(
        "Welcome to Crypto Analysis Bot! 🚀\n\n"
        "Use /analyze <symbol> to get quick analysis\n"
        "Example: /analyze btc"
    )

async def handle_callback(update, context):
    """Handle callback queries from inline buttons"""
    query = update.callback_query
    await query.answer()
    
    if query.data.startswith('detailed_'):
        coin_id = query.data.split('_')[1]
        await query.message.reply_text(f"Detailed analysis for {coin_id} coming soon!")

def main():
    # Create application
    application = Application.builder().token(os.getenv('TELEGRAM_BOT_TOKEN')).build()
    
    # Initialize handlers
    analysis_handlers = AnalysisHandlers()
    
    # Add handlers
    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('analyze', analysis_handlers.quick_analysis))
    application.add_handler(CallbackQueryHandler(handle_callback))
    
    # Start bot
    print('Starting bot...')
    application.run_polling()

if __name__ == '__main__':
    main()