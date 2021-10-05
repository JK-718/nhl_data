import sqlalchemy
import pyodbc
from sqlalchemy.orm import sessionmaker, Session 
from sqlalchemy import create_engine

def db_session(connection_string):
    engine = create_engine(connection_string)
    session_factory = sessionmaker(bind=engine)
    session = session_factory()
    return session, engine

def get_engine():
    engine = create_engine('mssql+pyodbc://DESKTOP-M58TA4E/hockey?driver=SQL+Server+Native+Client+11.0')
    return engine

def db_conn_cursor():
    conn = pyodbc.connect('Driver={SQL Server};'
                      'Server=DESKTOP-M58TA4E;'
                      'Database=hockey;'
                      'Trusted_Connection=yes;')
    cursor = conn.cursor()
    return conn, cursor