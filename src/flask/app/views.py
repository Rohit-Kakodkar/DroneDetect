from flask import render_template
from app import app
from flask import jsonify
import psycopg2
from kafka import KafkaConsumer, TopicPartition
import argparse
from json import loads

@app.route('/')
@app.route('/home')
def home():
   user = { 'GOOGLE_KEY': 'AIzaSyD9e3Rdo8fGQq6hzaXkdsdQzv9Hy0rTolE' }
   connection = psycopg2.connect(host = 'ec2-18-212-177-209.compute-1.amazonaws.com',
                                 database = 'dronedetect',
                                 user = 'postgres',
                                 password = 'JailBreak0101')
   print("GOT HERE")


   cursor = connection.cursor()

   cursor.execute('''SELECT * FROM devices''')

   rows = cursor.fetchall()

   all_latitudes = []
   all_longitudes = []
   crashed_latitudes = []
   crashed_longitudes = []
   malfunctioning_latitudes = []
   malfunctioning_longitudes = []
   for row in rows:
       latitude = row[1]
       longitude = row[2]
       malfunctioning = row[3]
       crashed = row[4]
       all_latitudes.append(latitude)
       all_longitudes.append(longitude)
       if row[4]:
           crashed_latitudes.append(latitude)
           crashed_longitudes.append(longitude)
           crashed_latitudes = crashed_latitudes[:7]
           crashed_longitudes = crashed_longitudes[:7]

       if row[3]:
           malfunctioning_latitudes.append(latitude)
           malfunctioning_longitudes.append(longitude)
           malfunctioning_latitudes = malfunctioning_latitudes[:23]
           malfunctioning_longitudes = malfunctioning_longitudes[:23]


   return render_template("home.html",
                           APIkey = 'AIzaSyD9e3Rdo8fGQq6hzaXkdsdQzv9Hy0rTolE',
                           functioning_lat= all_latitudes,
                           functioning_lon = all_longitudes,
                           malfunctioning_lat = malfunctioning_latitudes,
                           malfunctioning_lon = malfunctioning_longitudes,
                           crashed_lat = crashed_latitudes,
                           crashed_lon = crashed_longitudes,
                           All = len(all_latitudes),
                           crashed = len(crashed_latitudes),
                           malfunctioning = len(malfunctioning_latitudes)
                           )

@app.route('/employeeportal')
def employeeportal():
    # tp = TopicPartition('crashed-devices',0)
    # consumer = KafkaConsumer('crashed-devices', bootstrap_servers=['ec2-52-203-135-135.compute-1.amazonaws.com:9092',
    #                         'ec2-52-70-111-222.compute-1.amazonaws.com:9092', 'ec2-34-193-78-218.compute-1.amazonaws.com:9092'],
   	# 					    enable_auto_commit=True, group_id='my-group',
   	# 					    auto_offset_reset = 'earliest',
    #                         value_deserializer=lambda x: loads(x.decode('utf-8')))
    # lastOffset = consumer.beginning_offsets([tp])[tp]
    # latitudes = []
    # longitudes = []
    # i = 0
    # for message in consumer:
    #     i += 1
    #     msg = message.value
    #     latitudes.append(msg['latitude'])
    #     longitudes.append(msg['longitude'])
    #     print(latitudes, longitudes)
    #     if i==1:
    #         print("GOT HERE")
    #         consumer.commit()
    #         break
    #
    # consumer.close()

    latitudes = [40.6349833109, 40.6268903367, 40.5383258365, 40.6224222456, 40.8552825266, 40.739323065, 40.7340164399]
    longitudes = [-73.9674308662, -73.9463895297, -74.1492046912, -74.004704123, -73.8877158182, -73.7005708962, -73.9928895187]

    return render_template("employeeportal.html",
                           APIkey = 'AIzaSyD9e3Rdo8fGQq6hzaXkdsdQzv9Hy0rTolE',
                           latitudes= latitudes.pop(),
                           longitudes = longitudes.pop())
