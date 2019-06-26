from flask import render_template
from app import app
from flask import jsonify
import psycopg2
from kafka import KafkaConsumer

@app.route('/')
@app.route('/home')
def home():
   user = { 'GOOGLE_KEY': api_key }
   connection = psycopg2.connect(host = psnode,
                                 database = dbname,
                                 user = psuser,
                                 password = pspassword)

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
   consumer = KafkaConsumer('numtest', bootstrap_servers=['localhost:9092'],
   						    enable_auto_commit=True, group_id='my-group',
   						    auto_offset_reset = 'earliest')
   latitudes = [40.7128, 40.7228, 40.7228]
   longitudes = [-74.0160, -74.0260, -74.0360]
   return render_template("employeelogin.html",
                           APIkey = api_key,
                           latitudes= latitudes,
                           longitudes = longitudes)
