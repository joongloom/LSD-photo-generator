from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

def get_settings_kb():
    kb = [
        [KeyboardButton(text="Low"), KeyboardButton(text="Medium"), KeyboardButton(text="High")],
        [KeyboardButton(text="🎲 Surprise Me (Random)")]
    ]
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)