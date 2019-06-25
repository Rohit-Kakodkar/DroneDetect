from events import recovery_event
import math
from datetime import datetime
from time import sleep
from json import dumps
from kafka import KafkaProducer
import numpy as np
import time
import argparse
from time import sleep
import pandas

def parse_args():

    parser = argparse.ArgumentParser(description='Data generation')
    parser.add_argument('--number_of_devices', type=int, default=1,\
                                help='Total number of drones deployed')
    parser.add_argument('--broker', type=str, default= 'localhost:9092', \
                                metavar='N', nargs = '+', help='list of brokers')
    parser.add_argument('--topic', type=str, default='sensor-data', \
                                help='topic of kafka cluster')
    parser.add_argument('--partition', type=int, default=0,
                                help="partition on which this producer should send")
    parser.add_argument('--start_id', type=int, default=0,
                                help='ID of the first device in the list')
    parser.add_argument('--faulty', type=bool, default=False,
                                help='Is this a stream from faulty devices')
    parser.add_argument('--crashed', type = bool, default=False,
                                help='Is this stream for crashed devices')
    args = parser.parse_args()

    return args

class Generate_data():
    """
        Class to simulate sensor data
            output : kafka dump of json
    """

    def __init__(self, address, n):
        """
            Intialize variables
            ndrones = Number of drones
            event_log = Logical which initiates an anomalous events
            event_log_time = time parameter for anamalous events
            __barometer_event_reading = barometric event resulting from anomalous event
        """
        self.dataProducer = KafkaProducer(bootstrap_servers=address)
        self.ndrones = n
        self.event_log = np.zeros(n, dtype = bool)
        self.__crashed_event_log = np.zeros(n, dtype = bool)
        self.__crashed_barometric_data = np.zeros(n)
        self.event_log_time = -20*np.ones(n)
        self.__barometer_event_reading = np.zeros(n)

    def Serialize_JSON(self):
        """
            Serialize datetime JSON for kafka producer
        """
        if isinstance(self.TimeStamp, datetime):
            return self.TimeStamp.__str__()

    def instantiate_event(self):
        """
            instantiate anomalous event
        """
        for i in range(self.ndrones):
            if np.random.uniform(0,1) < 0.1:
                self.event_log[i] = True

    def stop_event(self):
        """
            Stop anamalous event
        """
        for i in range(self.ndrones):
            if self.event_log[i] and self.event_log_time[i]>=20:
                self.event_log[i] = False
                self.event_log_time[i] = -20

    def update_time_log(self):
        dt = 0.1
        for i in range(self.ndrones):
            if self.event_log[i]:
                self.event_log_time += dt

    def generate_event(self):
        """
            simulate __barometer_event_reading from anamalous event
        """
        self.instantiate_event()
        self.update_time_log()
        for i in range(self.ndrones):
            if self.event_log[i]:
                ts = self.event_log_time[i]
                self.__barometer_event_reading[i] = recovery_event(0, 1, 100, ts, 1)\
                                                    .generate_altitude()

    def crashed_event(self):
        """
            Generate data from crashed drones
        """

        for i in range(self.ndrones):
            if (np.random.rand() < 0.0001) & (not self.__crashed_event_log[i]):
                self.__crashed_event_log[i] = True

        for i in range(self.ndrones):
            if self.__crashed_event_log[i]:
                self.__crashed_barometric_data[i] = -1
            else :
                self.__crashed_barometric_data[i] = np.random.randint(low = 395, high = 405)

    def ProduceData(self, topic, faulty, crashed, start_id):
        """
            Produce data and sent to kafka producer
        """
        self.TimeStamp = datetime.now()
        print(self.TimeStamp)
        while True:


            if faulty:
                self.generate_event()
            elif crashed:
                self.crashed_event()


            # baromatric_reading = np.random.uniform(395, 405, self.ndrones) + self.__barometer_event_reading
            if faulty:
                print(str(faulty))
                baromatric_reading = np.random.randint(low = 395, high = 405, size = self.ndrones) + self.__barometer_event_reading
            elif crashed:
                baromatric_reading = self.__crashed_barometric_data
            else:
                baromatric_reading = np.random.randint(low = 395, high = 405, size = self.ndrones)


            latitude = np.zeros(self.ndrones)
            longitude = np.zeros(self.ndrones)
            gyrometer_x = np.random.uniform(-0.4, 0.4, self.ndrones)
            gyrometer_y = np.random.uniform(-0.4, 0.4, self.ndrones)
            wind_speed = 55*np.ones(self.ndrones)

            # generate data for every device/drone
            start = time.time()
            for device_id in range(self.ndrones):
                data = dumps({  "device_id" : device_id+start_id,
                                "latitude" : latitude[device_id],
                                "longitude" : longitude[device_id],
                                "barometric_reading" : baromatric_reading[device_id],
                                "TimeStamp" : time.time(),
                                "gyrometer_x" : gyrometer_x[device_id],
                                "gyrometer_y" : gyrometer_y[device_id],
                                "wind_speed" : wind_speed[device_id]}).encode('utf-8')

                self.dataProducer.send(topic, value = data)

            if 0.1-(time.time()-start)>0:
                sleep(0.1-(time.time()-start))

            print(str(time.time()-start))
            self.stop_event()

if __name__ == '__main__':

    args = parse_args()
    address = args.broker
    partition_id = args.partition
    n = args.number_of_devices
    topic = args.topic
    faulty = args.faulty
    crashed = args.crashed
    start_id = args.start_id
    producer = Generate_data(address, n)
    producer.ProduceData(topic, faulty, crashed, start_id)
