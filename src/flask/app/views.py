from flask import render_template
from app import app
from flask import jsonify
import psycopg2

@app.route('/')
@app.route('/home')
def home():
   user = { 'GOOGLE_KEY': 'AIzaSyD9e3Rdo8fGQq6hzaXkdsdQzv9Hy0rTolE' }
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
                           APIkey = 'AIzaSyD9e3Rdo8fGQq6hzaXkdsdQzv9Hy0rTolE',
                           functioning_lat= all_latitudes,
                           functioning_lon = all_longitudes,
                           malfunctioning_lat = malfunctioning_latitudes,
                           malfunctioning_lon = malfunctioning_longitudes,
                           crashed_lat = crashed_latitudes,
                           crashed_lon = crashed_longitudes
                           )

@app.route('/employeelogin')
def employeelogin():
   user = { 'GOOGLE_KEY': 'AIzaSyD9e3Rdo8fGQq6hzaXkdsdQzv9Hy0rTolE' }
   latitudes = [40.7128, 40.7228, 40.7228]
   longitudes = [-74.0160, -74.0260, -74.0360]
   return render_template("employeelogin.html",
                           APIkey = 'AIzaSyD9e3Rdo8fGQq6hzaXkdsdQzv9Hy0rTolE',
                           latitudes= latitudes,
                           longitudes = longitudes)
