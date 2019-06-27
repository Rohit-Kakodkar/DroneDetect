spark-submit --packages org.apache.spark:spark-streaming-kafka-0-8_2.11:2.0.0\
 --master spark://${SPARK_MASTER}:7077\
 ${HOME}/DroneDetect/src/spark/sparkDirectStream.py\
 --broker ${BROKER}\
 --topic sensor-data-1\
 --dbname ${DB_NAME}\
 --psnode ${PS_NODE}\
 --pusername ${PS_USER}\
 --password ${PS_PASS}
