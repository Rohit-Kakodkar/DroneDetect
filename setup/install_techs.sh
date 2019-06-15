#!/bin/bash


##--------------------------------------------------------
# Define your cluster names as named in .yml files
KAFKA_CLUSTER=kafka-cluster
#---------------------------------------------------------

## Fetch kafka-cluster ips
peg fetch ${KAFKA_CLUSTER}

# Install these if you're setting up cluster for first time
# otherwise comment these out
for tech in ssh aws environment ; do
  peg install ${KAFKA_CLUSTER} $tech
done


# Install kafka and zookeeper
for tech in zookeeper kafka ; do
  peg install ${KAFKA_CLUSTER} $tech
done

# Find number of nodes in kafka-cluster
NUMBER_OF_NODES=`peg describe kafka-cluster | grep ec2 | wc -l`

# Add NUMBER_OF_NODES to .profile
dest=/home/ubuntu/.profile
peg sshcmd-cluster ${KAFKA_CLUSTER} "echo 'export NUMBER_OF_NODES=${NUMBER_OF_NODES}' >> $dest"
