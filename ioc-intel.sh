#! /bin/bash

# This script performs some quick lookups against a list of ip address
# or FQDN IOCs and prints to stdout 
# 
# Pre-requisite: 
 # a configured CIF client with access to a CIF repository
 # https://code.google.com/p/collective-intelligence-framework/
 #
 # nping (nmap.com/nping) if you want to be noisy
#
# Actions: 
 # name lookup
 # CYMRU ASN network lookup
 # cif query
#
# Usage:  ./ioc-intel.sh <file containing list of IOCs, one per line>
#
# TODO:
 # - better output handling, rather than just stdout
 # - add command-line options for more advanced functions
 # - filter out home domains
 # - add command-line option for filtering

# BEGIN SCRIPT
# create the work list from the specified filed and ignore RFC1918 IPs
LIST=`egrep -v '(^127\.0\.0\.1)|(^192\.168)|(^10\.)|(^172\.1[6-9])|(^172\.2[0-9])|(^172\.3[0-1])' $1`

echo "start time"
date 
# perform the lookups
for ioc in $LIST; do
  echo " "
  echo "processing IOC $ioc"
  echo "--------------------------------"
  # name lookup
  echo "host resolution"
  nslookup $ioc 8.8.8.8 |egrep -i 'Name|Address' 
  # CYMRU lookup
  echo "CYMRU ASN lookup"
  whois -h whois.cymru.com $ioc
  # CIF lookup
  echo "query CIF database for indications of compromise"
  cif -q $ioc
  echo "check for host availability on port 80"
  #this test is very noisy and should only be used when stealth is not required
  nping --tcp-connect -p 80 --flags rst -c 1 $ioc 
  echo " "
done
 
echo "finish time"
date 

# fin
