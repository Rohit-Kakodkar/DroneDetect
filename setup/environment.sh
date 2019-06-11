#!/bin/sh

#The script contains commands to setup the cluster enviroment
#It uses peg tool that can be run from local machine

KAFKA_CLUSTER=kafka-cluster
SPARK_CLUSTER=insight-cluster
DISPLAY_CLUSTER=display-cluster

source ~/.bash_profile

#kafka setup
peg up setup/spark/master_kafka.yml
peg up setup/spark/workers_kafka.yml
peg fetch ${KAFKA_CLUSTER}
peg install ${KAFKA_CLUSTER} ssh
peg install ${KAFKA_CLUSTER} aws
peg install ${KAFKA_CLUSTER} environment
peg sshcmd-cluster ${KAFKA_CLUSTER} "sudo apt-get install bc"
peg install ${KAFKA_CLUSTER} zookeeper
peg service ${KAFKA_CLUSTER} zookeeper start
peg install ${KAFKA_CLUSTER} kafka
peg service ${KAFKA_CLUSTER} kafka start
peg sshcmd-cluster ${KAFKA_CLUSTER} "sudo pip install kafka"
