import telebot
import db
import func
import os
from dotenv import load_dotenv
from icecream import ic
load_dotenv()

TOKEN = os.getenv("BOT_TOKEN")
bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def start_message(message):
    user_lang = db.get_user_language(message.from_user.id)
    welcome_text = func.get_text(user_lang, 'welcome')
    bot.send_message(message.chat.id, welcome_text)

@bot.message_handler(commands=['language'])
def change_language(message):
    markup = telebot.types.ReplyKeyboardMarkup(one_time_keyboard=True)
    # Добавляем кнопки для выбора языка
    markup.add('English', 'Русский', 'Қазақша')

    msg = bot.send_message(message.chat.id, "Выберите язык / Choose language / Тілді таңдаңыз", reply_markup=markup)
    bot.register_next_step_handler(msg, set_language)

def set_language(message):
    user_lang = message.text
    # Обновляем язык пользователя в базе данных
    db.update_user_language(message.from_user.id, user_lang)
    bot.send_message(message.chat.id, "Язык изменен на " + user_lang)

@bot.message_handler(commands=['new_issue'])
def new_issue(message):
    msg = bot.send_message(message.chat.id, "Опишите проблему:")
    bot.register_next_step_handler(msg, process_issue_description)

def process_issue_description(message):
    issue = {'description': message.text}
    msg = bot.send_message(message.chat.id, "Введите адрес:")
    bot.register_next_step_handler(msg, process_issue_address, issue)

def process_issue_address(message, issue):
    issue['address'] = message.text
    msg = bot.send_message(message.chat.id, "Отправьте фото (или пропустите этот шаг):")
    bot.register_next_step_handler(msg, process_issue_photo, issue)

def process_issue_photo(message, issue):
    if message.content_type == 'photo':
        photo = message.photo[-1].file_id
        issue['photo'] = photo
    msg = bot.send_message(message.chat.id, "Отправьте вашу геопозицию (или пропустите этот шаг):")
    bot.register_next_step_handler(msg, process_issue_location, issue)

def process_issue_location(message, issue):
    if message.content_type == 'location':
        location = message.location
        issue['location'] = (location.latitude, location.longitude)
    msg = bot.send_message(message.chat.id, "Введите контактный телефон:")
    bot.register_next_step_handler(msg, process_issue_phone, issue)

def process_issue_phone(message, issue):
    issue['phone'] = message.text
    # Сохраняем заявку в базу данных
    ic(issue)
    db.save_new_issue(issue, message.chat.id)
    bot.send_message(message.chat.id, "Заявка создана.")



@bot.message_handler(func=lambda message: message.text in ["Новые заявки", "В работе", "Завершенные"])
def show_issues_by_status(message):
    status = db.IssueStatus.NEW if message.text == "Новые заявки" \
        else db.IssueStatus.IN_PROGRESS if message.text == "В работе" \
        else db.IssueStatus.RESOLVED
    issues = db.get_issues_by_status(status)
    for issue in issues:
        bot.send_message(message.chat.id, f"Заявка {issue.id}: {issue.description}")

bot.polling()
