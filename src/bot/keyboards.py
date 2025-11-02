from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

def get_settings_kb():
    kb = [
        [
            KeyboardButton(text="Art"),
            KeyboardButton(text="Trip"),
            KeyboardButton(text="Deep")
        ],
        [
            KeyboardButton(text="Low"),
            KeyboardButton(text="Medium"),
            KeyboardButton(text="High")
        ]
    ]
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)