from flask import render_template
from app import app
from flask import jsonify
import psycopg2
from kafka import KafkaConsumer
import argparse

@app.route('/')
@app.route('/home')
def home():
   user = { 'GOOGLE_KEY': api_key }
   connection = psycopg2.connect(host = 'ec2-35-175-139-211.compute-1.amazonaws.com',
                                 database = 'dronedetect',
                                 user = 'postgres',
                                 password = 'JailBreak0101')

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

       if row[3]:
           malfunctioning_latitudes.append(latitude)
           malfunctioning_longitudes.append(longitude)


   return render_template("home.html",
                           APIkey = api_key,
                           functioning_lat= all_latitudes,
                           functioning_lon = all_longitudes,
                           malfunctioning_lat = malfunctioning_latitudes,
                           malfunctioning_lon = malfunctioning_longitudes,
                           crashed_lat = crashed_latitudes,
                           crashed_lon = crashed_longitudes
                           )

@app.route('/employeelogin')
def employeelogin():
    consumer = KafkaConsumer('crashed-devices', bootstrap_servers=['ec2-52-203-135-135.compute-1.amazonaws.com:9092',
                            'ec2-52-70-111-222.compute-1.amazonaws.com:9092', 'ec2-34-193-78-218.compute-1.amazonaws.com'],
   						    enable_auto_commit=True, group_id='my-group',
   						    auto_offset_reset = 'earliest',
                            value_deserializer=lambda x: loads(x.decode('utf-8')))
    lastOffset = consumer.end_offsets([tp])[tp]
    latitude = []
    longitude = []
    for message in consumer:
        msg = message.value
        latitudes.append(msg['latitude'])
        longitudes.append(msg['longitude'])
        if message.offset == lastOffset -1:
    		consumer.commit()
    		continue

    return render_template("employeelogin.html",
                           APIkey = api_key,
                           latitudes= latitudes,
                           longitudes = longitudes)
