import telebot
from telebot import types
import db
import func
import os
from dotenv import load_dotenv
from icecream import ic
import yaml

load_dotenv()

TOKEN = os.getenv("BOT_TOKEN")
bot = telebot.TeleBot(TOKEN)

user_states = []
user_choices={}

def load_yaml_config(path):
    with open(path, 'r', encoding='utf-8') as file:
        return yaml.safe_load(file)

config = load_yaml_config('dialog.yaml')

def set_user_state(user_id, state):
    user_states[user_id] = state
  
def update_user_state(user_id, new_state):
# Assuming you have a data structure to store user states, like a dictionary
# You can use the user_id as a key to store the state for each user
# For example:
    user_states[user_id] = new_state
  
def save_user_choice(user_id, key, value):
    # Assuming you have a data structure to store user choices, like a dictionary
    # You can use the user_id as a key to store choices for each user
    # For example:
    if user_id not in user_choices:
        user_choices[user_id] = {}
    user_choices[user_id][key] = value

def get_user_state(user_id):
    return user_states.get(user_id, 'start')

def reset_user_state(user_id):
    user_states.pop(user_id, None)

def handle_dialog(message, step):
    user_id = message.chat.id
    set_user_state(user_id, step)
    step_data = config['steps'][step]
    markup = None

    if 'options' in step_data:
        markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
        for option in step_data['options']:
            markup.add(types.KeyboardButton(option))

    elif 'inline_keyboard' in step_data:
        markup = types.InlineKeyboardMarkup()
        for option in step_data['inline_keyboard']:
            markup.add(types.InlineKeyboardButton(option, callback_data=option))
    ic(step_data)
    bot.send_message(user_id, step_data['message'], reply_markup=markup)


def handle_dialog(message, step):
    step_data = config['steps'][step]
    markup = None

    if 'options' in step_data:
        markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
        for option in step_data['options']:
            markup.add(types.KeyboardButton(option))

    elif 'inline_keyboard' in step_data:
        markup = types.InlineKeyboardMarkup()
        for option in step_data['inline_keyboard']:
            markup.add(types.InlineKeyboardButton(option, callback_data=option))
            ic(option)

    bot.send_message(message.chat.id, step_data['message'], reply_markup=markup)

def send_light_outage_options(message):
    markup = types.InlineKeyboardMarkup()
    for i in range(1, 11):
        markup.add(types.InlineKeyboardButton(str(i), callback_data=str(i)))
    markup.add(types.InlineKeyboardButton("Все", callback_data="all"))
    bot.send_message(message.chat.id, "Выберите количество фонарей:", reply_markup=markup)

def send_inline_keyboard(message, step_name):
    step_data = config['steps'][step_name]
    markup = types.InlineKeyboardMarkup()

    row_buttons = []
    for i, option in enumerate(step_data['inline_options'], start=1):
        row_buttons.append(types.InlineKeyboardButton(str(option), callback_data=str(option)))

        # Проверка на layout и перенос на новую строку
        if i % step_data['layout'][0] == 0 or i == len(step_data['inline_options']):
            markup.row(*row_buttons)
            row_buttons = []

    bot.send_message(message.chat.id, step_data['message'], reply_markup=markup)


@bot.message_handler(commands=['start'])
def start_message(message):
    ic(handle_dialog(message, 'start'))


# @bot.message_handler(commands=['start'])
# def start_message(message):
#     user_lang = db.get_user_language(message.from_user.id)
#     ic(user_lang)
#     welcome_text = func.get_text(user_lang, 'welcome')
#     bot.send_message(message.chat.id, welcome_text)

@bot.message_handler(commands=['language'])
def change_language(message):
    markup = telebot.types.ReplyKeyboardMarkup(one_time_keyboard=True)
    # Добавляем кнопки для выбора языка
    markup.add('English', 'Русский', 'Қазақша')

    msg = bot.send_message(message.chat.id, "Выберите язык / Choose language / Тілді таңдаңыз", reply_markup=markup)
    ic(bot.register_next_step_handler(msg, set_language))

def set_language(message):
    user_lang = message.text
    # Обновляем язык пользователя в базе данных
    db.update_user_language(message.from_user.id, user_lang)
    ic(bot.send_message(message.chat.id, "Язык изменен на " + user_lang))

@bot.message_handler(commands=['new_issue'])
def new_issue(message):
    set_user_state(message.chat.id, 'new_issue')
    msg = bot.send_message(message.chat.id, "Опишите проблему:")
    ic(bot.register_next_step_handler(msg, process_issue_description))

def process_issue_description(message):
    issue = {'description': message.text}
    update_user_state(message.chat.id, 'description')
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

@bot.callback_query_handler(func=lambda call: True)
def handle_callback(call):
    print('принт из коллбэка')
    user_id = call.from_user.id
    callback_data = call.data
    current_step = get_user_state(user_id)
    ic(user_id, current_step, callback_data)
    ic(call.data)
    if current_step == 'start':
        if callback_data in ["Горит освещение днем", "Аварийная опора"]:
            save_user_choice(user_id, 'problem_type', callback_data)
            handle_dialog(call.message, 'address')
        elif callback_data == "Не горит освещение":
            send_light_outage_options(call.message)
            save_user_choice(user_id, 'problem_type', callback_data)
            update_user_state(user_id, 'light_outage')
    elif current_step == 'light_outage':
        if callback_data.isdigit():
            save_user_choice(user_id, 'non_working_lights', callback_data)
        handle_dialog(call.message, 'address')
    # Handle other steps of the questionnaire based on the user's choices

    bot.answer_callback_query(call.id)



bot.polling()
