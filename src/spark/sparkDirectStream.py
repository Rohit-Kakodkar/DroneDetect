from argparse import ArgumentParser
from pyspark import SparkContext, SparkConf
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

def parse_args():
    '''
        Argument parser
    '''

    parser = ArgumentParser(description = 'DroneDetect')
    parser.add_argument('--broker', default='localhost:9092',\
                                help = 'List all kafka brokers')
    parser.add_argument('--topic', default='sensor-data', \
                                help = 'Topic to which spark is subscribed to')
    # parser.add_argument('--psnode', default='localhost:5432',\
    #                             help = 'Location of postgres database')
    # parser.add_argument('--dbname', default='dronedetect', \
    #                             help = 'Name of the postgres database')
    parser.add_argument('--spark_master', default='localhost', \
                                help = 'Name of master spark node')
    args = parser.parse_args()
    return args

def spark_conf(master):
    '''
        Spark config inputs to increase throughput of spark Streaming
            input - master : DNS of spark master node
            rvalue - spark_config object
    '''
    sc_conf = SparkConf()
    sc_conf.setAppName("DroneDetect")
    # sc_conf.setMaster("{}:7077".format(master))
    sc_conf.set("spark.executor.memory", "1000m")
    sc_conf.set("spark.executor.cores", "2")
    sc_conf.set("spark.executor.instances", "15")
    sc_conf.set("spark.driver.memory", "5000m")
    sc_conf.set("spark.executor.heartbeatInterval", "20")

    return sc_conf

def quiet_logs( sc ):
    logger = sc._jvm.org.apache.log4j
    logger.LogManager.getLogger("org"). setLevel( logger.Level.ERROR )
    logger.LogManager.getLogger("akka").setLevel( logger.Level.ERROR )

def get_anomalous_event(length_array):
    '''
        Generate expected anomalous signal from barometric data
    '''
    ts = np.linspace(-10, 10, length_array)
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
    '''
        Root Mean Square Error
    '''
    arr = ar1 - ar2
    return np.sqrt(np.sum(np.square(arr))/len(ar1))

def detect_barometric_anamoly(barometric_reading, TimeStamp):
    '''
        Driver function to detect barometric anamolies
    '''
    barometric_reading = np.asarray(barometric_reading)
    TimeStamp = np.asarray(TimeStamp)

    if np.amin(barometric_reading)>370:
        return False
    else:
        # Time at which the drone height is lowest

        barometric_reading, TimeStamp = [x, y for y,x in sorted(zip(TimeStamp,barometric_reading))]

        Minimum_time = TimeStamp[np.where(barometric_reading == min(barometric_reading))]

        # Define window size that you wanna pick out the data
        # i.e. window = [Minimum_time-Window_Size_Secs:Minimum_time]
        Window_Size_Secs = 10
        sliced_barometric = barometric_reading[np.where((TimeStamp > (Minimum_time - Window_Size_Secs)) & \
                                                         (TimeStamp < (Minimum_time + Window_Size_Secs)))]
        sliced_TimeStamp = TimeStamp[np.where((TimeStamp > (Minimum_time - Window_Size_Secs)) & \
                                            (TimeStamp < (Minimum_time + Window_Size_Secs)))]

        # generate expected malfunctioning device data
        length_array = sliced_barometric.size
        anomalous_event, ts = get_anomalous_event(length_array)
        # print(str(anomalous_event.size))
        # print('******************************************************************************')
        # anomalous_event = anomalous_event[np.where((ts >= (np.amin(sliced_TimeStamp) - Minimum_time)[0]) & \
        #                                             (ts <= (np.amax(sliced_TimeStamp) - Minimum_time)[0]))]

        Error = RMSE(sliced_barometric, anomalous_event)

        if Error < 20:
            return True
        else:
            return False

def process_drones(rdd):
    '''
        Driver function to process drone rdd's and select sensor data close to the event
    '''

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

        anamoly_udf = udf(detect_barometric_anamoly, BooleanType())

        malfunctioning_DF = GroupedDF.withColumn("malfunctioning", anamoly_udf("barometric_reading", "TimeStamp"))

        malfunctioning_DF = malfunctioning_DF.drop('barometric_reading')

        malfunctioning_DF.show()

        # connector = PostgresConnector()
        # connector.write(malfunctioning_DF, devices, 'overwrite')

if __name__ == '__main__':
    '''
        Main function to launch spark job
    '''

    args = parse_args()
    broker = args.broker
    topic = args.topic
    master = args.spark_master
    sc_conf = spark_conf(master)

    sc = SparkContext(conf = sc_conf).getOrCreate()
    quiet_logs(sc)
    ssc = StreamingContext(sc, 60)
    spark = SparkSession(sc)
    kafkaStream = KafkaUtils.createDirectStream(ssc, [topic], {"metadata.broker.list": broker})

    rdd = kafkaStream.map(lambda x: json.loads(x[1]))

    mappedData = rdd.map(lambda x: (int(x["device_id"]),\
                                        x["latitude"],\
                                        x["longitude"],\
                                        x["TimeStamp"],\
                                        x["barometric_reading"],\
                                        x["gyrometer_x"],\
                                        x["gyrometer_y"],\
                                        x["wind_speed"]))

    mappedData.foreachRDD(process_drones)

    ssc.start()
    ssc.awaitTermination()
