#!/usr/bin/env python
# coding: utf-8

from parsers.schedule_parser import parser
from db.create import engine, PersonDB, EventDB
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy import desc
from parsers.schedule_parser import Event


def session() -> Session:
    ssn = sessionmaker(bind=engine)()
    return ssn


def people_from_db(ssn: Session) -> dict:
    return {
    persondb.id: {'first_name': persondb.first_name, 'last_name': persondb.last_name, 'chat_id': persondb.tg_chat_id}
    for persondb in ssn.query(PersonDB)}


def events_from_db(first_name='', last_name='', all=False) -> list:
    """

    :param first_name: the user's name
    :type first_name: str

    :param last_name: the user's surname
    :type last_name: str

    :return: set of the Event objects
    :rtype: set[Event, ...]
    """
    events = []
    ssn = session()
    if last_name != '':
        if first_name == 'Фамилии':
            persondb = ssn.query(PersonDB).filter_by(last_name=last_name).first()
        else:
            persondb = ssn.query(PersonDB).filter_by(last_name=last_name, first_name=first_name).first()

        events = [Event(name=persondb.first_name, surname=persondb.last_name, user_name=persondb.tg_username,
                        event_name=eventdb.event_name, chat_id=persondb.tg_chat_id, start=eventdb.start,
                        end=eventdb.end) for eventdb in
                  ssn.query(EventDB).filter_by(person_id=persondb.id).order_by(desc(EventDB.start))[::-1]]

    elif all:

        data_event = (list({'person_id': eventdb.person_id, 'event_name': eventdb.event_name, 'start': eventdb.start,
                            'end': eventdb.end} for eventdb in ssn.query(EventDB)))
        data_person = {persondb.id: {'first_name': persondb.first_name, 'last_name': persondb.last_name,
                                     'chat_id': persondb.tg_chat_id} for persondb in ssn.query(PersonDB)}

        for event in data_event:
            new_event = Event(
                name=data_person[event['person_id']]['first_name'],
                surname=data_person[event['person_id']]['last_name'],
                chat_id=data_person[event['person_id']]['chat_id'],
                event_name=event['event_name'],
                start=event['start'],
                end=event['end']
            )
            events.append(new_event)

    return events


def events_to_db(new_events: list) -> dict:
    ssn = session()
    people = {persondb.tg_username: persondb.id for persondb in ssn.query(PersonDB)}
    db_events = events_from_db(all=True)
    messages = {}

    for event in new_events:
        if f'{event.user_name}' not in people.keys():
            new_person = PersonDB(
                first_name=event.name,
                last_name=event.surname,
                tg_username=event.user_name
            )
            ssn.add(new_person)
            ssn.commit()
            people[f'{event.user_name}'] = new_person.id
        ssn.commit()

        if not db_events:
            new_event_db = EventDB(
                person_id=people[f'{event.user_name}'],
                event_name=event.event_name,
                start=event.start,
                end=event.end
            )
            ssn.add(new_event_db)

        else:
            eventdb = ssn.query(EventDB).filter_by(
                person_id=people[event.user_name],
                start=event.start,
            ).first()

            if event.event_name != eventdb.event_name:
                eventdb.event_name = event.event_name
                person_tg_chat_id = ssn.query(PersonDB.tg_chat_id).filter_by(id=eventdb.person_id).first()[0]
                if person_tg_chat_id not in messages.keys():
                    messages[person_tg_chat_id] = []
                messages[person_tg_chat_id].append(
                    f'{eventdb.start.strftime("%H:%M")} - {eventdb.end.strftime("%H:%M")} {eventdb.event_name}')

    ssn.commit()

    return messages
