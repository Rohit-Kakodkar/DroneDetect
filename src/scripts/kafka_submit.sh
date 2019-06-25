python ${HOME}/DroneDetect/src/kafka/kafka_producer.py\
 --number_of_devices $1\
 --broker localhost:9092\
 --topic sensor-data\
 --crashed $2\
 --start_id $3
