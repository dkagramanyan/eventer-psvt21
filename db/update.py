#!/usr/bin/env python
# coding: utf-8

from db import get
from db.create import PersonDB
from parsers.schedule_parser import parser
import time
from telebot import TeleBot


def database(bot: TeleBot) -> None:
    while True:
        new_events = get.events_to_db(parser())

        for chat_id in new_events.keys():
            if chat_id:
                bot.send_message(
                    chat_id=chat_id,
                    text='Расписание изменено:\n' + '\n'.join(new_events[chat_id])
                )
                time.sleep(0.2)

        time.sleep(20)


def tg_chat_id(username: str, chat_id: int) -> None:
    session = get.session()
    persondb = session.query(PersonDB).filter_by(tg_username=username).first()
    persondb.tg_chat_id = chat_id
    session.commit()
