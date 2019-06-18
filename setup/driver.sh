#!/bin/bash

# Driver script to setup and start zookeeper and kafka clusters

SETUP_DEST="/home/rohit/DroneDetect/setup"

peg up $SETUP_DEST/master.yml
peg up $SETUP_DEST/workers.yml

bash $SETUP_DEST/copy_idrsapub_to_workers.sh
bash $SETUP_DEST/copy_allnodesdns_to_master.sh

bash $SETUP_DEST/install_techs.sh
#
# bash pull_repos.sh
#
# peg sshcmd-cluster ${KAFKA_CLUSTER} "bash ~/DroneDetect/setup/fix_zookeeper.sh"
