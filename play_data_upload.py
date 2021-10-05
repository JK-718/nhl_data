import pyodbc 
import requests
import pandas as pd
import sqlalchemy

conn = pyodbc.connect('Driver={SQL Server};'
                      'Server=DESKTOP-M58TA4E;'
                      'Database=hockey;'
                      'Trusted_Connection=yes;')

engine = sqlalchemy.create_engine('mssql+pyodbc://DESKTOP-M58TA4E/hockey?driver=SQL+Server+Native+Client+11.0')
cursor = conn.cursor()
df = pd.DataFrame(columns = ['Event', 'Period', 'PeriodType', 'PeriodTime', 'PeriodTimeRemaining',
                        'DateTime', 'GoalsAway', 'GoalsHome', 'CoordinateX', 'CoordinateY', 'ShotType',
                        'Player1', 'Player1ID', 'Player1Type', 'Player2', 'Player2ID', 'Player2Type',                        
                        'Player3', 'Player3ID', 'Player3Type', 'Player4', 'Player4ID', 'Player4Type',
                        'Goalie', 'GoalieID', 'GameID', 'Team', 'TeamID', 'TeamCode'])

url = 'https://statsapi.web.nhl.com/api/v1/game/{}/feed/live'.format(2020030111)
response = requests.get(url)
data = response.json()

min_game_id = 2020020001
max_game_id = 2020020868
#max_game_id = 2020020003
for game_id in range(min_game_id, max_game_id + 1):
    print(game_id)
    url = f'https://statsapi.web.nhl.com/api/v1/game/{game_id}/feed/live'
    response = requests.get(url)
    data = response.json()
    
    for i, play in enumerate(data['liveData']['plays']['allPlays']):
        key = list(play.keys())[0]
        value = list(play.values())[0]
        
        if key == 'result':
            continue
        elif key == 'players':
            event = play['result']['event']
        if play['result']['event'] == 'Goal':
            length = len(play['players'])
        try:
            period = play['about']['period']
            period_type = play['about']['periodType']
            period_time = play['about']['periodTime']
            period_time_remaining = play['about']['periodTimeRemaining']
            dt = play['about']['dateTime']
            goals_away = play['about']['goals']['away']
            goals_home = play['about']['goals']['home']
            x_coord = play['coordinates']['x']
            y_coord = play['coordinates']['y']
            team = play['team']['name']
            team_id = play['team']['id']
            team_code = play['team']['triCode']
            
            length = len(play['players'])
            goalie, goalie_id = None, None
            player1 = play['players'][0]['player']['fullName']
            player1_id = play['players'][0]['player']['id']
            
            shot_type = None
            if event in ['Shot', 'Goal']:
                shot_type = play['result']['secondaryType']
            
            if event == 'Giveaway':
                player1_type = 'Giveawayer'
            elif event == 'Takeaway':
                player1_type = 'Takeawayer'
            else:
                player1_type = play['players'][0]['playerType']
            if player1_type == 'Goalie':
                    goalie, goalie_id = player1, player1_id
            
            if length >= 2:
                player2 = play['players'][1]['player']['fullName']
                player2_id = play['players'][1]['player']['id']
                player2_type = play['players'][1]['playerType']
                if player2_type == 'Goalie':
                    goalie, goalie_id = player2, player2_id
            else:
                player2 = None
                player2_id = None
                player2_type = None
                
            if length >= 3:
                player3 = play['players'][2]['player']['fullName']
                player3_id = play['players'][2]['player']['id']
                player3_type = play['players'][2]['playerType']
                if player3_type == 'Goalie':
                    goalie, goalie_id = player3, player3_id
            else:
                player3 = None
                player3_id = None
                player3_type = None
                
            if length >= 4:
                player4 = play['players'][3]['player']['fullName']
                player4_id = play['players'][3]['player']['id']
                player4_type = play['players'][3]['playerType']
                if player4_type == 'Goalie':
                    goalie, goalie_id = player4, player4_id
            else:
                player4 = None
                player4_id = None
                player4_type = None
                
        except KeyError:
            pass
        
        df = df.append({'Event': event, 'Period': period, 'PeriodType': period_type,
                        'PeriodTime': period_time, 'PeriodTimeRemaining': period_time_remaining,
                        'DateTime': dt, 'GoalsAway': goals_away, 'GoalsHome': goals_home,
                        'CoordinateX': x_coord, 'CoordinateY': y_coord, 'ShotType': shot_type,
                        'Player1': player1, 'Player1ID': player1_id, 'Player1Type': player1_type,
                        'Player2': player2, 'Player2ID': player2_id, 'Player2Type': player2_type,
                        'Player3': player3, 'Player3ID': player3_id, 'Player3Type': player3_type,
                        'Player4': player4, 'Player4ID': player4_id, 'Player4Type': player4_type,
                        'Goalie': goalie, 'GoalieID': goalie_id, 'GameID': game_id,
                        'Team': team, 'TeamID': team_id, 'TeamCode': team_code}, ignore_index = True)
        
        if game_id % 50 == 0:
            df.to_sql('PlayData', con=engine, schema ='nhl', if_exists='append', index=False)
            df = pd.DataFrame(columns = ['Event', 'GameID'])

    
df.to_sql('PlayData', con=engine, schema ='nhl', if_exists='append', index=False)