#!/usr/bin/env python
# coding: utf-8

from bot.configBot import token, pin
import telebot
from telebot import types
from db import get, update
from datetime import datetime
from db.create import PersonDB, EventDB

bot = telebot.TeleBot(token)  # connection to the tg bot
logged_users = {}  # dictionary of users who correctly wrote the password


def name(message: types.Message) -> None:
    """The function of inviting the user to write his name.
    The next step is to invite to write his surname.

    :param message: the received message from telegram
    :type message: types.Message

    :return: nothing
    :rtype: None
    """
    first_name = bot.send_message(message.chat.id, 'Напиши свое имя')
    bot.register_next_step_handler(first_name, save_first_name)


def save_first_name(message: types.Message) -> None:
    """The function of inviting the user to write his surname.
    The next step is to save the received data to the database.

    :param message: the received message from telegram
    :type message: types.Message

    :return: nothing
    :rtype: None
    """
    first_name = message.text

    last_name = bot.send_message(message.chat.id, 'Напиши свою фамилию')
    bot.register_next_step_handler(last_name, save_last_name, first_name)


def save_last_name(message: types.Message, first_name: str) -> None:
    """The function of saving the received data to the database.

    :param message: the received message from telegram
    :type message: types.Message

    :param first_name: the received user's name
    :type first_name: str

    :return: nothing
    :rtype: None
    """
    last_name = message.text

    events = get.events_from_db(first_name, last_name)

    message_text = ''
    rows = []

    if events:
        for event in events:
            if event.start < datetime.now():
                rows.append(f'{event.start.strftime("%H:%M")} - {event.end.strftime("%H:%M")} {event.event_name}')

        message_text = '\n'.join(rows)

    if message_text:
        nrows = 70
        if len(rows) > nrows:
            i = 0
            message_text = '\n'.join(rows[i: i + nrows])
            while i < len(rows) + nrows and message_text:
                bot.send_message(message.chat.id, message_text)
                i += nrows
                message_text = '\n'.join(rows[i: i + nrows])
        else:
            bot.send_message(message.chat.id, message_text)
    else:
        message_text = 'Ивентов не найдено.'
        bot.send_message(message.chat.id, message_text)


@bot.message_handler(commands=['start'])
def hello_message(message: types.Message) -> None:
    """The function is the handler of the start command.
    The next step is to write a password.

    :param message: the received message from telegram
    :type message: types.Message

    :return: nothing
    :rtype: None
    """
    bot.send_message(message.chat.id, 'Привет!\nЯ рад видеть тебя на этом прекрасном мероприятии.')
    user = User(
        chat_id=message.chat.id,
        username=message.chat.username
    )
    user_name_msg = bot.send_message(message.chat.id, 'Введите свое имя:')
    bot.register_next_step_handler(user_name_msg, enter_name, user)


class User:

    def __init__(self, name='', surname='', chat_id=0, username=''):
        self.name = name
        self.surname = surname
        self.chat_id = chat_id
        self.username = username

    def __repr__(self):
        return f'<User(name="{self.name}", surname="{self.surname}", chat_id="{self.chat_id}", username="{self.username}")>'


def enter_name(message: types.Message, user: User) -> None:
    user.name = message.text
    user_surname_msg = bot.send_message(message.chat.id, 'Введите свою фамилию:')
    bot.register_next_step_handler(user_surname_msg, enter_surname, user)


def enter_surname(message: types.Message, user: User) -> None:
    user.surname = message.text
    session = get.session()
    persondb = session.query(PersonDB).filter_by(first_name=user.name, last_name=user.surname).first()
    if persondb:
        password_msg = bot.send_message(message.chat.id, 'Введите пароль:')
        bot.register_next_step_handler(password_msg, enter_pin, user)
    else:
        bot.send_message(user.chat_id, 'Неправильные данные, попробуйте заново: /start')


def enter_pin(message: types.Message, user: User) -> None:
    """The password check function.

    :param message: the received message from telegram
    :type message: types.Message

    :return: nothing
    :rtype: None
    """
    if message.text.lower() == pin:
        bot.send_message(message.chat.id, 'Введен правильный пароль. Доступ открыт!')
        logged_users[message.chat.first_name] = message.chat.id
        update.tg_chat_id(user.name, user.surname, user.chat_id)
        update.tg_username(user.name, user.surname, user.username)
        bot.send_message(message.chat.id, 'Нажмите /help, чтобы узнать о командах')
    else:
        bot.send_message(message.chat.id, 'Неверный пароль, попробуйте еще раз!')


@bot.message_handler(commands=['help'])
def help_command(message: types.Message) -> None:
    """The function is the handler of the help command.

    :param message: the received message from telegram
    :type message: types.Message

    :return: nothing
    :rtype: None
    """
    bot.send_message(
        message.chat.id,
        f'В нашем боте существуют такие команды:\n'
        f'/start — полностью начинает работу бота заново\n'
        f'/help — выводит команды, которые существуют в боте\n'
        f'/schedule - выводит ваше расписание'
    )


@bot.message_handler(commands=['schedule'])
def give_schedule(message):
    """The function is the handler of the schedule command.

    :param message: the received message from telegram
    :type message: types.Message

    :return: nothing
    :rtype: None
    """
    buttons = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)

    surname = types.KeyboardButton('Фамилии')
    name_and_surname = types.KeyboardButton('Фамилии и имени')

    buttons.add(surname, name_and_surname)

    bot.send_message(
        message.chat.id,
        'По этой команде вы можете получить свое расписание!\n'
        'Поиск по:',
        reply_markup=buttons
    )


@bot.message_handler(content_types=['text'])
def handler(message: types.Message) -> None:
    """The function is the handler of the text.
    React to the following phrases:
        'Фамилии' - starts the second step of obtaining information
        'Фамилии и имени' - starts the first step of obtaining information

    :param message: the received massage from telegram
    :type message: types.Message

    :return: nothing
    :rtype: None
    """
    if message.text == 'Фамилии':
        save_first_name(message)

    elif message.text == 'Фамилии и имени':
        name(message)

    else:
        bot.send_message(message.chat.id, 'Чет не то')


bot.polling()
