#!/usr/bin/env python
# coding: utf-8

import get
from create import PersonDB
from schedule_parser import parser
import time
from telebot import TeleBot
from datetime import datetime
import logging

# Connect logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


def database(bot: TeleBot) -> None:
    """The function of updating the db.

    :param bot: the bot object
    :type bot: TeleBot

    :return: nothing
    :rtype: None
    """

    while True:
        # print(f'INFO: {datetime.now()} - db.update.database - db is updating')

        try:
            new_events = get.events_to_db(parser())

            for chat_id in new_events.keys():
                if chat_id:
                    messages = new_events[chat_id]
                    message = ''
                    for new_event in messages:
                        if 'Смена деятельности: ' in new_event:
                            bot.send_message(
                                chat_id=chat_id,
                                text=new_event
                            )
                        else:
                            message += new_event + '\n'

                    if message:
                        bot.send_message(
                            chat_id=chat_id,
                            text='Расписание изменено:\n' + message
                        )

                    time.sleep(0.2)

            if new_events:
                print(f'INFO: {datetime.now()} - db.update.database - db was update')

            # else:
            # print(f'INFO: {datetime.now()} - db.update.database - completion db update')

            time.sleep(60)

        except Exception as e:
            print(f'{datetime.now()} - db.update.database - {e}')


def tg_chat_id(username: str, chat_id: int) -> PersonDB:
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

    if not persondb:
        return persondb

    persondb.tg_chat_id = chat_id

    session.commit()

    return persondb
