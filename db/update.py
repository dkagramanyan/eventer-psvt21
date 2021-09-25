#!/usr/bin/env python
# coding: utf-8

from db import get
from db.create import PersonDB, EventDB
from parsers.schedule_parser import parser


# get.events_to_db(parser())


def tg_chat_id(name: str, surname: str, chat_id: int) -> None:
    session = get.session()
    persondb = session.query(PersonDB).filter_by(first_name=name, last_name=surname).first()
    persondb.tg_chat_id = chat_id
    session.commit()


def tg_username(name: str, surname: str, user_name: str):
    session = get.session()
    persondb = session.query(PersonDB).filter_by(first_name=name, last_name=surname).first()
    persondb.tg_username = user_name
    session.commit()
