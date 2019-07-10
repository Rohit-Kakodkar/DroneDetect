#!/bin/sh

SPARK_CLUSTER=kafka-cluster

# setup spark using pegasus

peg up spark_master.yml
peg up spark-workers.yml
peg fetch ${SPARK_CLUSTER}
peg install ${SPARK_CLUSTER} ssh
peg install ${SPARK_CLUSTER} aws
peg install ${SPARK_CLUSTER} environment
peg sshcmd-cluster ${SPARK_CLUSTER} "sudo apt-get install bc"
peg install ${SPARK_CLUSTER} hadoop
peg service ${SPARK_CLUSTER} hadoop start
peg install ${SPARK_CLUSTER} spark
peg service ${SPARK_CLUSTER} spark start

# your spark cluster should now be up and running
