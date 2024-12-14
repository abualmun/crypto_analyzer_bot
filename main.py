import os
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from src.bot.handlers.analysis_handlers import AnalysisHandler
from src.bot.keyboards.reply_keyboards import get_main_keyboard, get_analysis_keyboard

# Load environment variables
load_dotenv()

# Initialize handlers
analysis_handler = AnalysisHandler()

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler for /start command"""
    welcome_message = (
        "Welcome to CryptoAnalyst Bot! 🚀\n\n"
        "Available commands:\n"
        "/analyze [symbol] - Full technical analysis\n"
        "/quick [symbol] - Quick market overview\n"
        "\nExample: /analyze btc or /quick eth"
    )
    await update.message.reply_text(welcome_message, reply_markup=get_main_keyboard())

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler for /help command"""
    help_text = (
        "🤖 CryptoAnalyst Bot Commands:\n\n"
        "📊 Analysis Commands:\n"
        "/analyze [symbol] - Detailed technical analysis\n"
        "/quick [symbol] - Quick market overview\n\n"
        "💡 Examples:\n"
        "/analyze btc - Analyze Bitcoin\n"
        "/quick eth - Quick Ethereum analysis\n\n"
        "You can also ask in natural language:\n"
        "'Analyze Bitcoin' or 'Quick check ETH'"
    )
    await update.message.reply_text(help_text)

async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler for text messages"""
    text = update.message.text

    if text == '📊 Analysis':
        await update.message.reply_text(
            "Choose analysis type:",
            reply_markup=get_analysis_keyboard()
        )
    elif text == '📈 Quick Analysis' or text == '📊 Deep Analysis':
        await update.message.reply_text(
            "Please send the cryptocurrency symbol you want to analyze.\n"
            "Example: BTC or ETH"
        )
    elif text == '↩️ Back':
        await update.message.reply_text(
            "Main menu:",
            reply_markup=get_main_keyboard()
        )
    else:
        # Handle as potential analysis request
        await analysis_handler.handle_text_analysis(update, context)

def main():
    """Main function to run the bot"""
    # Create application
    application = Application.builder().token(os.getenv('TELEGRAM_BOT_TOKEN')).build()

    # Add handlers
    application.add_handler(CommandHandler('start', start_command))
    application.add_handler(CommandHandler('help', help_command))
    application.add_handler(CommandHandler('analyze', analysis_handler.cmd_analyze))
    application.add_handler(CommandHandler('quick', analysis_handler.cmd_quick))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))

    # Start the bot
    print('Starting bot...')
    application.run_polling()

if __name__ == '__main__':
    main()