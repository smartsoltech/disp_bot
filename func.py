from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import yaml
import os

# Глобальный словарь для хранения языковых пакетов
languages = {}

def load_languages():
    """
    Загружает языковые пакеты из файлов YAML.
    """
    global languages
    language_files = [f for f in os.listdir('localization') if f.endswith('.yaml')]
    for file in language_files:
        lang_code = file.split('.')[0]
        with open(f'localization/{file}', 'r', encoding='utf8') as f:
            languages[lang_code] = yaml.safe_load(f)

def get_text(lang_code, key):
    """
    Возвращает текст по ключу для указанного языкового кода.
    """
    return languages.get(lang_code, {}).get(key, key)

def generate_inline_keyboard(buttons):
    """
    Создает и возвращает инлайн клавиатуру.
    """
    keyboard = InlineKeyboardMarkup()
    for button in buttons:
        keyboard.add(InlineKeyboardButton(text=button['text'], callback_data=button['callback']))
    return keyboard

# Инициализация языковых пакетов
load_languages()

