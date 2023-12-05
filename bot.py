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
    ic(user_lang)
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


@bot.message_handler(commands=['view_issues'])
def view_issues(message):
    markup = telebot.types.ReplyKeyboardMarkup(one_time_keyboard=True)
    for status in db.IssueStatus:
        markup.add(status.value)
    msg = bot.send_message(message.chat.id, "Выберите статус заявки:", reply_markup=markup)
    bot.register_next_step_handler(msg, show_issues_by_status)

def show_issues_by_status(message):
    status = message.text
    issues = db.get_issues_by_status(status)
    response = '\n'.join([f"ID: {issue.id}, Описание: {issue.description}" for issue in issues])
    bot.send_message(message.chat.id, response or "Заявки не найдены.")

def generate_yandex_map_link(location_str):
    location = tuple(map(float, location_str.strip("()").split(", ")))
    latitude, longitude = location
    base_url = "https://yandex.ru/maps/?"
    params = f"ll={longitude},{latitude}&z=12&l=map&pt={longitude},{latitude}"
    return base_url + params

@bot.message_handler(func=lambda message: message.text in ["Новый", "В работе", "Завершенные"])
def show_issues_by_status(message):
    status = db.IssueStatus.NEW if message.text == "Новый" \
        else db.IssueStatus.IN_PROGRESS if message.text == "В работе" \
        else db.IssueStatus.RESOLVED
    issues = db.get_issues_by_status(status)
    for issue in issues:
        bot.send_message(message.chat.id, f"Заявка {issue.id}: {issue.description}")
                # Проверяем, есть ли в заявке изображение
        if issue.photo:
            bot.send_photo(message.chat.id, issue.photo)
                # Отправка ссылки на карту, если есть координаты
        if issue.location:
            map_link = generate_yandex_map_link(issue.location)
            bot.send_message(message.chat.id, f"Местоположение: {map_link}")

@bot.message_handler(commands=['export_issues'])
def handle_export_issues(message):
    filename = 'issues_export.xlsx'
    func.export_issues_to_excel(filename)

    # Отправляем файл в чат
    with open(filename, 'rb') as file:
        bot.send_document(message.chat.id, file)


bot.polling()
