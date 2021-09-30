#!/usr/bin/env python
# coding: utf-8

from configDB import connect_path
from sqlalchemy import *
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime, timezone, timedelta
import logging

# Connect logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

try:
    engine = create_engine(connect_path, pool_size=1000)
    db = declarative_base()


    class PersonDB(db):
        """The object is a cell in the people table in the db.

        first_name - user's name
        last_name - user's surname
        tg_chat_id - user's tg chat id
        tg_username - user's tg tag

        """

        __tablename__ = 'people'

        id = Column(Integer, primary_key=True)
        first_name = Column(String)
        last_name = Column(String)
        tg_chat_id = Column(Integer)
        tg_username = Column(String, unique=True)
        current_action = Column(String)

        def __init__(self,
                     first_name='first_name',
                     last_name='last_name',
                     tg_chat_id=0,
                     tg_username='tg_username',
                     current_action='Сидит дома'
                     ):
            self.first_name = first_name
            self.last_name = last_name
            self.tg_chat_id = tg_chat_id
            self.tg_username = tg_username,
            self.current_action = current_action

        def __repr__(self):
            return f'<Person(name="{self.first_name}", surname="{self.last_name}", tg_username="{self.tg_username}", current_action="{self.current_action}")>'


    class EventDB(db):
        """The object is a cell in the schedule table in the db.

        person_id - person's id in the people table in the db who should do the event
        action - action to be taken by a person
        start - start date and time of the event
        end - end date and time of the event

        """

        __tablename__ = 'schedule'

        id = Column(Integer, primary_key=True)
        person_id = Column(Integer, ForeignKey(PersonDB.id))
        action = Column(String)
        start = Column(DateTime)
        end = Column(DateTime)

        def __init__(self,
                     person_id=0,
                     action='None',
                     start=datetime.strptime('0:00', '%H:%M').time(),
                     end=datetime.strptime('0:00', '%H:%M').time()
                     ):
            self.person_id = person_id
            self.action = action
            self.start = start
            self.end = end

        def __repr__(self):
            return f'<Event(person_id="{self.person_id}", action="{self.action}", start="{self.start}", end="{self.end}")>'


    db.metadata.create_all(engine)

except Exception as e:
    print(f'{datetime.now(timezone(timedelta(hours=3.0)))} - db.create - "{e}"')
