#!/usr/bin/env python
# coding: utf-8

from __future__ import print_function
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
import logging
from parsers.configParser import ggl_token_file_name, credentials_file_name, spreadsheet_id, number_orginizers, ranges
import os
from datetime import datetime, timezone, timedelta

# Connect logging
logging.basicConfig(
    filename='parser.log',
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.WARNING
)
logger = logging.getLogger(__name__)


def get_creds() -> Credentials:
    """The function to create credentials in order to connect to Google Drive files.

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
    """The function to get unformatted, full information rows from a spreadsheet by table id and read ranges.

    :param spreadsheet_id: spreadsheet id
    :type spreadsheet_id: str

    :param ranges: range of columns as 'A:Z'
    :type ranges: str

    :return: data rows with unformatted full information from a spreadsheet
    :rtype: list[...]
    """
    credentials = get_creds()

    service = build('sheets', 'v4', credentials=credentials)

    request = service.spreadsheets().get(
        spreadsheetId=spreadsheet_id,
        ranges=ranges,
        includeGridData=True
    )
    response = request.execute()

    return response['sheets'][0]['data'][0]['rowData']


def get_table(spreadsheet: str, ranges: str) -> list:
    """The function to get data from a spreadsheet in a readable, unformatted form.

    :param spreadsheet: spreadsheet id
    :type spreadsheet: str

    :return: list of columns with formatted values or None
    :rtype: list[[str | None, ...], ...]
    """
    table = []

    row_data = get_row_data(
        spreadsheet_id=spreadsheet,
        ranges=ranges
    )

    for row in row_data[:number_orginizers + 1]:
        try:
            # filling the table
            for i, value in enumerate(row['values']):
                if len(table) <= i:
                    table.append([])

                if value and 'formattedValue' in value.keys():
                    formatted_value = value['formattedValue']
                else:
                    formatted_value = None

                table[i].append(formatted_value)

        except Exception as e:
            with open('../parsers/parser.log', 'a') as f:
                print(f'{datetime.now(timezone(timedelta(hours=3.0)))} - parsers:schedule_parser - {e}', file=f)

    return table


class Event:
    """The event object.

    name - person's name
    surname - the person's surname
    user_name - the person's telegram tag
    chat_id - the person's telegram chat id
    event_name - place or action that the person should do
    start - start time of the event
    end - end time of the event

    """

    def __init__(self,
                 name='name',
                 surname='surname',
                 user_name='user_name',
                 event_name='event_name',
                 chat_id=0,
                 start=datetime.strptime('0:00', '%H:%M').time(),
                 end=datetime.strptime('0:00', '%H:%M').time()
                 ):
        self.name = name
        self.surname = surname
        self.user_name = user_name
        self.chat_id = chat_id
        self.event_name = event_name
        self.start = start
        self.end = end

    def __repr__(self):
        return f'Event<{self.surname} {self.name} (@{self.user_name} - {self.chat_id}): {self.start} - {self.end} {self.event_name}>'


def parser() -> set:
    """The function to create a set of events from the parsed table.

    :return: set of the Event objects
    :rtype: set[Event, ...]
    """
    table = get_table(spreadsheet_id, ranges)

    evnts = set()

    names = table[0][1:]
    events = [table[i][1:] for i in range(5, 68)]
    timings = [table[i][0] for i in range(5, 68)] + ['23:59']

    for person, name in enumerate(names):
        surname, name = name.split()

        # filling the evnts
        for number, event_name in enumerate(events):
            event = Event(
                name=name,
                surname=surname,
                event_name=event_name[person],
                start=datetime.strptime(timings[number], '%H:%M').time(),
                end=datetime.strptime(timings[number + 1], '%H:%M').time()
            )

            evnts.add(event)

    return evnts
