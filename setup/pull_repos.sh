#!/bin/bash

# clones TaxiOptimizer to the clusters, downloads necessary .jar files and installs required Python packages

KAFKA_CLUSTER=kafka-cluster

output=""
dest=/home/ubuntu/.profile


echo "Downloading remote repository"
peg sshcmd-cluster ${KAFKA_CLUSTER} "git clone -b develop https://github.com/AndreyBozhko/TaxiOptimizer"
