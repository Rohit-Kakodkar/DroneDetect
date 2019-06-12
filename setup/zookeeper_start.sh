#!/bin/sh

touch zookeeper-logs

# start zookeeper
cd kafka_2.12-2.2.0/
nohup bin/zookeeper-server-start.sh config/zookeeper.properties > ~/zookeeper-logs &
