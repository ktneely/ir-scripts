#!/usr/bin/python3

# This script checks the status of the tickets in Redmine and
# ServiceNow, closing the Redmine ticket if the ServiceNow ticket has
# been fully closed.
# Version 0.5

#modules
import requests
import os
import csv
import json
from redmine import Redmine

# set working directory for prefs and log files
os.chdir(os.path.expanduser("~") + "/.incmgmt/")

# See Readme for the preferences file parameters
prefs = open('ov_prefs.txt','r')
redmine_project = prefs.readline().rstrip()
redmine_server = prefs.readline().rstrip()
redmine_key = prefs.readline().rstrip()
sn_server = prefs.readline().rstrip()
user = prefs.readline().rstrip()
pwd = prefs.readline().rstrip()
severity_filter = prefs.readline().rstrip()
ov_report = prefs.readline().rstrip()
preamble =  prefs.readline().rstrip()
prefs.close()

# Turn off the SSL certificate warnings.  This is a less-than-stellar
# idea.  TODO: implement using the certifi package to verify the SSL
# certificate
requests.packages.urllib3.disable_warnings()

## More prefs.  Man, I need to create a proper prefs file
# identify the Redmine server parameters as an object
redmine = Redmine(redmine_server, requests={'verify': False}, \
    key=redmine_key, version='2.5.1')

ticketlogfile = 'ticketlog.csv' #log file from Vuln-tickets.py
ticketlogtmp = open('ticketlogtmp.csv','w')  # temp file for open tix

# CheckLogFile looks for a file called opentix.csv containing the
# current list of open tickets needed for processing.  See the README

def CheckLogFile():
    if os.path.isfile(ticketlogfile):    # check for ticketlog 
        if os.path.isfile('opentix.csv'):   # check for the file
            print("opentix file exists: checking tickets...")
            return None
        else:
            CreateLogFile()
    else:
        print("You need to run Vuln-tickets.py prior to running this")
        exit()

def CreateLogFile():
    print("Creating opentix.csv for tracking open tickets!")
    with open(ticketlogfile) as ticketlog:
        fields = ['rm_ticket', 'sn_ticket', 'sys_id', 'rm_url']
        reader = csv.DictReader(ticketlog, fieldnames=fields)
        opentixfile = open('opentix.csv','w')
        for row in reader:  # read in the ticket information
            rm_ticket = row['rm_ticket']
            sn_ticket = row['sn_ticket']
            sys_id = row['sys_id']
            opentixfile.write(rm_ticket + ',' + sn_ticket + \
                ',' + sys_id + '\n')
    ticketlog.close()
    opentixfile.close()

def WriteActive(rm_ticket, sn_ticket, sys_id): #maintains active tickets
    ticketlogtmp.write(rm_ticket + "," + sn_ticket + "," \
                + sys_id + "\n")
    
def CheckSNStatus(rm_ticket, sn_ticket, sys_id):
    headers = {"Content-Type":"application/json", \
               "Accept":"application/json"}
    sn_url = sn_server + '/' + sys_id
    incident = requests.get(sn_url, auth=(user, pwd), \
                headers = headers)
    if incident.status_code != 200:   # error handling for bad response
        print('Status:', incident.status_code, 'Headers:', incident.headers, 'Error Response:',incident.json())
        print("Error in retrieving ServiceNow ticket.  See above")
        exit()
    else:
        print("ServiceNow status is: " + \
            str(incident.json()['result']['u_status']))
        if incident.json()['result']['u_status'] != 'Closed':
            print("Ticket still open, writing to opentix")
            WriteActive(rm_ticket, sn_ticket, sys_id)
            return None
        else:
            CheckRMStatus(rm_ticket, sn_ticket, sys_id)
            return None

# CheckRMStatus is only called if the ServiceNow ticket is closed. 
# If it is, then this runs to also close the ticket in Redmine.
def CheckRMStatus(rm_ticket, sn_ticket, sys_id):
    incident = redmine.issue.get(rm_ticket)   # get ticket info
    status = incident.status                  # capture the status
    print("Redmine status is: " + str(status)) # output for user
    if str(status) != 'Closed':
        # Check the status of the ticket and close if still open
        print("The Redmine Ticket is still open. Closing now.")
        UpdateRedmineTicket(rm_ticket, sn_ticket)
        print("Writing to opentix for a double-check next run")
        WriteActive(rm_ticket, sn_ticket, sys_id) 
        return None
    else:
        print("Ticket already closed in Redmine. Removing.")
        return None
        
def UpdateRedmineTicket(ticket, sn_ticket):
    updatemsg = "ServiceNow ticket " + sn_ticket + " has been marked done"
    redmine.issue.update(ticket, status_id = 5, \
     notes = updatemsg)
    return None


# Main    
CheckLogFile() # Check/Create ACTIVE tickets logfile
with open('opentix.csv') as ticketlog:
    fields  = ['rm_ticket', 'sn_ticket', 'sys_id', 'rm_url']
    ticketdata = csv.DictReader(ticketlog, fieldnames=fields)
    # for each ServiceNow Ticket Number, check the status
    for row in ticketdata:  # read in the ticket information
        rm_ticket = row['rm_ticket']
        sn_ticket = row['sn_ticket']
        sys_id = row['sys_id']
        print(rm_ticket, sn_ticket)  # output current work for user
        CheckSNStatus(rm_ticket, sn_ticket, sys_id)

ticketlogtmp.close()
os.rename('ticketlogtmp.csv','opentix.csv')
