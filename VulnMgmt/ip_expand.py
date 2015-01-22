#!/usr/bin/python2.7

# Takes a list of CIDR blocks (from the file 'cidr_list.txt' in /tmp),
# calculates every IP address contained within those blocks, saves
# each individual IP to a file (for use in other programs) and also
# spits out the total number of blocks and total number of addresses
# to STDOUT


#import os
import ipcalc  # requires Python 2.x

# specify resources
cidr_list = open('/tmp/cidr_list.txt', 'r')   # list of blocks
ip_list = open('/tmp/ip_list.txt', 'w')       # all the IPs
ip_count = 0                                  # tally the IPs
cidr_count = 0                                # tally the blocks


def listIPs(cidr):
    block_ips = 0
    for ip in ipcalc.Network(cidr):
        block_ips += 1
        ip_list.write(str(ip) + '\n')
    return block_ips

for block in cidr_list:
    print("Processing " + block)   # some output for the user
    cidr_count += 1
    block_ips = listIPs(block.strip())
    ip_count = ip_count + block_ips

ip_list.close()
cidr_list.close()

print("\n \n")
print("Evaluated CIDR blocks: " + str(cidr_count) + '\n')
print("Total number of addresses: " + str(ip_count))
print("List of addresses saved to /tmp/ip_list.txt")

