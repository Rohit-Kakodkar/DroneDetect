import argparse
from pyspark import SparkContext
from pyspark.streaming import StreamingContext
from pyspark.streaming.kafka import KafkaUtils
import json

if __name__ == '__main__':

    sc = SparkContext(appName = 'DroneDetect')
    ssc = StreamingContext(sc, 10)
    kafkaStream = KafkaUtils.createDirectStream\
                            (ssc, ['sensor-data'], {"metadata.broker.list": 'localhost:9092'})

    rdd = kafkaStream.map(lambda x: x[1])

    total_in_section = rdd.count()

    total_in_section.pprint()

    ssc.start()
    ssc.awaitTermination()
