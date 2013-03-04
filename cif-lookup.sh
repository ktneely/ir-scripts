#! /bin/bash                                                                    

# a simple query against cif server(s) for matches on suspect IPs                  

# create the work list from the specified filed and ignore RFC1918 IPs
LIST=`egrep -v '(^127\.0\.0\.1)|(^192\.168)|(^10\.)|(^172\.1[6-9])|(^172\.2[0-9\
])|(^172\.3[0-1])' $1`

# query known CIF servers 
for ioc in $LIST; do
    echo "processing IOC $ioc"
    if [[ -n $(cif $ioc) ]]; then
        echo "Match found on local cif server"
    else
        echo "no match on local cif server"
    fi
    if [[ -n $(cif -C ~/.cif2 $ioc) ]]; then
	echo "Match found on remote cif serer"
    else
	echo "no match on remote cif server"
    fi
  done
