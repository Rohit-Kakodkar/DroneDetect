#!/bin/sh

KAFKA_CLUSTER=kafka-clusters

# setup kafka using pegasus

peg up setup/kafka_master.yml
peg up setup/kafka-workers.yml
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

# your kafka cluster should now be up and running
