import requests
import pandas as pd
from database_connection import db_session, db_conn_cursor
import matplotlib.pyplot as plt
import seaborn as sns

url = 'https://statsapi.web.nhl.com/api/v1/game/{}/feed/live'.format(2020030111)
response = requests.get(url)
data = response.json()

conn, cursor = db_conn_cursor()

query = """
select
*
from nhl.shotview
"""

df = pd.read_sql_query(query, conn)
plt.scatter(df.CoordinateXAdjusted, df.CoordinateYAdjusted)
plt.hist2d(df.CoordinateXAdjusted, df.CoordinateYAdjusted, bins = 50)

goals = df.pivot('CoordinateXAdjusted', 'CoordinateYAdjusted', 'GoalFlag')
sns.heatmap(goals)