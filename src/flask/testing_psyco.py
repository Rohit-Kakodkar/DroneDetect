import psycopg2

connection = psycopg2.connect(host = 'ec2-35-175-139-211.compute-1.amazonaws.com',
                              database = 'dronedetect',
                              user = 'postgres',
                              password = 'JailBreak0101')

cursor = connection.cursor()

cursor.execute('''SELECT * FROM devices''')

rows = cursor.fetchall()

for row in rows:
    if row[4]:
        print(row)
