#!/usr/bin/env python
# coding: utf-8

from __future__ import print_function
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
import logging
from configParser import ggl_token_file_name, credentials_file_name, spreadsheet_id, ranges
import os
from datetime import datetime, timezone, timedelta

# Connect logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


def get_creds() -> Credentials:
    """The function of creating credentials in order to connect to Google Drive files.

    :return: credentials
    :rtype: Credentials
    """

    SCOPES = ['https://www.googleapis.com/auth/drive.metadata.readonly', 'https://www.googleapis.com/auth/drive']

    # try to read the credentials from the token file
    creds = None
    if os.path.exists(ggl_token_file_name):
        creds = Credentials.from_authorized_user_file(ggl_token_file_name, SCOPES)

    # create or update credentials and token file
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())

        else:
            flow = InstalledAppFlow.from_client_secrets_file(credentials_file_name, SCOPES)
            creds = flow.run_local_server(port=0)

        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    return creds


def get_row_data(spreadsheet_id: str, ranges: str) -> list:
    """The function of getting an unformatted, full information rows from a spreadsheet by table id and read ranges.

    :param spreadsheet_id: spreadsheet id
    :type spreadsheet_id: str

    :param ranges: range of columns as 'A:Z'
    :type ranges: str

    :return: data rows with unformatted full information from a spreadsheet
    :rtype: list[...]
    """

    rowData = []

    credentials = get_creds()

    try:
        service = build('sheets', 'v4', credentials=credentials)

        request = service.spreadsheets().get(
            spreadsheetId=spreadsheet_id,
            ranges=ranges,
            includeGridData=True
        )
        response = request.execute()
        rowData = response['sheets'][0]['data'][0]['rowData']

    except Exception as e:
        print(f'{datetime.now(timezone(timedelta(hours=3.0)))} - parsers.schedule_parser.get_row_data - {e}')

    return rowData


def get_table(spreadsheet_id: str, ranges: str) -> list:
    """The function of getting data from a spreadsheet in a readable, unformatted form.

    :param spreadsheet_id: spreadsheet id
    :type spreadsheet_id: str

    :param ranges: range of columns as 'A:Z'
    :type ranges: str

    :return: list of columns with formatted values or None
    :rtype: list[[str | None, ...], ...]
    """

    table = []

    row_data = get_row_data(
        spreadsheet_id=spreadsheet_id,
        ranges=ranges
    )

    for row in row_data:
        try:
            # filling the table
            for i, value in enumerate(row['values']):
                if len(table) <= i:
                    table.append([])

                if value and 'formattedValue' in value.keys():
                    formatted_value = value['formattedValue']
                else:
                    if i == 0:
                        continue

                    else:
                        formatted_value = 'Отдых'

                table[i].append(formatted_value)

        except Exception as e:
            print(f'{datetime.now(timezone(timedelta(hours=3.0)))} - parsers.schedule_parser.get_table - {e}')

    return table


class Event:
    """The event object.

    name - person's name
    surname - the person's surname
    user_name - the person's telegram tag
    chat_id - the person's telegram chat id
    action - place or action that the person should do
    start - start time of the event
    end - end time of the event

    """

    def __init__(self,
                 name='name',
                 surname='surname',
                 user_name='user_name',
                 action='action',
                 chat_id=0,
                 start=datetime.strptime('0:00', '%H:%M'),
                 end=datetime.strptime('0:00', '%H:%M')
                 ):
        self.name = name
        self.surname = surname
        self.user_name = user_name
        self.chat_id = chat_id
        self.action = action
        self.start = start
        self.end = end

    def __repr__(self):
        return f'<Event(name="{self.name}", surname="{self.surname}", user_name="{self.user_name}", chat_id="{self.chat_id}", start={self.start}", end="{self.end}", action="{self.action}")>'

    def __eq__(self, other):
        try:
            eq_name = self.name == other.name
            eq_surname = self.surname == other.surname
            eq_action = self.action == other.action
            eq_start = self.start == other.start
            eq_end = self.end == other.end
            return eq_name and eq_surname and eq_action and eq_start and eq_end

        except Exception as e:
            print(f'{datetime.now(timezone(timedelta(hours=3.0)))} - parsers.schedule_parser.Event - {e}')


def parser() -> list:
    """The function of creating a list of events from the parsed table.

    :return: list of the Event objects
    :rtype: list[Event, ...]
    """

    evnts = []

    try:
        table = get_table(spreadsheet_id, ranges)

        names = table[0][1:]
        tg_usernames = table[1][1:]
        events = [table[i][1:] for i in range(6, 69)]
        timings = [table[i][0] for i in range(6, 69)] + ['00:00']

        for person, name in enumerate(names):
            date = '2021-10-02'
            name = name.split()

            if len(name) == 1:
                print(f'{datetime.now()} - parsers.schedule_parser.parser - name is {name} and it\'s wrong')
                continue

            surname, name = name[0], name[1]
            tg_username = tg_usernames[person]

            # filling the evnts
            for number, action in enumerate(events):

                if timings[number] == '0:00':
                    date = datetime.strptime(date, '%Y-%m-%d')
                    date += timedelta(days=1)
                    date = date.strftime('%Y-%m-%d')

                time_start = datetime.strptime(date + ' ' + timings[number], '%Y-%m-%d %H:%M')
                time_end = datetime.strptime(date + ' ' + timings[number + 1], '%Y-%m-%d %H:%M')

                event = Event(
                    name=name,
                    surname=surname,
                    user_name=tg_username,
                    action=action[person],
                    start=time_start,
                    end=time_end
                )

                evnts.append(event)

    except Exception as e:
        print(f'{datetime.now(timezone(timedelta(hours=3.0)))} - parsers.schedule_parser.parser - {e}')

    return evnts
