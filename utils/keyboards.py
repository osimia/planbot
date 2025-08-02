from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

def main_menu_kb():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Добавить доход"), KeyboardButton(text="Добавить расход")],
            [KeyboardButton(text="Статистика")],
            [KeyboardButton(text="Советы")],
            [KeyboardButton(text="Главное меню")],
        ],
        resize_keyboard=True
    )

# Универсальная функция для сценариев

def scenario_kb(options):
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=opt)] for opt in options] + [[KeyboardButton(text="Главное меню")]],
        resize_keyboard=True
    )
