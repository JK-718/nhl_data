import requests
import pandas as pd
from database_connection import get_engine

engine = get_engine()

game_df = pd.DataFrame(columns = ['GameID', 'PK', 'Season', 'GameType', 'Start', 'End',
                                  'HomeTeam', 'HomeTeamID', 'AwayTeam', 'AwayTeamID',
                                  'VenueID', 'VenueName'])
player_df = pd.DataFrame(columns = ['Name', 'ID'])

game_df = pd.DataFrame()
player_df = pd.DataFrame()

min_game_id = 2020020001
max_game_id = 2020020868

for game_id in range(min_game_id, max_game_id + 1):
    url = f'https://statsapi.web.nhl.com/api/v1/game/{game_id}/feed/live'
    response = requests.get(url)
    data = response.json()
    print(game_id)
    #game, datetime, status, teams, players, venue
    #game
    pk = data['gameData']['game']['pk']
    season = data['gameData']['game']['season']
    game_type = data['gameData']['game']['type']

    #datetime
    start_dt = data['gameData']['datetime']['dateTime'] 
    end_dt = data['gameData']['datetime']['endDateTime']
    
    #status
    #skipped because only planning on uploading finished game
    
    #teams
    home_team = data['gameData']['teams']['home']
    home_team_name = home_team['name']
    home_team_id = home_team['id']
    home_team_goals = data['liveData']['boxscore']['teams']['home']['teamStats']['teamSkaterStats']['goals']
    away_team = data['gameData']['teams']['away']
    away_team_name = away_team['name']
    away_team_id = away_team['id']
    away_team_goals = data['liveData']['boxscore']['teams']['away']['teamStats']['teamSkaterStats']['goals']
    winner = home_team_name if home_team_goals > away_team_goals else away_team_name
    winner_id = home_team_id if home_team_goals > away_team_goals else away_team_id
    
    #players
    players = data['gameData']['players']
    for i, j in enumerate(players):
        try:
            player = players[j]
            player_id = player['id']
            player_name = player['fullName']
            player_number = player['primaryNumber']
            player_age = player['currentAge']
            player_country = player['birthCountry']
            player_nationality = player['nationality']
            player_height = player['height']
            player_weight = player['weight']
            player_shoots = player['shootsCatches']
            player_position = player['primaryPosition']['name']
            player_team = player['currentTeam']['name']
            player_team_id = player['currentTeam']['id']
            player_team_abbr = player['currentTeam']['triCode']
            if player_team_id == home_team_id:
                player_home_away = 'Home'
            elif player_team_id == away_team_id:
                player_home_away = 'Away'
            else:
                player_home_away = None
                print(player_home_away, player_team_id, home_team_id, away_team_id)
            player_df = player_df.append({'Name': player_name, 'ID': player_id, 'Number': player_number, 
                                          'Team': player_team, 'TeamCode': player_team_abbr,
                                          'TeamID': player_team_id, 'Age': player_age,'Country': player_country, 
                                          'Nationality': player_nationality,'Height': player_height, 
                                          'Weight': player_weight, 'Shot': player_shoots, 'Position': player_position,
                                          'GameID': game_id, 'GamePK': pk, 'HomeAway': player_home_away}, ignore_index=True)

        except:
            pass
    
    #venue
    venue = data['gameData']['venue']
    try:
        venue_id = venue['id']
        venue_name = venue['name']
    except KeyError:
        venue_id = None

    game_df = game_df.append({'GameID': game_id, 'PK': pk, 'Season': season,
                              'GameType': game_type, 'Start': start_dt, 'End': end_dt,
                                  'HomeTeamGoals': home_team_goals, 'AwayTeamGoals': away_team_goals,
                                  'Winner': winner, 'WinnerID': winner_id,
                                  'HomeTeam': home_team_name, 'HomeTeamID': home_team_id, 
                                  'AwayTeam': away_team_name, 'AwayTeamID': away_team_id,
                                  'VenueID': venue_id, 'VenueName': venue_name}, ignore_index=True)

    if game_id % 100 == 0:
            player_df.to_sql('GamePlayerData', con=engine, schema ='nhl', if_exists='append', index=False)
            player_df = pd.DataFrame(columns = ['Name', 'ID'])
            game_df.to_sql('GameData', con=engine, schema ='nhl', if_exists='append', index=False)
            game_df = pd.DataFrame(columns = ['GameID', 'PK', 'Season', 'GameType', 'Start', 'End',
                                  'HomeTeam', 'HomeTeamID', 'AwayTeam', 'AwayTeamID',
                                  'VenueID', 'VenueName'])
            
player_df.to_sql('GamePlayerData', con=engine, schema ='nhl', if_exists='append', index=False)
game_df.to_sql('GameData', con=engine, schema ='nhl', if_exists='append', index=False)


