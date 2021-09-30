#!/usr/bin/env python
# coding: utf-8

from create import engine, PersonDB, EventDB
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy import asc
from schedule_parser import Event
import logging
from datetime import datetime

# Connect logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


def session() -> Session:
    """The function of getting a connection to the db.

    :return: connected session to db
    :rtype: Session
    """

    return sessionmaker(bind=engine)()


def people_from_db(ssn: Session) -> dict:
    """The function of getting a dictionary of people from the people table in the db.
    Structure of the dictionary:
        key - person's db id
        value - the second dictionary
    Structure of the second dictionary:
        key - name of the characteristic
        value - value of the characteristic
    {
        id: {
            'first_name': str,
            'last_name': str,
            'chat_id': int
        }
    }

    :param ssn: connected session to db
    :type ssn: Session

    :return: dictionary of the people
    :rtype: dict
    """

    return {
        persondb.id: {
            'first_name': persondb.first_name,
            'last_name': persondb.last_name,
            'chat_id': persondb.tg_chat_id
        } for persondb in ssn.query(PersonDB)
    }


def events_from_db(first_name='', last_name='', all=False) -> list:
    """The function of getting a list of events from the schedule table in the db.

    :param first_name: the user's name
    :type first_name: str

    :param last_name: the user's surname
    :type last_name: str

    :param all: flag to get all people from the db
    :type all: bool

    :return: list of the Event objects
    :rtype: list[Event, ...]
    """

    events = []
    ssn = session()

    if last_name != '':  # get events for one person only

        if first_name == 'По фамилии':  # get only by surname
            persondb = ssn.query(PersonDB).filter_by(last_name=last_name).first()

        else:  # get by name and surname
            persondb = ssn.query(PersonDB).filter_by(last_name=last_name, first_name=first_name).first()

        if not persondb:
            return [None]

        events = [
            Event(
                name=persondb.first_name,
                surname=persondb.last_name,
                user_name=persondb.tg_username,
                action=eventdb.action,
                chat_id=persondb.tg_chat_id,
                start=eventdb.start,
                end=eventdb.end
            ) for eventdb in ssn.query(EventDB).filter_by(person_id=persondb.id).order_by(asc(EventDB.start))
        ]

    elif all:  # get all people

        data_event = list(
            {
                'person_id': eventdb.person_id,
                'action': eventdb.action,
                'start': eventdb.start,
                'end': eventdb.end
            } for eventdb in ssn.query(EventDB)
        )

        data_person = {
            persondb.id: {
                'first_name': persondb.first_name,
                'last_name': persondb.last_name,
                'chat_id': persondb.tg_chat_id
            } for persondb in ssn.query(PersonDB)
        }

        for event in data_event:
            new_event = Event(
                name=data_person[event['person_id']]['first_name'],
                surname=data_person[event['person_id']]['last_name'],
                chat_id=data_person[event['person_id']]['chat_id'],
                action=event['action'],
                start=event['start'],
                end=event['end']
            )
            events.append(new_event)

    return events


def events_to_db(new_events: list) -> dict:
    """The function of updating the schedule table in the database and
    getting a dictionary of messages about all changes in the schedule for each user id.
    Structure of the dictionary:
        key - chat id
        value - list of the changes
    Example of the element in the list:
        '09:00 - 09:00 Action'

    :param new_events: list of the Event objects
    :type new_events: list[Event, ...]

    :return: dictionary of messages for each user id
    :rtype: dict
    """

    messages = {}

    ssn = session()
    db_events = events_from_db(all=True)
    people = {
        persondb.tg_username: {
            'id': persondb.id,
            'current_action': persondb.current_action
        } for persondb in ssn.query(PersonDB)
    }

    for event in new_events:
        if f'{event.user_name}' not in people.keys():  # add new person to the db
            new_person = PersonDB(
                first_name=event.name,
                last_name=event.surname,
                tg_username=event.user_name,
                current_action=event.action
            )
            ssn.add(new_person)
            ssn.commit()
            people[f'{event.user_name}'] = {
                'id': new_person.id,
                'current_action': event.action
            }

        elif event.action != people[event.user_name]['current_action'] and abs(
                (event.start - datetime.now()).days * 24 * 60 + (event.start - datetime.now()).seconds / 60 - 60) < 10:

            person = ssn.query(PersonDB).filter_by(tg_username=event.user_name).first()
            if person.tg_chat_id not in messages.keys():
                messages[person.tg_chat_id] = []
            messages[person.tg_chat_id].append(f'Смена деятельности:\n'
                                               f'С {event.start} - {event.action}')

            person.current_action = event.action

            ssn.commit()

        if not db_events:  # if db is empty
            new_event_db = EventDB(
                person_id=people[f'{event.user_name}']['id'],
                action=event.action,
                start=event.start,
                end=event.end
            )
            ssn.add(new_event_db)

        else:  # update event from db
            eventdb = ssn.query(EventDB).filter_by(
                person_id=people[event.user_name]['id'],
                start=event.start,
            ).first()

            if event and eventdb and event.action != eventdb.action:
                eventdb.action = event.action  # change the action

                # add message to the person
                person_tg_chat_id = ssn.query(PersonDB.tg_chat_id).filter_by(id=eventdb.person_id).first()[0]
                if person_tg_chat_id not in messages.keys():
                    messages[person_tg_chat_id] = []
                messages[person_tg_chat_id].append(
                    f'{eventdb.start.strftime("%H:%M")} - {eventdb.end.strftime("%H:%M")} - {eventdb.action}'
                )

    ssn.commit()

    return messages
