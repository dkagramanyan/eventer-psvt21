#!/usr/bin/env python
# coding: utf-8

from configBot import token
import telebot
from telebot import types
import get, update
from datetime import datetime
from threading import Thread
import logging
from create import PersonDB

# Connect logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

bot = telebot.TeleBot(token)  # connection to the tg bot

logged_users = set(
    persondb.tg_username for persondb in get.session().query(PersonDB).filter(PersonDB.tg_chat_id != 0).all()
)  # list of users who wrote to the bot and is the organizer


class User:
    """The object is the user.

    chat_id - user's tg chat id
    username - user's tg tag

    """

    def __init__(self,
                 chat_id=0,
                 username=''
                 ):
        self.chat_id = chat_id
        self.username = username

    def __repr__(self):
        return f'<User(chat_id="{self.chat_id}", username="{self.username}")>'

    def __eq__(self, other):
        return type(other) == User and self.chat_id == other.chat_id and self.username == other.username


@bot.message_handler(commands=['start'])
def start(message: types.Message) -> None:
    """The function is the handler of the start command.
    Checks if the user is the organizer.

    :param message: the received message from tg
    :type message: types.Message

    :return: nothing
    :rtype: None
    """

    try:
        if message.chat.username not in logged_users:
            if update.tg_chat_id(username=message.chat.username, chat_id=message.chat.id):
                logged_users.add(message.chat.username)

                bot.send_message(
                    chat_id=message.chat.id,
                    text='Авторизация прошла успешно.\n'
                         'Чтобы вывести доступные команды, напиши /help'
                )

            else:
                bot.send_message(message.chat.id, 'К сожалению, ты не организатор данного мероприятия.\n'
                                                  'Попробуй вновь написать команду /start.\n'
                                                  'Если произошла ошибка, напиши об этом руководству.')
        else:
            bot.send_message(
                chat_id=message.chat.id,
                text='Авторизация была произведена.\n'
                     'Чтобы вывести доступные команды, напиши /help'
            )

    except Exception as e1:  # the first exception
        try:
            bot.send_message(message.chat.id, 'Что-то пошло не так, напиши отвечающим за бота или руководству')
        except Exception as e2:  # the second exception
            print(f'{datetime.now()} - bot.main.start.exception2 - {e2}')

        print(f'{datetime.now()} - bot.main.start.exception1 - {e1}')


@bot.message_handler(commands=['help'])
def help_command(message: types.Message) -> None:
    """The function is the handler of the help command.

    :param message: the received message from tg
    :type message: types.Message

    :return: nothing
    :rtype: None
    """

    try:

        if message.chat.username in logged_users:
            text = '/myschedule - мое расписание\n' \
                   '/start - авторизоваться\n' \
                   '/schedule - чужое расписание\n' \
                   '/help - имеющиеся команды'

        else:
            text = 'К сожалению, ты не организатор данного мероприятия.\nПопробуй вновь написать команду /start.\nЕсли произошла ошибка, напиши об этом руководству.'

        bot.send_message(
            chat_id=message.chat.id,
            text=text
        )

    except Exception as e:
        print(f'{datetime.now()} - bot.main.help - {e}')


@bot.message_handler(commands=['myschedule'])
def my_schedule(message: types.Message) -> None:
    """The function is the handler of the my schedule command.

    :param message: the received message from tg
    :type message: types.Message

    :return: nothing
    :rtype: None
    """
    try:
        if message.chat.username in logged_users:
            person = get.person(username=message.chat.username)
            send_schedule(message=message, my=True, first_name=person['first_name'], last_name=person['last_name'])

        else:
            bot.send_message(
                chat_id=message.chat.id,
                text='К сожалению, ты не организатор данного мероприятия.\n'
                     'Попробуй вновь написать команду /start.\n'
                     'Если произошла ошибка, напиши об этом руководству.'
            )

    except Exception as e:
        print(f'{datetime.now()} - bot.main.my_schedule - {e}')


@bot.message_handler(commands=['schedule'])
def choice_way_to_to_get_schedule(message: types.Message) -> None:
    """The function is the handler of the schedule command.

    :param message: the received message from telegram
    :type message: types.Message

    :return: nothing
    :rtype: None
    """

    try:
        if message.chat.username in logged_users:
            buttons = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)

            surname = types.KeyboardButton('По фамилии')
            name_and_surname = types.KeyboardButton('По имени и фамилии')

            buttons.add(surname, name_and_surname)

            bot.send_message(
                chat_id=message.chat.id,
                text='По этой команде вы можете получить расписание!\n'
                     'Поиск по фамилии или по имени и фамилии?',
                reply_markup=buttons
            )

        else:
            bot.send_message(
                chat_id=message.chat.id,
                text='К сожалению, ты не организатор данного мероприятия.\n'
                     'Попробуй вновь написать команду /start.\n'
                     'Если произошла ошибка, напиши об этом руководству.'
            )

    except Exception as e:
        print(f'{datetime.now()} - bot.main.schedule - {e}')


@bot.message_handler(content_types=['text'])
def handler(message: types.Message) -> None:
    """The function is the handler of the text.
    React to the following phrases:
        'По фамилии' - invites to write the organizer's surname
        'По имени и фамилии' - invites to write the organizer's name
    Also react to any other phrases - calls the help function.

    :param message: the received massage from telegram
    :type message: types.Message

    :return: nothing
    :rtype: None
    """

    if message.chat.username in logged_users:

        if message.text == 'По фамилии':
            invite_write_surname(message)

        elif message.text == 'По имени и фамилии':
            invite_write_name(message)

        else:
            help_command(message=message)
    else:
        bot.send_message(
            chat_id=message.chat.id,
            text='К сожалению, ты не организатор данного мероприятия.\n'
                 'Попробуй вновь написать команду /start.\n'
                 'Если произошла ошибка, напиши об этом руководству.'
        )


def invite_write_name(message: types.Message) -> None:
    """The function of inviting the user to write his name.
    The next step is to invite to write his surname.

    :param message: the received message from telegram
    :type message: types.Message

    :return: nothing
    :rtype: None
    """

    try:
        first_name = bot.send_message(message.chat.id, 'Напиши имя')
        bot.register_next_step_handler(first_name, invite_write_surname)

    except Exception as e:
        print(f'{datetime.now()} - bot.main.invite_write_name - {e}')


def invite_write_surname(message: types.Message) -> None:
    """The function of inviting the user to write his surname.
    The next step is to send the schedule from the database by received data.

    :param message: the received message from telegram
    :type message: types.Message

    :return: nothing
    :rtype: None
    """

    try:
        first_name = message.text  # user's name or 'По фамилии'

        last_name = bot.send_message(message.chat.id, 'Напиши фамилию')
        bot.register_next_step_handler(last_name, send_schedule, first_name)

    except Exception as e:
        print(f'{datetime.now()} - bot.main.invite_write_surname - {e}')


def send_schedule(message: types.Message, first_name: str, my=False, last_name='') -> None:
    """The function of sending the schedule from the db.

    :param message: the received message from telegram
    :type message: types.Message

    :param first_name: the received user's name
    :type first_name: str

    :param my: flag showing whose schedule the user requested
    :type my: bool

    :param last_name: the received user's surname
    :type last_name: str

    :return: nothing
    :rtype: None
    """

    try:
        if not my:
            last_name = message.text

        events = get.events_from_db(first_name, last_name)

        message_text = ''
        rows = []

        if events:  # create rows of events by list of events
            if not events[0]:
                bot.send_message(
                    chat_id=message.chat.id,
                    text='Пользователь не найден'
                )
                return

            current_action = events[0].action
            current_start = events[0].start
            current_end = events[0].end

            for event in events[1:]:
                if current_action == event.action:
                    current_end = event.end

                else:
                    rows.append(
                        f'{current_start.strftime("%H:%M")} - {current_end.strftime("%H:%M")} - {current_action}')
                    current_action = event.action
                    current_start = event.start
                    current_end = event.end

            rows.append(f'{current_start.strftime("%H:%M")} - ... - {current_action}')

            message_text = '\n'.join(rows)

        if message_text:  # create and send messages by rows of events
            nrows = 70
            if len(rows) > nrows:  # if the message length is too long
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

    except Exception as e:
        print(f'{datetime.now()} - bot.main.send_schedule - {e}')


def main() -> None:
    """The main function.
    Launches bot and parsing.

    :return: nothing
    :rtype: None
    """

    bot_thread = Thread(target=bot.polling)
    bot_thread.start()
    print(f'{datetime.now()} - bot.main - bot launched successfully')

    parser = Thread(target=update.database, args=(bot,))
    parser.start()
    print(f'{datetime.now()} - bot.main - parser launched successfully')


main()
