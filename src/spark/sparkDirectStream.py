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
from time import sleep
from scipy import interpolate
from pgConnector import PostgresConnector

parser = ArgumentParser(description = 'DroneDetect')
parser.add_argument('--broker', default='localhost:9092',\
                            help = 'List all kafka brokers')
parser.add_argument('--topic', default='sensor-data', \
                            help = 'Topic to which spark is subscribed to')
parser.add_argument('--psnode', default='localhost:5432',\
                            help = 'Location of postgres database')
parser.add_argument('--dbname', default='dronedetect', \
                            help = 'Name of the postgres database')
parser.add_argument('--pusername', default='default',
                            help = 'Your postgres username')
parser.add_argument('--password', default='password',
                            help = 'postgres password')
parser.add_argument('--spark_master', default='localhost', \
                            help = 'Name of master spark node')
args = parser.parse_args()


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

    return sc_conf

def quiet_logs( sc ):
    logger = sc._jvm.org.apache.log4j
    logger.LogManager.getLogger("org"). setLevel( logger.Level.ERROR )
    logger.LogManager.getLogger("akka").setLevel( logger.Level.ERROR )

def get_min(barometric_reading):
    return float(min(barometric_reading))

def get_anomalous_event(length_array):
    '''
        Generate expected anomalous signal from barometric data
    '''
    ts = np.linspace(-10, 10, length_array)
    speed = 2
    mu = 0
    variance = 1
    sigma = math.sqrt(variance)
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
        return float(0.0)
        # return False
    elif np.amin(barometric_reading)<0:
        return float(0.0)
        # return False
    else :
        # Time at which the drone height is lowest

        sorted_TimeStamp = TimeStamp.argsort()
        barometric_reading = barometric_reading[sorted_TimeStamp]
        TimeStamp = TimeStamp[sorted_TimeStamp]

        Minimum_time = TimeStamp[np.where(barometric_reading == np.amin(barometric_reading))]
        Mid_time = TimeStamp[int(TimeStamp.size/2)]

        # Define window size that you wanna pick out the data
        # i.e. window = [Minimum_time-Window_Size_Secs:Minimum_time]
        Window_Size_Secs = 10
        sliced_barometric = barometric_reading[np.where((TimeStamp > (Minimum_time - Window_Size_Secs)) & \
                                                         (TimeStamp < (Minimum_time + Window_Size_Secs)))]
        sliced_TimeStamp = TimeStamp[np.where((TimeStamp > (Minimum_time - Window_Size_Secs)) & \
                                            (TimeStamp < (Minimum_time + Window_Size_Secs)))]

        # generate expected malfunctioning device data
        length_array = TimeStamp[np.where((TimeStamp > (Mid_time - Window_Size_Secs)) & \
                                            (TimeStamp < (Mid_time + Window_Size_Secs)))].size
        anomalous_event, ts = get_anomalous_event(length_array)
        sliced_anomalous = anomalous_event[np.where((ts > (np.amin(sliced_TimeStamp) - Minimum_time)[0]) & \
                                                     (ts <= (np.amax(sliced_TimeStamp) - Minimum_time)[0]))]
        sliced_ts = ts[np.where((ts > (np.amin(sliced_TimeStamp) - Minimum_time)[0]) & \
                                                     (ts <= (np.amax(sliced_TimeStamp) - Minimum_time)[0]))]

        f = interpolate.interp1d(np.linspace(0,1,len(sliced_anomalous)), sliced_anomalous)

        x = np.linspace(0, 1, sliced_barometric.size)
        compare_anomalous = f(x)

        Error = RMSE((sliced_barometric), compare_anomalous)

        # return float(Error)
        # if Error < 10:
        #     return True
        # else:
        #     return False

def detect_crashed_drones(baromatric_reading):
    """
        Function to detect crashed drones
    """

    if np.amin(baromatric_reading) < 0:
        return True
    else :
        return False

def process_drones(rdd):
    '''
        Driver function to process drone rdd's and select sensor data close to the event
    '''

    if rdd.isEmpty():
	       print("RDD is empty")
    else:
        s3_bucket='s3a://dronesensordata/drone_detect_data'
        df = rdd.toDF()
        df = df.selectExpr("_1 as device_id",\
                            "_2 as latitude",\
                            "_3 as longitude",\
                            "_4 as TimeStamp",\
                            "_5 as barometric_reading", \
                            "_6 as gyrometer_x",\
                            "_7 as gyrometer_y",\
                            "_8 as wind_speed")

        GroupedDF = df.groupBy("device_id").agg(f.collect_list('barometric_reading').\
                                alias('barometric_reading'),\
                                f.collect_list('latitude').\
                                alias('latitude'),\
                                f.collect_list('longitude').\
                                alias('longitude'),\
                                f.collect_list('gyrometer_x').\
                                alias('gyrometer_x'),\
                                f.collect_list('gyrometer_y').\
                                alias('gyrometer_y'),\
                                f.collect_list('wind_speed').\
                                alias('wind_speed'),\
                                f.collect_list('TimeStamp').\
                                alias('TimeStamp'))

        anamoly_udf = udf(detect_barometric_anamoly, FloatType())
        crashed_udf = udf(detect_crashed_drones, BooleanType())
        minimum_udf = udf(get_min, FloatType())

        processed_DF = GroupedDF.withColumn("malfunctioning", anamoly_udf("barometric_reading", \
                                                                            "TimeStamp")) \
                                .withColumn("crashed", crashed_udf("barometric_reading"))

        # crashed_DF = processed_DF.filter(processed_DF['malfunctioning'])

        processed_DF.show()

        Total_number = crashed_DF.count()

        # malfunctioning_DF.coalesce(2)\
        #                  .write\
        #                  .mode('append')\
        #                  .parquet('{}/malfunctioning_devices_sensor_data.parquet'.format(s3_bucket))

        # print('Total Number of partitions = {}'.format(crashed_DF.rdd.getNumPartitions()))
        #
        # print('Total number of malfunctioning = {}'.format(Total_number))

        processed_DF = processed_DF.drop('barometric_reading')
        processed_DF = processed_DF.drop('latitude')
        processed_DF = processed_DF.drop('longitude')
        processed_DF = processed_DF.drop('gyrometer_x')
        processed_DF = processed_DF.drop('gyrometer_y')
        processed_DF = processed_DF.drop('wind_speed')
        processed_DF = processed_DF.drop('TimeStamp')

        # connector = PostgresConnector(args.psnode, args.dbname, args.pusername, args.password)
        # connector.write(processed_DF, 'devices', 'overwrite')

if __name__ == '__main__':
    '''
        Main function to launch spark job
    '''
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
