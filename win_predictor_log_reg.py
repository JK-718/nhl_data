import pandas as pd
import matplotlib.pyplot as plt
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from database_connection import db_conn_cursor

conn, cursor = db_conn_cursor()
query = "select * from nhl.teamgameshotview"
df = pd.read_sql_query(query, conn)
df.fillna(0, inplace=True)
X, y = df.iloc[:, 3:6].values, df.iloc[:, 2].values
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)
log_reg = LogisticRegression()
log_reg.fit(X_train, y_train)
y_proba = log_reg.predict_proba(X_test)
plt.plot(X_test[:, 0], y_proba[:, 1])