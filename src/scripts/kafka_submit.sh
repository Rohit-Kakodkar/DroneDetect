${HOME}/DroneDetect/src/kafka/kafka_producer.py /
--number_of_devices 300 /
--broker $KAFKA_CLUSTER_1:9092 $KAFKA_CLUSTER_2:9092 $KAFKA_CLUSTER_2:9092 /
--topic sensor-data-1
