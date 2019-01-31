import psycopg2 as db
import pandas as pd
database_host = 'dataport.pecanstreet.org'
database_port = '5434'
database_name = 'postgres'
database_schema = 'university'
database_username='iMnYaDQqKn5f'
database_password='KFmf95DPQ6T2'

conn = db.connect('host=' + database_host +
                          ' port=' + database_port +
                          ' dbname=' + database_name +
                          ' user=' + database_username +
                          ' password=' + database_password)

sql_query = """SELECT * from university.survey_2017_all_participants"""
df = pd.read_sql(sql_query, conn)
df.to_csv("../metadata/survey_2017_all_participants.csv", index=False)
