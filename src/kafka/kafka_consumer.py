"""
	Testing kafka consumer
"""

from kafka import KafkaConsumer
from json import loads
import matplotlib.pyplot as plt
import numpy as np

consumer = KafkaConsumer('sensor-data',
						 bootstrap_servers = ['localhost:9092'],
						 auto_offset_reset='latest',
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
		if min(baromatric_reading)<370:
			print('True')
		else:
			print('False')
		baromatric_reading=[]
