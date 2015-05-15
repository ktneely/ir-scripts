#!/usr/bin/python3

import os
from redmine import Redmine
import datetime as dt
import requests
import json

# Set variables
os.chdir(os.path.expanduser("~") + "/.incmgmt/")
prefs = []
for line in open('mw-prefs.txt'):
    prefs.append(line)
redmine_project = prefs[0].rstrip() 
redmine_server = prefs[1].rstrip() 
redmine_key = prefs[2].rstrip()
sn_server = prefs[3].rstrip() 
user = prefs[4].rstrip()
pwd = prefs[5].rstrip() 
wikipage = "https://io.arubanetworks.com/projects/incident_management/wiki/Open_SSID_access_point"  # description of how to handle this issue

# Connect to redmine
redmine = Redmine(redmine_server, requests={'verify': False}, \
                key=redmine_key, version='2.5.1')
project = redmine.project.get(redmine_project)


## Begin functions

# Create an issue in Service Now
def sn_issue(subject, redmine_url, impact, urgency, wikipage):
    # Define the headers
    headers = {"Content-Type":"application/json", \
               "Accept":"application/json"}
    # Construct JSON object containing the incident data
    incident_data = '{'  + \
        '"short_description":"' + subject + '",' + \
        '"description":' + '"A rogue access point has been discovered on the network.  For full information, see: ' + \
          redmine_url + '  and for instructions, see: ' + \
          wikipage + '",'\
        '"u_category":' + '"Intranet",' + \
        '"u_subcategory":' + '"Access Issues",' + \
        '"impact":' + '"' + str(impact)  + '",' + \
        '"urgency":' + '"' + str(urgency)  + '",' + \
        '"contact_type":"Alert"' + '}' 
    # Create the incident on the Service Now system
    response = requests.post(sn_server, auth=(sn_user, sn_pass), \
        headers=headers, data=incident_data)
    # Capture the ticket number and unique identifier
    if response.status_code != 201: 
        print('Status:', response.status_code, 'Headers:', \
            response.headers, 'Error Response:',response.json())
        exit()
    sn_ticket = response.json()['result']['number']
    sys_id = response.json()['result']['sys_id']
    print("service now ticket created")
    return sn_ticket, sys_id

# Log the created tickets to a file
def log(redmine_issue_id, sn_ticket, sys_id, redmine_url):
    # Write log file of tickets created
    ticket_log = open('ticketlog.csv','a')
    opentix_log = open('opentix.csv','a')
    ticket_log.write(redmine_issue_id + ',' + sn_ticket + ',' + \
        sys_id + ',' + redmine_url + ',' + '\n')
    opentix_log.write(redmine_issue_id + ',' + sn_ticket + ',' + \
        sys_id + '\n')
    ticket_log.close()
    opentix_log.close()


# Calculate interval for checking tickets
def timeRange(interval):
    now = dt.datetime.today()  # capture the current time
    delta = dt.timedelta(minutes=interval)  # set the interval
    diff = now - delta  # calculate the filter start time
    return diff

# Determine if the issue is in the relevant interval and create a
# service now ticket if it is
def CheckInterval(created_filter, issue):
    if issue.created_on - created_filter == abs(issue.created_on - \
                                            created_filter):
        redmine_url = redmine_server + "/issues/" + str(issue.id)
        subject = issue.subject
        sn_ticket, sys_id = sn_issue(subject, redmine_url, 2, 2, wikipage)
        log(str(issue.id), sn_ticket, sys_id, redmine_url)
    else:
        return None
        
## Begin script
# set a time filter for finding newly active tickets.
# Interval in minutes
created_filter = timeRange(30)
# Retrieve all newly-created tickets that relate to a Rogue SSID
def RetrieveTickets():
    for i in project.issues:
        try:
            if str(i.category).rstrip() == "Rogue SSID":
                CheckInterval(created_filter, i) # check if new
        except:
            pass    # ignore errors

