import telebot
from telebot import types
import json
from email_sender import send_email
from datetime import date
from dotenv import dotenv_values


config = dotenv_values("config.env")

# Завантаження тексту повідомлень з файлу JSON

with open('data.json', 'r', encoding='utf-8') as file:
    messages = json.load(file)


# Токен бота

bot = telebot.TeleBot(config.get("TELEGRAM_BOT_TOKEN"))

anonym_mode = set()
info_list = []
chat_messages = []
user_data = {}


# Обробка команди /start


@bot.message_handler(commands=['start'])
def start_message(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(types.KeyboardButton(messages["start_button"]))
    anonym_mode.add(message.from_user.id)
    bot.send_message(message.chat.id, messages["start_message"], reply_markup=markup)


# Обробка повідомлень з кнопкою "start_button"


@bot.message_handler(func=lambda message: message.text == messages["start_button"])
def handle_start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(types.KeyboardButton(messages["anon_yes_button"]), types.KeyboardButton(messages["anon_no_button"]))
    bot.send_message(message.chat.id, messages["anon_question"], reply_markup=markup)


# Обробка повідомлень з кнопкою "anon_yes_button"


@bot.message_handler(func=lambda message: message.text == messages["anon_yes_button"])
def handle_yes(message):
    bot.send_message(message.chat.id, messages["anon_response"])
    bot.send_message(message.chat.id, messages["choose_topic_message"])
    info_list.append(f'Контактна інформація: Анонімно')
    show_topics(message)

# Обробка повідомлень з кнопкою "anon_no_button"


@bot.message_handler(func=lambda message: message.text == messages["anon_no_button"])
def handle_no(message):
    bot.send_message(message.chat.id, messages["non_anon_response"])
    bot.send_message(message.chat.id, messages["contact_info_prompt"])
    bot.register_next_step_handler(message, collect_contact_data)

# Збір контактних даних


def collect_contact_data(message):
    info_list.append(f'Контактна інформація: {message.text}')
    process_contact_info(message)

# Обробка контактної інформації та перехід до вибору теми


def process_contact_info(message):
    bot.send_message(message.chat.id, messages["choose_topic_message"])
    show_topics(message)
    anonym_mode.discard(message.from_user.id)

# Відображення доступних тем


def show_topics(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(types.KeyboardButton(messages["bulling"]), types.KeyboardButton(messages["v1"]))
    markup.add(types.KeyboardButton(messages["v2"]), types.KeyboardButton(messages["Other"]))
    markup.add(types.KeyboardButton(messages["button_back"]))
    bot.send_message(message.chat.id, messages["topic_selection"], reply_markup=markup)

# Обробка обраної теми користувачем


@bot.message_handler(func=lambda message: message.text in [messages["bulling"], messages["v1"],
                                                           messages["v2"], messages["Other"], messages["button_back"]])
def handle_topic(message):
    if message.text == messages["bulling"]:
        bot.send_message(message.chat.id, messages["bullying_prompt"])
        info_list.append(f'Тема звернення: {message.text}')
        bot.send_message(message.chat.id, messages["other_prompt_ans"])
        bot.register_next_step_handler(message, collect_description_data)

    elif message.text == messages["v1"]:
        bot.send_message(message.chat.id, messages["teacher_issues_prompt"])
        info_list.append(f'Тема звернення: {message.text}')
        bot.send_message(message.chat.id, messages["other_prompt_ans"])
        bot.register_next_step_handler(message, collect_description_data)

    elif message.text == messages["v2"]:
        bot.send_message(message.chat.id, messages["academic_integrity_prompt"])
        info_list.append(f'Тема звернення: {message.text}')
        bot.send_message(message.chat.id, messages["other_prompt_ans"])
        bot.register_next_step_handler(message, collect_description_data)

    elif message.text == messages["Other"]:
        bot.send_message(message.chat.id, messages["other_prompt"])
        info_list.append(f'Тема звернення: {message.text}')
        bot.send_message(message.chat.id, messages["other_prompt_ans"])
        bot.register_next_step_handler(message, collect_description_data)

    elif message.text == messages["button_back"]:
        handle_start(message)

# Збір опису проблеми


def collect_description_data(message):

    info_list.append(f'Опис проблеми: {message.text}')
    handle_problem_description(message)

# Збір додаткових даних


def collect_additional_data(message):
    additional_data = message.text
    info_list.append(f'Додаткова інформація: {additional_data}')
    bot.register_next_step_handler(message, handle_commands)

# Обробка опису проблеми та відображення кнопок управління


def handle_problem_description(message):
    if message.from_user.id not in anonym_mode:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add(types.KeyboardButton(messages["go_to_beginning"]), types.KeyboardButton(messages["add_description"]),
                   types.KeyboardButton(messages["end_dialog"]))
        bot.send_message(message.chat.id, messages["v3"], reply_markup=markup)
    else:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add(types.KeyboardButton(messages["go_to_beginning"]), types.KeyboardButton(messages["add_description"]),
                   types.KeyboardButton(messages["delete_dialog"]), types.KeyboardButton(messages["end_dialog"]))
        bot.send_message(message.chat.id, messages["v3"], reply_markup=markup)

# Обробка кнопок управління


@bot.message_handler(func=lambda message: True)
def handle_commands(message):
    if message.text == messages["go_to_beginning"]:
        start_message(message)
        info_list.clear()
    elif message.text == messages["add_description"]:
        bot.send_message(message.chat.id, messages["additional_details_prompt"])
        bot.register_next_step_handler(message, collect_additional_data)

        if message.from_user.id not in anonym_mode:
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            markup.add(types.KeyboardButton(messages["go_to_beginning"]),
                       types.KeyboardButton(messages["end_dialog"]))
        else:
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            markup.add(types.KeyboardButton(messages["go_to_beginning"]),
                       types.KeyboardButton(messages["delete_dialog"]),
                       types.KeyboardButton(messages["end_dialog"]))
        bot.send_message(message.chat.id, messages["v3"], reply_markup=markup)
    elif message.text == messages["delete_dialog"]:
        anonym_mode.discard(message.from_user.id)
        info_list.clear()
        bot.send_message(message.chat.id, messages["dialog_deleted"])
    elif message.text == messages["button_back"]:
        handle_topic(message)
    elif message.text == messages["end_dialog"]:
        # Виклик функції для відправлення листа
        current_date = date.today()
        current_date = f"\n{current_date}"
        info_list.append(current_date)
        info_data_email = "\n".join(info_list)
        send_email(info_data_email)
        bot.send_message(message.chat.id, messages["ending"])
        return

print("bot has been started")
bot.polling()
