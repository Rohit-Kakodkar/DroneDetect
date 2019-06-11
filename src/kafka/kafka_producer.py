import sys
sys.path.insert(0, '/home/rohit/DroneDetect/src/utility')

from events import recovery_event
import math
from datetime import datetime
from time import sleep
from json import dumps
from kafka import KafkaProducer
import numpy as np
import argparse

parser = argparse.ArgumentParser(description='Data generation')
parser.add_argument('--number_of_devices', type=int, default=1,
                    help='Total number of drones deployed')
# define broker list
parser.add_argument('--broker', type=str, default= 'localhost:9092', help='list of brokers')
# define the partition where kafka should write
parser.add_argument('--partition', type=int, default=0,
                    help="partition on which this producer should send")

args = parser.parse_args()

class Generate_data():

    def __init__(self, address, n):
        self.dataProducer = KafkaProducer(bootstrap_servers=[address])
        self.ndrones = n
        self.event_log = np.zeros(n, dtype = bool)
        self.event_log_time = -5*np.ones(n)
        self.__barometer_event_reading = np.zeros(n)

    def Serialize_JSON(self):
        if isinstance(self.TimeStamp, datetime):
            return self.TimeStamp.__str__()

    def instantiate_event(self):
        for i in range(self.ndrones):
            if np.random.uniform(0,1) < 0.05:
                self.event_log[i] = True

    def stop_event(self):
        for i in range(self.ndrones):
            if self.event_log[i] and self.event_log_time[i]>=5:
                self.event_log[i] = False

    def update_time_log(self):
        dt = 0.1
        for i in range(self.ndrones):
            if self.event_log[i]:
                self.event_log_time += dt

    def generate_event(self):
        self.instantiate_event()
        self.update_time_log()
        for i in range(self.ndrones):
            if self.event_log[i]:
                ts = self.event_log_time[i]
                self.__barometer_event_reading[i] = recovery_event(1, 1, 100, ts, 1)\
                                                    .generate_altitude()

    def ProduceData(self):
        self.TimeStamp = datetime.now()
        print(self.TimeStamp)
        while True:
            self.generate_event()
            baromatric_reading = np.random.uniform(395, 400, n) + self.__barometer_event_reading
            gyrometer_x = np.random.uniform(-0.4, 0.4, n)
            gyrometer_y = np.random.uniform(-0.4, 0.4, n)
            wind_speed = 55*np.ones(n)

            for device_id in range(n):
                data = dumps({  "device_id" : device_id,
                                "baromatric_reading" : baromatric_reading[device_id],
                                "gyrometer_x" : gyrometer_x[device_id],
                                "gyrometer_y" : gyrometer_y[device_id],
                                "wind_speed" : wind_speed[device_id]}).encode('utf-8')
                sleep(0.1)

            self.dataProducer.send('sensor_data', value = data)
            self.stop_event()

if __name__ == '__main__':
    address = str(args.broker)
    partition_id = str(args.partition)
    n = args.number_of_devices
    producer = Generate_data(address, n)
    producer.ProduceData()
