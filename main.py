import os
from dotenv import load_dotenv
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters
from src.bot.handlers.analysis_handlers import AnalysisHandler
from src.bot.handlers.callback_handler import CallbackHandler
from src.bot.handlers.message_handler import CustomMessageHandler  # Updated import
from src.bot.keyboards.reply_keyboards import AnalysisKeyboards

# Load environment variables
load_dotenv()

# Create shared user_states dictionary
user_states = {}

# Initialize handlers
analysis_handler = AnalysisHandler()
callback_handler = CallbackHandler()
message_handler = CustomMessageHandler()  # Updated class name
keyboards = AnalysisKeyboards()

# Share user_states between handlers
callback_handler.user_states = user_states
message_handler.user_states = user_states

async def start_command(update, context):
    """Handle /start command"""
    welcome_text = (
        "Welcome to CryptoAnalyst Bot! 🚀\n\n"
        "I can help you analyze cryptocurrencies with technical analysis "
        "and charts. Select an option below to get started:"
    )
    await update.message.reply_text(
        welcome_text,
        reply_markup=keyboards.get_main_menu()
    )

def main():
    """Main function to run the bot"""
    # Create application
    application = Application.builder().token(os.getenv("TELEGRAM_BOT_TOKEN")).build()

    # Add command handlers
    application.add_handler(CommandHandler('start', start_command))
    application.add_handler(CommandHandler('analyze', analysis_handler.cmd_analyze))
    application.add_handler(CommandHandler('quick', analysis_handler.cmd_quick))
    application.add_handler(CommandHandler('chart', analysis_handler.cmd_chart))
    
    # Add callback handler for keyboard interactions
    application.add_handler(CallbackQueryHandler(callback_handler.handle_callback))

    # Add message handler for text inputs - Fixed handler
    application.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            message_handler.handle_message
        )
    )

    # Start the bot
    print('Starting bot...')
    application.run_polling()

if __name__ == '__main__':
    
    main()