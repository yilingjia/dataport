import psycopg2 as db
import pandas as pd
database_host = 'dataport.cloud'
database_port = '5434'
database_name = 'postgres'
database_schema = 'university'
database_username = 'iMnYaDQqKn5f'
database_password = 'KFmf95DPQ6T2'

conn = db.connect('host=' + database_host +
                  ' port=' + database_port +
                  ' dbname=' + database_name +
                  ' user=' + database_username +
                  ' password=' + database_password)

sql_query = """SELECT DISTINCT dataid from university.electricity_egauge_hours"""

list_of_buildings = pd.read_sql(sql_query, conn).dataid.values


total = len(list_of_buildings)
count = -1
print(total)
for building_id in list_of_buildings:
    count += 1
    if count < 500:
        continue
    else:
        print(count, "/", total)
        sql_query = """SELECT* FROM university.electricity_egauge_hours WHERE dataid=%d""" %int(building_id)
        df = pd.read_sql(sql_query, conn)
        df.to_csv("../metadata/electricity_egauge_hours/%d.csv" % int(building_id))
