import requests
import pandas as pd
import numpy as np
from database_connection import db_session, db_conn_cursor
import matplotlib.pyplot as plt
import seaborn as sns

NET_LOC_ADJ = [89, 0]

def get_data():
    conn, cursor = db_conn_cursor()
    query = """
    select
    *
    from nhl.playdataview
    order by gameid, datetime
    """ #remember to change to playdataview
    dataframe = pd.read_sql_query(query, conn)
    return dataframe

def calculate_angle(vector_1, vector_2, vector_3):
    return np.arccos(np.dot(vector_1 - vector_2, vector_3 - vector_2) / 
                     (np.linalg.norm(vector_1 - vector_2) * np.linalg.norm(vector_3 - vector_2)))

def angle_between_events(dataframe):
    angle_change = 0
    angle_change_array = np.zeros(len(dataframe))
    for i, row in dataframe.iterrows():
        if i == 0:
            angle_change_array[i] = None
        elif (dataframe.loc[i, 'Event'] != 'Shot' or dataframe.loc[i - 1, 'Event'] != 'Shot') or (dataframe.loc[i, 'HomeAway'] != dataframe.loc[i - 1, 'HomeAway']):
            angle_change_array[i] = None
        else:
            angle_change = calculate_angle(np.array([dataframe.loc[i - 1, 'CoordinateXAdjusted'], dataframe.loc[i - 1, 'CoordinateYAdjusted']]),
                                           np.array(NET_LOC_ADJ), 
                                           np.array([dataframe.loc[i, 'CoordinateXAdjusted'], dataframe.loc[i, 'CoordinateYAdjusted']]))
            angle_change_array[i] = angle_change
    angle_change_array_degrees = np.degrees(angle_change_array)
    return angle_change_array_degrees

def convert_to_seconds(time_string):
    time_string_minutes = int(time_string[0:2])
    time_string_seconds = int(time_string[3:5])
    return (time_string_minutes * 60) + time_string_seconds

def time_between_plays(dataframe):
    time_diff = 0
    time_diff_array = np.zeros(len(dataframe))
    rebound_array = np.zeros(len(dataframe))
    for i, row in dataframe.iterrows():
        if i == 0:
            time_diff = convert_to_seconds(dataframe.loc[i, 'PeriodTime'])
            time_diff_array[i] = time_diff
        else:
            time_diff = dataframe.loc[i, 'PeriodTimeRemainingSeconds'] - dataframe.loc[i - 1, 'PeriodTimeRemainingSeconds']
            time_diff_array[i] = time_diff
            if abs(time_diff) <= 3:
                rebound_array[i] = 1
    return time_diff_array, rebound_array

def get_shots():
    df = get_data()
    df['PeriodTimeRemainingSeconds'] = df.apply(lambda x: convert_to_seconds(x.PeriodTimeRemaining), axis=1)
    time_array, rebound_array = time_between_plays(df)
    df['TimeBetween'], df['IsRebound'] = time_array.tolist(), rebound_array.tolist()
    angle_array = angle_between_events(df)
    df['AngleChange'] = angle_array.tolist()
    return df
    
if __name__ == '__main__':
    get_shots()