#!/bin/bash

$FLASK_NODE=flask-node

peg up flask_app.yml
peg up kafka-workers.yml
peg fetch ${KAFKA_CLUSTER}
peg install ${KAFKA_CLUSTER} ssh
peg install ${KAFKA_CLUSTER} aws
peg install ${KAFKA_CLUSTER} environment
peg sshcmd ${FLASK_NODE} 'sudo pip install Flask'
