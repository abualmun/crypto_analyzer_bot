# Updated main.py
import os
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from src.bot.keyboards.reply_keyboards import get_main_keyboard, get_analysis_keyboard, get_learn_keyboard

load_dotenv()

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Welcome to Smart Crypto Analyzer Bot! 🚀\n\n"
        "I'm here to help you with cryptocurrency analysis and education.\n\n"
        "Use the keyboard below to navigate through features:",
        reply_markup=get_main_keyboard()
    )

async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    if text == '📊 Analysis':
        await update.message.reply_text(
            "Choose analysis type:",
            reply_markup=get_analysis_keyboard()
        )
    elif text == '📚 Learn':
        await update.message.reply_text(
            "What would you like to learn about?",
            reply_markup=get_learn_keyboard()
        )
    elif text == '↩️ Back':
        await update.message.reply_text(
            "Main menu:",
            reply_markup=get_main_keyboard()
        )
    # Add more handlers for other buttons

def main():
    application = Application.builder().token(os.getenv('TELEGRAM_BOT_TOKEN')).build()

    # Add handlers
    application.add_handler(CommandHandler('start', start_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))

    print('Starting bot...')
    application.run_polling()

if __name__ == '__main__':
    main()