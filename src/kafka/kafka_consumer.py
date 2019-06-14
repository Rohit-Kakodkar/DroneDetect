"""
	Testing kafka consumer
"""

from kafka import KafkaConsumer
from json import loads
import matplotlib.pyplot as plt
import numpy as np

consumer = KafkaConsumer('sensor_data',
						 bootstrap_servers = ['localhost:9092'],
						 auto_offset_reset='earliest',
						 enable_auto_commit=True,
						 group_id='my-group',
						 value_deserializer=lambda x: loads(x.decode('utf-8')))


baromatric_reading = []

i = 0
for message in consumer:
	i += 1
	message = message.value
	baromatric_reading.append(message['baromatric_reading'])
	if (i%100 == 0):
		plt.plot(np.linspace(0, 1, num = len(baromatric_reading)), baromatric_reading)
		plt.show()
