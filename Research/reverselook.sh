#!/bin/bash
# reads a list specified on the command line and looks up
# each hostname or IP address
LIST=`grep -o '[0-9]\{1,3\}\.[0-9]\{1,3\}\.[0-9]\{1,3\}\.[0-9]\{1,3\}' $1`
for i in $LIST
do nslookup $i
done