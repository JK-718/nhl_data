import requests
import pandas as pd
from database_connection import get_engine

engine = get_engine()

def get_seconds(time):
    minutes = int(time[0:2])
    seconds = int(time[3:5])
    return (minutes * 60) + seconds

df = pd.DataFrame(columns = ['GameID', 'PlayerName', 'PlayerID', 'Period', 'StartTime', 'StartTimeSeconds',
                             'EndTime', 'EndTimeSeconds', 'Duration', 'DurationSeconds' 'Description', 'Details',
                             'ShiftNumber', 'EventNumber', 'Team', 'TeamCode', 'TeamID'])

min_game_id = 2020020001
max_game_id = 2020020868

for game_id in range(min_game_id, max_game_id + 1):
    print(game_id)
    url = f'https://api.nhle.com/stats/rest/en/shiftcharts?cayenneExp=gameId={game_id}'
    response = requests.get(url)
    data = response.json()

    total_shifts = data['total']
    shifts = data['data']
    
    for shift in shifts:
        duration = shift['duration']
        try:
            duration_seconds = get_seconds(duration)
        except:
            duration_seconds = None
        start_time = shift['startTime']
        try:
            start_time_seconds = get_seconds(start_time)
        except:
            start_time_seconds = None
        end_time = shift['endTime']
        try:
            end_time_seconds = get_seconds(end_time)
        except:
            end_time_seconds = None
        description = shift['eventDescription']
        details = shift['eventDetails']
        event_number = shift['eventNumber']
        try:
            player_name = shift['firstName'] + ' ' + shift['lastName']
        except:
            player_name = None
        period = shift['period']
        player_id = shift['playerId']
        shift_number = shift['shiftNumber']
        team_code = shift['teamAbbrev']
        team_id = shift['teamId']
        team_name = shift['teamName']
        
        df = df.append({'GameID': game_id, 'PlayerName': player_name, 'PlayerID': player_id, 'Period': period,
                        'StartTime': start_time, 'StartTimeSeconds': start_time_seconds, 'EndTime': end_time, 
                        'EndTimeSeconds': end_time_seconds,'Duration': duration, 'DurationSeconds': duration_seconds, 
                        'Description': description, 'Details': details, 'ShiftNumber': shift_number, 
                        'EventNumber': event_number, 'Team': team_name, 'TeamCode': team_code, 
                        'TeamID': team_id}, ignore_index=True)
        
    if game_id % 25 == 0:
        df.to_sql('ShiftData', con=engine, schema ='nhl', if_exists='append', index=False)
        df = pd.DataFrame(columns = ['GameID', 'PlayerName', 'PlayerID', 'Period', 'StartTime', 'EndTime',
                             'Duration', 'Description', 'Details', 'ShiftNumber', 'EventNumber',
                             'Team', 'TeamCode', 'TeamID'])
    
df.to_sql('ShiftData', con=engine, schema ='nhl', if_exists='append', index=False)