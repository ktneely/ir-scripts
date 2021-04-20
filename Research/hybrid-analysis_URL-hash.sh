#!/bin/bash
# Reads a list of URL Hashes from a file and looks them up on Hybrid Analysis
# Returns the URL
#
# MUST have the VxAPI available and configured:
# Depends on:  https://github.com/PayloadSecurity/VxAPI
# Run in same directory as VxAPI

LIST=`cat $1`



# move previous run, overwriting ones that occurred before
#rm output.csv
mv output.csv output_previous.csv

for HASH in $LIST
do
    echo "processing $HASH"
    ./vxapi.py search_hash $HASH > data.txt
#    cat $DATA
    URL=`grep '"url":' data.txt | awk -F'"' '{print $4}'`
    IPArray=(`grep -o '[0-9]\{1,3\}\.[0-9]\{1,3\}\.[0-9]\{1,3\}\.[0-9]\{1,3\}' data.txt`) # create matrix of IPs
    IPSTRING=`for val in "${IPArray[@]}"; do echo -n "$val,"; done`   # flatten IPs into comma-delimited string
    echo "$HASH,$URL,$IPSTRING" >> output.csv   # save the data
    sleep 15
done


# Cleanup
rm data.txt
