#!/bin/bash

# install kafka on instance
wget http://mirror.metrocast.net/apache/kafka/2.2.0/kafka_2.12-2.2.0.tgz
tar -xzf kafka_2.12-2.2.0.tgz

#!/bin/sh

touch zookeeper-logs
touch kafka-logs

# start zookeeper
cd kafka_2.12-2.2.0/
nohup bin/zookeeper-server-start.sh config/zookeeper.properties > ~/zookeeper-logs &

# start kafka-broker
nohup bin/kafka-server-start.sh config/server.properties > ~/kafka-logs &

cd ~
