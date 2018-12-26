import psycopg2 as db
import pandas as pd
database_host = 'dataport.cloud'
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

sql_query = """SELECT DISTINCT dataid from university.electricity_egauge_minutes"""

# list_of_buildings =  pd.read_sql(sql_query, conn).dataid.values
list_of_buildings = [114,  661, 2018, 2575, 2814, 2859, 3456, 3482, 5403, 6836, 6990,
       7536, 7940, 8236, 9134, 8188, 2156, 4220, 7951, 2094,   93,  871,
       9737, 7863, 1169, 1415, 3367, 3723, 4373, 4526, 5395, 5921, 7627,
       7850, 8156, 9982, 4514, 7117, 8956, 9248, 9278, 4874, 7641, 8292,
       4946, 4957, 2242, 5568, 3036, 9701,  434, 1507, 7901, 6101, 8565,
       6063,  781, 2532, 5317,  101, 3916, 1310, 3273, 9912, 3413, 2361,
       5809,  668]

total = len(list_of_buildings)
count = -1
for building_id in list_of_buildings:
	count = count+1
	print (count,"/",total)
	sql_query = """SELECT* FROM university.electricity_egauge_minutes WHERE dataid=%d AND localminute BETWEEN '06-09-2015' AND '10-10-2015'""" %int(building_id)
	df = pd.read_sql(sql_query, conn)
	df.to_csv("../metadata/electricity_egauge_minutes/%d.csv" %int(building_id))
