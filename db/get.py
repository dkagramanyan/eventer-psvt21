#!/usr/bin/env python
# coding: utf-8

from parsers.schedule_parser import parser
from db.create import engine, PersonDB, EventDB
from sqlalchemy.orm import sessionmaker, Session
from parsers.schedule_parser import Event


def session() -> Session:
    ssn = sessionmaker(bind=engine)()
    return ssn


def people_from_db(ssn: Session, all=False) -> dict:
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
            events = [Event(name=persondb.first_name, surname=persondb.last_name, user_name=persondb.tg_username,
                            event_name=eventdb.event_name, chat_id=persondb.tg_chat_id, start=eventdb.start,
                            end=eventdb.end) for eventdb in ssn.query(EventDB).filter_by(person_id=persondb.id)]

        else:
            persondb = ssn.query(PersonDB).filter_by(last_name=last_name, first_name=first_name).first()
            events = [Event(name=persondb.first_name, surname=persondb.last_name, user_name=persondb.tg_username,
                            event_name=eventdb.event_name, chat_id=persondb.tg_chat_id, start=eventdb.start,
                            end=eventdb.end) for eventdb in ssn.query(EventDB).filter_by(person_id=persondb.id)]

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


def schedule_by_name_and_surname(connection: Session, first_name: str, last_name: str) -> str:
    """The function of getting the text of the message to send to the user by his name and surname.

    :param connection: connection object
    :type connection: psy._psycopg.connection

    :param first_name: the user's name
    :type first_name: str

    :param last_name: the user's surname
    :type last_name: str

    :return: message text with information about the user's events
    :rtype: str
    """
    cursor = connection.cursor()

    cursor.execute("SELECT id "
                   "FROM plat_people_main "
                   "WHERE similarity(first_name, %s) > 0.5 AND similarity(middle_name, %s) > 0.5",
                   (first_name, last_name))
    person_id = cursor.fetchone()[0]

    cursor.execute("SELECT name, time_from, time_to "
                   "FROM plat_people_main as ppm "
                   "JOIN plat_timetable_main as ptm OgitN ppm.id = ptm.org_id "
                   "JOIN plat_timetable_cases as ptc ON ptm.event_id = ptc.id "
                   "WHERE org_id = %s", (person_id,))
    schedule = cursor.fetchall()

    message_text = f'Название: {schedule[0][0]}\n' \
        f'Время начала: {str(schedule[0][1])[:2]}:{str(schedule[0][1])[2:]}\n' \
        f'Время конца: {str(schedule[0][2])[:2]}:{str(schedule[0][2])[2:]}'

    return message_text


def schedule_by_surname(connection: Session, last_name: str) -> str:
    """The function of getting the text of the message to send to the user only by his surname.

    :param connection: connection object
    :type connection: psy._psycopg.connection

    :param last_name: the user's surname
    :type last_name: str

    :return: message text with information about the user's events
    :rtype: str
    """
    cursor = connection.cursor()

    cursor.execute("SELECT id "
                   "FROM plat_people_main "
                   "WHERE similarity(middle_name, %s) > 0.5",
                   (last_name,))
    person_id = cursor.fetchone()[0]

    cursor.execute("SELECT name, time_from, time_to "
                   "FROM plat_people_main as ppm "
                   "JOIN plat_timetable_main as ptm ON ppm.id = ptm.org_id "
                   "JOIN plat_timetable_cases as ptc ON ptm.event_id = ptc.id "
                   "WHERE org_id = %s", (person_id,))
    schedule = cursor.fetchall()

    message_text = f'Название: {schedule[0][0]}\n' \
        f'Время начала: {str(schedule[0][1])[:2]}:{str(schedule[0][1])[2:]}\n' \
        f'Время конца: {str(schedule[0][2])[:2]}:{str(schedule[0][2])[2:]}'

    return message_text


def events_to_db(events_from_google: list) -> None:
    ssn = session()
    people = {persondb.first_name + '_' + persondb.last_name: persondb.id for persondb in ssn.query(PersonDB)}
    db_events = events_from_db(all=True)

    for event in events_from_google:
        if event not in db_events:
            if f'{event.name}_{event.surname}' not in people.keys():
                new_person = PersonDB(
                    first_name=event.name,
                    last_name=event.surname
                )
                ssn.add(new_person)
                ssn.commit()
                people[f'{event.name}_{event.surname}'] = new_person.id

            new_event_db = EventDB(
                person_id=people[f'{event.name}_{event.surname}'],
                event_name=event.event_name,
                start=event.start,
                end=event.end
            )
            ssn.add(new_event_db)
            db_events.append(event)

    ssn.commit()
