#!/usr/bin/env python
# coding: utf-8

from db.configDB import connect_path
from sqlalchemy import *
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime, timezone, timedelta

try:
    engine = create_engine(connect_path)
    db = declarative_base()


    class Person(db):
        __tablename__ = 'people'

        id = Column(Integer, primary_key=True)
        first_name = Column(String)
        last_name = Column(String)
        tg_chat_id = Column(Integer)
        tg_username = Column(String)

        def __init__(self, first_name, last_name, tg_chat_id, tg_username):
            self.first_name = first_name
            self.last_name = last_name
            self.tg_chat_id = tg_chat_id
            self.tg_username = tg_username

        def __repr__(self):
            return f'<Person(name="{self.first_name}", surname="{self.last_name}", tg_username="{self.tg_username}")>'


    class Event(db):
        __tablename__ = 'schedule'

        id = Column(Integer, primary_key=True)
        person_id = Column(Integer, ForeignKey(Person.id))
        event_name = Column(String)
        start = Column(DateTime)
        end = Column(DateTime)

        def __init__(self, person_id, event_name, start, end):
            self.person_id = person_id
            self.event_name = event_name
            self.start = start
            self.end = end

        def __repr__(self):
            return f'<Event(person_id="{self.person_id}", event_name="{self.event_name}", start="{self.start}", end="{self.end}")>'


    db.metadata.create_all(engine)

except Exception as e:
    print(f'{datetime.now(timezone(timedelta(hours=3.0)))} - db.get.database() - "{e}"')
