import os
os.environ['PYSPARK_SUBMIT_ARGS'] = '--packages org.apache.spark:spark-streaming-kafka-0-8_2.11:2.0.2 pyspark-shell'

import findspark
findspark.init()

import argparse
from pyspark import SparkContext
from pyspark.streaming import StreamingContext
from pyspark.streaming.kafka import KafkaUtils
import json

def RMSE(rdd, ):

def 


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Spark Streaming')
    parser.add_argument('--broker', type=str, default='localhost:9092', help = 'List all kafka brokers')
    parser.add_argument('--topic', type=str, default='sensor-data', help='name of the topic to be listing for')

    sc = SparkContext(appName = 'DroneDetect')
    ssc = StreamingContext(sc, 10)
    kafkaStream = KafkaUtils.createDirectStream\
                            (ssc, ['sensor-data'], {"metadata.broker.list": 'localhost:9092'})

#    data = kafkaStream.collect()

    rdd = kafkaStream.map(lambda x: x[1]). \
                      map(lambda x: json.loads(x))



    barometric_rdd = rdd.map(lambda x: x['barometric_rdd'])
    gyrox_rdd = rdd.map(lambda x: x['gyrometer_x'])
    gyroy_rdd = rdd.map(lambda x: x['gyrometer_y'])
    wind_speed_rdd = rdd.map(lambda x: x['wind_speed'])

    ssc.start()
    ssc.awaitTermination()
