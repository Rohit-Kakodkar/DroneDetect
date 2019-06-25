python ${HOME}/DroneDetect/src/kafka/kafka_producer.py\
 --number_of_devices $1\
 --broker ${KAFKA_CLUSTER_1}:9092 ${KAFKA_CLUSTER_2}:9092 ${KAFKA_CLUSTER_3}:9092\
 --topic sensor-data-1\
 --faulty $2\
 --crashed $3\
 --start_id $4
