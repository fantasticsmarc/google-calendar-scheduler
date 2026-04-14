import os
import datetime
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import pickle

# Autenticación y construcción del servicio de Google Calendar
SCOPES = ['https://www.googleapis.com/auth/calendar']
creds = None

if os.path.exists('Summer Schedule/token.pickle'):
    with open('Summer Schedule/token.pickle', 'rb') as token:
        creds = pickle.load(token)

if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
    else:
        flow = InstalledAppFlow.from_client_secrets_file('Summer Schedule/credentials.json', SCOPES)
        creds = flow.run_local_server(port=0)
    with open('Summer Schedule/token.pickle', 'wb') as token:
        pickle.dump(creds, token)

service = build('calendar', 'v3', credentials=creds)

# Función para eliminar eventos por ID
def delete_event_by_id(service, event_id):
    try:
        service.events().delete(calendarId='primary', eventId=event_id).execute()
        print(f'Event with ID {event_id} deleted.')
    except Exception as e:
        print(f'An error occurred: {e}')

# Leer IDs de eventos desde el archivo events.txt y eliminarlos
event_file = 'Summer Schedule/events.txt'
if os.path.exists(event_file):
    with open(event_file, 'r') as f:
        lines = f.readlines()
    
    for line in lines:
        if '-' in line:
            event_id = line.strip().split(' - ')[-1]
            delete_event_by_id(service, event_id)
    
    # Eliminar el archivo events.txt
    os.remove(event_file)
    print(f'File {event_file} deleted.')
else:
    print(f'File {event_file} not found.')

# Eliminar la imagen generada
image_file = 'Summer Schedule/schedule.png'
if os.path.exists(image_file):
    os.remove(image_file)
    print(f'File {image_file} deleted.')
else:
    print(f'File {image_file} not found.')
