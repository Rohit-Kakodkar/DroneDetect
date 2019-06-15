#!/bin/bash

# provides every master node with the addresses of every node from other clusters

output=""
dest=/home/ubuntu/.profile

clusters=kafka-cluster


clusters=`echo $clusters | sed s/","/" "/g`


for cluster in $clusters ; do

	i=1
	CLUSTER=`echo $cluster | tr '[:lower:]' '[:upper:]' | sed s/"-"/"_"/g`
	for dns in `peg describe $cluster | grep ec2 | sed s/".*DNS: "//g` ; do

		output="$output\nexport ${CLUSTER}_$i=$dns"
		i=`expr $i + 1`

	done

done


for cluster in $clusters ; do

	echo $'$output'
	peg sshcmd-cluster $cluster "echo $'$output' >> $dest"

done
