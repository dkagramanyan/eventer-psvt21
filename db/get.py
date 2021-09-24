#!/usr/bin/env python
# coding: utf-8

from db.configDB import db
import psycopg2 as psy
from psycopg2 import OperationalError
from psycopg2 import extensions
from datetime import datetime, timezone, timedelta


def connection() -> extensions.connection:
    """The function to getting the connection to the database by information from the configDB file.

    :return: connection object
    :rtype: psy._psycopg.connection
    """
    try:
        conn = psy.connect(
            user=db['user'],
            password=db['password'],
            host=db['host'],
            port=db['port'],
            database=db['database']
        )
        return conn

    except OperationalError as error:
        print(f'{datetime.now(timezone(timedelta(hours=3.0)))} - '
              f'db.get.connection() - '
              f'Ошибка при работе с PostgreSQL "{error}"')


def schedule_by_name_and_surname(connection: extensions.connection, first_name: str, last_name: str) -> str:
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


def schedule_by_surname(connection: extensions.connection, last_name: str) -> str:
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
