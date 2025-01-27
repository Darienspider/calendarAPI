import datetime
import os.path
import pytz #timezone import for google calendar
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

import time 



class GoogleCalendar:
    def __init__(self):
        self.SCOPES = ['https://www.googleapis.com/auth/calendar',"https://www.googleapis.com/auth/calendar.readonly"]
        self.timezones = [i for i in pytz.all_timezones]
        self.setup('America/New_York')

    def getTimezones(self):
        return self.timezones

    def setup(self,timezone):
        creds = None
        self.timezone = timezone
        if os.path.exists('token.json'):
            creds = Credentials.from_authorized_user_file('token.json',self.SCOPES)
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                
                flow = InstalledAppFlow.from_client_secrets_file(
                    "credentials.json", self.SCOPES
                )
                creds = flow.run_local_server(port=0)
            with open('token.json', 'w') as token:
                token.write(creds.to_json())
        
        try:
            self.service = build("calendar", "v3", credentials=creds)
            print("Successfully authenticated")

        except HttpError as error:
            print(f"An error occurred: {error}")

    def create_event(self, event_title, location, description,starttime: datetime, endtime : datetime ,attendeees : list):    
        """ Creates / Adds an invent to the google calendar """
        event = {
            "summary": f"{event_title}",
            "location": f"{location}",
            "description": f"{description}",
            "start": {"dateTime": f"{starttime}", "timeZone": f"{self.timezone}"},
            "end": {"dateTime": f"{endtime}", "timeZone": f"{self.timezone}"},
            "recurrence": ["RRULE:FREQ=DAILY;COUNT=2"],
            "attendees": [
                {"email": "shadarien@shadwilliams.dev"}
            ],
        }
        self.service.events().insert(calendarId='primary', body=event).execute()
        print(event['summary'] +  ' has been added to the calendar')
    def show_events (self):
        """ Shows all the events in the google calendar """
        events = self.service.events().list(calendarId='primary').execute()
        found_events = {}
        for events in events['items']:
            summary = events['summary']
            event_id = events['id']
            startVisual = datetime.datetime.strptime(events['start']['dateTime'],"%Y-%m-%dT%H:%M:%S%z").strftime("%m/%d/%Y %I:%M %p")
            start =events['start']['dateTime']

            endvisual = datetime.datetime.strptime(events['end']['dateTime'],"%Y-%m-%dT%H:%M:%S%z").strftime("%m/%d/%Y %I:%M %p")
            end = events['start']['dateTime']

            found_events[event_id] = {"summary":summary,"timestamp": (start,end), "visual": (startVisual,endvisual)}

        return found_events
            # print(events['start']['dateTime'])
        
    def remove_events(self, chosen_id):
        """ Removes an event from the google calendar """
        events = self.show_events()
        # display event summary, start time
        #TODO: Implement this function
        for event,content in enumerate(events):
            try:
                self.service.events().delete(calendarId='primary', eventId=chosen_id).execute()
                print(f"Event {events[chosen_id]['summary']} has been deleted")
                break
            except HttpError as error:
                print(f"Event already deleted or not present")
                break
        pass

if __name__ == '__main__':
    test = GoogleCalendar()
    useTime = (datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S%z"))
    test.create_event('Test from API2','Home','This is a test',useTime,useTime,'test@gmail.com')
    events = test.show_events()
    event_ids = list(events.keys())
    time.sleep(60)
    test.remove_events(event_ids[-1])
    pass