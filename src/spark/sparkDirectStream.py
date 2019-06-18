# import sys
# import os
# sys.path.insert(0, '/home/rohit/DroneDetect/src/utility')

import argparse
from pyspark import SparkContext
from pyspark.streaming import StreamingContext
from pyspark.streaming.kafka import KafkaUtils
from pyspark.sql import SQLContext
from pyspark.sql import SparkSession
import pyspark.sql.functions as f
from pyspark.sql.functions import udf
from pyspark.sql.types import FloatType, BooleanType, IntegerType
import time
import json
import numpy as np
import scipy.stats as stats
import math
import pgConnector

def quiet_logs( sc ):
    logger = sc._jvm.org.apache.log4j
    logger.LogManager.getLogger("org"). setLevel( logger.Level.ERROR )
    logger.LogManager.getLogger("akka").setLevel( logger.Level.ERROR )

def get_min(ar1, ar2):
    return (min(ar1))

def get_anomalous_event(length_array):

    ts = np.linspace(-10, 10, 200)
    speed = 1
    mu = 1
    variance = 1
    sigma = np.sqrt(variance)
    drop = 100
    y_ideal=[]
    for t in ts:
        y_ideal.append(400 - drop * stats.norm.pdf(t*speed, mu, sigma))

    return np.array(y_ideal), np.array(ts)

def RMSE(ar1, ar2):
    arr = ar1 - ar2
    return np.sqrt(np.sum(np.square(arr))/len(ar1))

def detect_anamoly(barometric_reading, TimeStamp):

    barometric_reading = np.asarray(barometric_reading)
    TimeStamp = np.asarray(TimeStamp)


    if np.amin(barometric_reading)>370:
        return False
    else:
    #     # Time at which the drone height is lowest
        Minimum_time = TimeStamp[np.where(barometric_reading == min(barometric_reading))]

        Window_Size_Secs = 10
        sliced_barometric = barometric_reading[np.where((TimeStamp > (Minimum_time - Window_Size_Secs)) & \
                                                         (TimeStamp < (Minimum_time + Window_Size_Secs)))]
        sliced_TimeStamp = TimeStamp[np.where((TimeStamp > (Minimum_time - Window_Size_Secs)) & \
                                            (TimeStamp < (Minimum_time + Window_Size_Secs)))]

        length_array = barometric_reading.size
        anomalous_event, ts = get_anomalous_event(length_array)

        anomalous_event = anomalous_event[np.where((ts >= (np.amin(sliced_TimeStamp) - Minimum_time)[0]) & \
                                                    (ts <= (np.amax(sliced_TimeStamp) - Minimum_time)[0]))]
        #
        if sliced_barometric.size > anomalous_event.size:
            sliced_barometric = sliced_barometric[:anomalous_event.size]
        elif anomalous_event.size > sliced_barometric.size:
            anomalous_event = anomalous_event[:sliced_barometric.size]

        Error = RMSE(sliced_barometric, anomalous_event)

        if Error < 12:
            return True
        else:
            return False

def testing(rdd):

    if rdd.isEmpty():
	       print("RDD is empty")
    else:
        df = rdd.toDF()
        df = df.selectExpr("_1 as device_id",\
                            "_2 as TimeStamp",\
                            "_3 as barometric_reading", \
                            "_4 as gyrometer_x",\
                            "_5 as gyrometer_y",\
                            "_6 as wind_speed")

        GroupedDF = df.groupBy("device_id").agg(f.collect_list('barometric_reading').\
                                alias('barometric_reading'),\
                                 f.collect_list('TimeStamp').\
                                 alias('TimeStamp'))
        GroupedDF.show()
        #
        minimum_udf = udf(get_min, FloatType())
        anamoly_udf = udf(detect_anamoly, BooleanType())
        # # count_udf = udf(get_count, IntegerType())
        #

        Minimum_DF = GroupedDF.withColumn("min", minimum_udf("barometric_reading", "TimeStamp")).\
                                withColumn("Error", anamoly_udf("barometric_reading", "TimeStamp"))
                                # withColumn("Anamoly", anamoly_udf("barometric_reading")).\
                                # withColumn("count", count_udf("barometric_reading"))

        Minimum_DF = Minimum_DF.drop(['baromatric_reading', 'TimeStamp', 'min'])

        Minimum_DF.show()

        # connector = PostgresConnector()
        # connector.write(Minimum_DF, devices, 'Overwrite')






    # print(GroupedDF['count'])
    #
    #
    # total_values = df.groupBy("device_id").barometric_reading
    # total_values.pprint()


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Spark Streaming')
    parser.add_argument('--broker', type=str, default='localhost:9092', help = 'List all kafka brokers')
    parser.add_argument('--topic', type=str, default='sensor-data', help='name of the topic to be listing for')

    sc = SparkContext(appName = 'DroneDetect').getOrCreate()
    quiet_logs(sc)
    ssc = StreamingContext(sc, 60)
    spark = SparkSession(sc)
    kafkaStream = KafkaUtils.createDirectStream(ssc, ['sensor-data'], {"metadata.broker.list": 'localhost:9092'})

#    data = kafkaStream.collect()

    rdd = kafkaStream.map(lambda x: json.loads(x[1]))

    mappedData = rdd.map(lambda x: (int(x["device_id"]),x['TimeStamp'],x["baromatric_reading"],x["gyrometer_x"], x["gyrometer_y"],x['wind_speed']))


    mappedData.foreachRDD(testing)

    # barometric_rdd = rdd.map(lambda x: x['baromatric_reading'])
    # gyrox_rdd = rdd.map(lambda x: x['gyrometer_x'])
    # gyroy_rdd = rdd.map(lambda x: x['gyrometer_y'])
    # wind_speed_rdd = rdd.map(lambda x: x['wind_speed'])
    #
    # barometric_rdd.count().pprint()

    ssc.start()
    ssc.awaitTermination()
