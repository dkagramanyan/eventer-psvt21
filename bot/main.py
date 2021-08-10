from config import token
from config import database as db
from config import pin
from config import logged_users
import telebot
import psycopg2 as psy
from psycopg2 import Error

bot = telebot.TeleBot(token)


@bot.message_handler(commands=['start'])
def hello_message(message):
    bot.send_message(message.chat.id, 'Привет!\nЯ рад видеть тебя на этом прекрасном мероприятии')
    pin_code = bot.send_message(message.chat.id, 'Введите пароль!')
    bot.register_next_step_handler(pin_code, try_pin)


@bot.message_handler(content_types=['text'])
def try_pin(message):
    if message.text.lower() == pin:
        logged_users[message.chat.id] = 'yes'
        bot.send_message(message.chat.id, 'Введен правильный пароль. Доступ открыт!')
        first_name = bot.send_message(message.chat.id, 'Напиши свое имя')
        bot.register_next_step_handler(first_name, save_first_name)
    else:
        logged_users[message.chat.id] = 'no'
        bot.send_message(message.chat.id, 'Неверный пароль, попробуйте еще раз!')


def save_first_name(message):
    first_name = message.text
    last_name = bot.send_message(message.chat.id, 'Напиши свою фамилию')
    bot.register_next_step_handler(last_name, save_last_name, first_name)


def save_last_name(message, first_name):
    last_name = message.text
    give_id(message, first_name, last_name)


def give_id(message, first_name, last_name):
    """
    The function returns the user id depending on the first name and last name
    """
    try:
        connection = psy.connect(user=db['user'],
                                 password=db['password'],
                                 host=db['host'],
                                 port=db['port'],
                                 database=db['database'])
        cursor = connection.cursor()
        cursor.execute("SELECT version();")
        print("Вы подключены к -", cursor.fetchone(), "\n")

        cursor.execute("SELECT id FROM plat_people_main WHERE first_name = %s AND middle_name = %s",
                       (first_name, last_name))

        bot.send_message(message.chat.id, f'Вот твой id: {cursor.fetchall()[0][0]}')
    except Error as error:
        print('Ошибка при работе с PostgreSQL', error)
    finally:
        if connection:
            connection.close()
            cursor.close()


bot.polling()
