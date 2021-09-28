#!/usr/bin/env python
# coding: utf-8

from db import get
from db.create import PersonDB
from parsers.schedule_parser import parser
import time
from telebot import TeleBot
from datetime import datetime


def database(bot: TeleBot) -> None:
    """The function of updating the db.

    :param bot: the bot object
    :type bot: TeleBot

    :return: nothing
    :rtype: None
    """

    while True:

        try:
            new_events = get.events_to_db(parser())

            for chat_id in new_events.keys():
                if chat_id:
                    bot.send_message(
                        chat_id=chat_id,
                        text='Расписание изменено:\n' + '\n'.join(new_events[chat_id])
                    )
                    time.sleep(0.2)

            time.sleep(30)

        except Exception as e:
            print(f'{datetime.now()} - db.update.database - {e}')


def tg_chat_id(username: str, chat_id: int) -> None:
    """The function of updating the person's tg chat in the db.
    The function is authorization.

    :param username: the user's tg username
    :type username: str

    :param chat_id: the user's tg chat id
    :type chat_id: int

    :return: nothing
    :rtype: None
    """

    session = get.session()
    persondb = session.query(PersonDB).filter_by(tg_username=username).first()

    persondb.tg_chat_id = chat_id

    session.commit()
