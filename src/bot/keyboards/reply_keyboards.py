# src/bot/keyboards/reply_keyboards.py
from telegram import ReplyKeyboardMarkup

def get_main_keyboard():
    keyboard = [
        ['📊 Analysis', '📚 Learn'],
        ['⚙️ Settings', '❓ Help']
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def get_analysis_keyboard():
    keyboard = [
        ['📈 Quick Analysis', '📊 Deep Analysis'],
        ['🔍 Search Coin', '↩️ Back']
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def get_learn_keyboard():
    keyboard = [
        ['📚 Basic Concepts', '📊 Technical Analysis'],
        ['💡 Trading Tips', '↩️ Back']
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)