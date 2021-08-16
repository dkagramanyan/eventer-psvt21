from __future__ import print_function
import datetime
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials


def check_creds_and_make_service():
    """
        This function checks user's credentials,makes token if it doesn't exist
        and make a calendar service object for future manipulations
    """

    # If modifying these scopes, delete the file token.json.
    SCOPES = ['https://www.googleapis.com/auth/calendar']

    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    service = build('calendar', 'v3', credentials=creds)
    return service


def make_event(colorId, summary, location, description, start, end, mail):
    
    event = {
      'colorId': colorId,
      'summary': summary,
      'location': location,
      'description': description,
      'start': {
        'dateTime': start,
        'timeZone': 'Europe/Moscow',
      },
      'end': {
        'dateTime': end,
        'timeZone': 'Europe/Moscow',
      },
      'attendees': [
          {'email': mail},
      ],
      'reminders': {
        'useDefault': False,
        'overrides': [
          {'method': 'email', 'minutes': 24 * 60},
          {'method': 'popup', 'minutes': 10},
        ],
      },
    }

    return event


def main():

    service = check_creds_and_make_service()

    # Call the Calendar API
    now = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=3))).isoformat()


    event = make_event(
            colorId=2,
            summary='Google I/O 2015',
            location='800 Howard St., San Francisco, CA 94103',
            description='A chance to hear more about Google\'s developer products.',
            start='2021-08-16T17:00:00+03:00',
            end='2021-08-16T18:00:00+03:00',
            mail='dgkagramanyan@miem.hse.ru'
        )




    event = service.events().insert(calendarId='primary', body=event).execute()
    print('Event created: %s' % (event.get('htmlLink')))
    print('Getting the upcoming 10 events')
    events_result = service.events().list(calendarId='primary', timeMin=now,
                                        maxResults=10, singleEvents=True,
                                        orderBy='startTime').execute()
    events = events_result.get('items', [])

    if not events:
        print('No upcoming events found.')
    for event in events:
        start = event['start'].get('dateTime', event['start'].get('date'))
        print(start, event['summary'])


if __name__ == '__main__':
    main()
