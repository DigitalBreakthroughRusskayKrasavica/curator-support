import telebot
from main_functions import get_answer

token = '7194921152:AAFju-3aWuwSsqHkGl5lgeEMWu0jJgS62io'
telebot = telebot.TeleBot(token)


@telebot.message_handler(commands=['start'])
def start_message(message):
    telebot.send_message(
        message.chat.id,
        "Добро пожаловать в бот для поддержки студентов!"
    )


@telebot.message_handler(content_types='text')
def message_reply(message):
    print(message)
    answer = get_answer(message.text)
    telebot.send_message(message.chat.id, answer)


telebot.infinity_polling()
