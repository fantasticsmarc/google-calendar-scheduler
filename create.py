import os
import pandas as pd
import matplotlib.pyplot as plt
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

# Función para agregar eventos a Google Calendar y guardar nombre e ID en un archivo .txt
def add_event_to_calendar(service, summary, start_time_str, end_time_str, time_zone='Europe/Madrid', file='Summer Schedule/events.txt', day_count=1):
    try:
        event = {
            'summary': summary,
            'start': {
                'dateTime': start_time_str,
                'timeZone': time_zone,
            },
            'end': {
                'dateTime': end_time_str,
                'timeZone': time_zone,
            },
            'reminders': {
                'useDefault': False,
                'overrides': [
                    {'method': 'popup', 'minutes': 5},
                ],
            },
        }
        created_event = service.events().insert(calendarId='primary', body=event).execute()
        event_id = created_event['id']
        with open(file, 'a') as f:
            f.write(f'{summary} - {event_id}\n')
        print(f'Event created: {created_event.get("htmlLink")} for {summary} from {start_time_str} to {end_time_str}')
    except Exception as e:
        print(f'An error occurred: {e}')
        print(f'Failed to create event: {summary} from {start_time_str} to {end_time_str}')

# Horario ajustado
schedule = {
    'Hora': ['9:00 - 10:00', '10:00 - 11:00', '11:00 - 11:30', '11:30 - 14:30', '14:30 - 15:00', '15:00 - 17:00', '17:00 - 21:00', '21:00 - 22:00', '22:00 - 23:59'],
    'Lunes': ['Desayuno', 'Ejercicio', 'Tiempo libre', 'Python', 'Almuerzo', 'JavaScript', 'Tiempo libre', 'Cena', 'Ocio'],
    'Martes': ['Desayuno', 'Ejercicio', 'Tiempo libre', 'Arduino', 'Almuerzo', 'Python', 'Tiempo libre', 'Cena', 'Ocio'],
    'Miércoles': ['Desayuno', 'Ejercicio', 'Tiempo libre', 'JavaScript', 'Almuerzo', 'Arduino', 'Tiempo libre', 'Cena', 'Ocio'],
    'Jueves': ['Desayuno', 'Ejercicio', 'Tiempo libre', 'Python', 'Almuerzo', 'JavaScript', 'Tiempo libre', 'Cena', 'Ocio'],
    'Viernes': ['Desayuno', 'Ejercicio', 'Tiempo libre', 'Arduino', 'Almuerzo', 'Python', 'Tiempo libre', 'Cena', 'Ocio'],
    'Sábado': ['Desayuno', 'Ejercicio', 'Tiempo libre', 'Proyectos', 'Almuerzo', 'Proyectos', 'Tiempo libre', 'Cena', 'Ocio'],
    'Domingo': ['Desayuno', 'Ejercicio', 'Tiempo libre', 'Proyectos', 'Almuerzo', 'Proyectos', 'Tiempo libre', 'Cena', 'Ocio'],
}

# Crear DataFrame
df = pd.DataFrame(schedule)

# Colores
colors = ['#ADD8E6', '#87CEEB', '#4682B4', '#5F9EA0', '#B0E0E6', '#1E90FF', '#00BFFF', '#6495ED', '#4169E1']

# Guardar como imagen
fig, ax = plt.subplots(figsize=(12, 8))
ax.axis('tight')
ax.axis('off')

# Crear la tabla
the_table = ax.table(cellText=df.values, colLabels=df.columns, cellLoc='center', loc='center')

# Añadir colores
for i in range(len(df)):
    for j in range(len(df.columns)):
        the_table[(i+1, j)].set_facecolor(colors[i % len(colors)])

the_table.auto_set_font_size(False)
the_table.set_fontsize(12)
the_table.scale(1.5, 1.5)

# Ajustar la altura de las filas directamente
for pos, cell in the_table.get_celld().items():
    cell.set_height(0.15)

plt.savefig('Summer Schedule/schedule.png', bbox_inches='tight')

# Traducción de nombres de días
day_translation = {
    'Monday': 'Lunes',
    'Tuesday': 'Martes',
    'Wednesday': 'Miércoles',
    'Thursday': 'Jueves',
    'Friday': 'Viernes',
    'Saturday': 'Sábado',
    'Sunday': 'Domingo'
}

# Agregar eventos al calendario
start_date = datetime.date(2024, 6, 24)  # Primer lunes de verano
end_date = datetime.date(2024, 9, 22)  # Último domingo de verano

current_date = start_date
day_count = 1
while current_date <= end_date:
    day_name = current_date.strftime("%A")
    day_name_spanish = day_translation.get(day_name, "")
    if day_name_spanish in schedule:
        with open('Summer Schedule/events.txt', 'a') as f:
            f.write(f'Day {day_count}:\n')
        for time_slot, activity in zip(schedule['Hora'], schedule[day_name_spanish]):
            start_time, end_time = time_slot.split(' - ')
            # Asegúrate de que las horas estén en formato correcto
            start_time_str = f'{current_date}T{start_time}:00'
            end_time_str = f'{current_date}T{end_time}:00'
            try:
                start_datetime = datetime.datetime.strptime(f'{current_date} {start_time}', '%Y-%m-%d %H:%M')
                end_datetime = datetime.datetime.strptime(f'{current_date} {end_time}', '%Y-%m-%d %H:%M')
                print(f'Trying to add event: {activity} from {start_datetime.isoformat()} to {end_datetime.isoformat()}')
                add_event_to_calendar(service, activity, start_datetime.isoformat(), end_datetime.isoformat(), day_count=day_count)
            except ValueError as e:
                print(f'Error parsing date/time: {e}')
    current_date += datetime.timedelta(days=1)
    day_count += 1

print("Horario creado y eventos añadidos a Google Calendar.")
