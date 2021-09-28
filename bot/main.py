#!/usr/bin/env python
# coding: utf-8

from bot.configBot import token
import telebot
from telebot import types
from db import get, update
from datetime import datetime
from threading import Thread


bot = telebot.TeleBot(token)  # connection to the tg bot
logged_users = []  # dictionary of users who correctly wrote the password


class User:
    def __init__(self, chat_id=0, username=''):
        self.chat_id = chat_id
        self.username = username

    def __repr__(self):
        return f'<User(chat_id="{self.chat_id}", username="{self.username}")>'


@bot.message_handler(commands=['start'])
def start(message: types.Message) -> None:
    """The function is the handler of the start command.
    The next step is to write a password.

    :param message: the received message from telegram
    :type message: types.Message

    :return: nothing
    :rtype: None
    """
    user = User(
        chat_id=message.chat.id,
        username=message.chat.username
    )

    try:
        update.tg_chat_id(user.username, user.chat_id)
        logged_users.append(user)
        bot.send_message(
            chat_id=message.chat.id,
            text='Авторизация прошла успешно.\n'
                 'Чтобы вывести доступные команды, напиши /help')

    except Exception as e:
        bot.send_message(message.chat.id, 'Что-то пошло не так, напиши отвечающим за бота или руководству')
        print(f'{datetime.now()} - bot.main.start - {e}')


@bot.message_handler(commands=['help'])
def help_command(message: types.Message) -> None:
    """The function is the handler of the help command.

    :param message: the received message from telegram
    :type message: types.Message

    :return: nothing
    :rtype: None
    """
    bot.send_message(
        chat_id=message.chat.id,
        text=f'/start — полностью начинает работу бота заново\n'
        f'/help — выводит команды, которые существуют в боте\n'
        f'/schedule - выводит ваше расписание'
    )


@bot.message_handler(commands=['schedule'])
def choice_way_to_to_get_schedule(message):
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
        invite_write_surname(message)

    elif message.text == 'Фамилии и имени':
        invite_write_name(message)

    else:
        bot.send_message(message.chat.id, 'Чет не то')


def main():
    bot_thread = Thread(target=bot.polling)
    bot_thread.start()

    parser = Thread(target=update.database, args=(bot,))
    parser.start()


def invite_write_name(message: types.Message) -> None:
    """The function of inviting the user to write his name.
    The next step is to invite to write his surname.

    :param message: the received message from telegram
    :type message: types.Message

    :return: nothing
    :rtype: None
    """
    first_name = bot.send_message(message.chat.id, 'Напиши свое имя')
    bot.register_next_step_handler(first_name, invite_write_surname)


def invite_write_surname(message: types.Message) -> None:
    """The function of inviting the user to write his surname.
    The next step is to send the schedule from the database by received data.

    :param message: the received message from telegram
    :type message: types.Message

    :return: nothing
    :rtype: None
    """
    first_name = message.text

    last_name = bot.send_message(message.chat.id, 'Напиши свою фамилию')
    bot.register_next_step_handler(last_name, send_schedule, first_name)


def send_schedule(message: types.Message, first_name: str) -> None:
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


main()
