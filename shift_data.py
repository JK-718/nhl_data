import requests
import pandas as pd
from database_connection import get_engine

engine = get_engine()

df = pd.DataFrame(columns = ['GameID', 'PlayerName', 'PlayerID', 'Period', 'StartTime', 'EndTime',
                             'Duration', 'Description', 'Details', 'ShiftNumber', 'EventNumber',
                             'Team', 'TeamCode', 'TeamID'])

min_game_id = 2020020001
max_game_id = 2020020068

for game_id in range(min_game_id, max_game_id + 1):
    print(game_id)
    url = f'https://api.nhle.com/stats/rest/en/shiftcharts?cayenneExp=gameId={game_id}'
    response = requests.get(url)
    data = response.json()

    total_shifts = data['total']
    shifts = data['data']
    
    for shift in shifts:
        duration = shift['duration']
        start_time = shift['startTime']
        end_time = shift['endTime']
        description = shift['eventDescription']
        details = shift['eventDetails']
        event_number = shift['eventNumber']
        player_name = shift['firstName'] + ' ' + shift['lastName']
        period = shift['period']
        player_id = shift['playerId']
        shift_number = shift['shiftNumber']
        team_code = shift['teamAbbrev']
        team_id = shift['teamId']
        team_name = shift['teamName']
        
        df = df.append({'GameID': game_id, 'PlayerName': player_name, 'PlayerID': player_id, 'Period': period,
                        'StartTime': start_time, 'EndTime': end_time, 'Duration': duration, 'Description': description,
                        'Details': details, 'ShiftNumber': shift_number, 'EventNumber': event_number,
                        'Team': team_name, 'TeamCode': team_code, 'TeamID': team_id}, ignore_index=True)
        
