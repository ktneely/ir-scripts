#!/usr/bin/python3

# A set of Python3 modules for interacting with various ticketing
# systems such as Redmine and ServiceNow

import os
import requests
from redmine import Redmine

# Set wd
os.chdir(os.path.expanduser("~") + "/.incmgmt/")

# import ticketing system info and credentials from prefs file
prefs = []
for line in open('mw-prefs.txt'):
    prefs.append(line)
rm_project = prefs[0].rstrip()    # redmine project name
rm_server = prefs[1].rstrip()  # redmine server URL
rm_key = prefs[2].rstrip()     # redmine API key
sn_server = prefs[3].rstrip()  # ServiceNow URL
sn_user = prefs[4].rstrip()    # ServiceNow username
sn_pass = prefs[5].rstrip()    # ServiceNow password

# binds to the redmine server with the API key and also retrieves the
# project for use in interacting with the system
def bindRedmine():
    redmine = Redmine(rm_server, requests={'verify': False}, \
        key=rm_key, version='2.5.1')
    project = redmine.project.get(rm_project)
    return redmine, project

## Create the incident in ServiceNow with relevant information.  This
## takes four arguments:
### subject: the short description or incident subject line
### info_url: a URL containing further information for the responder
def sn_issue(host, redmine_url, impact, urgency, wikipage):
    # Define the headers
    headers = {"Content-Type":"application/json", \
               "Accept":"application/json"}
    # Construct JSON object containing the incident data
    incident_data = '{'  + \
        '"short_description":' + '"Malware detected on: ' + host + '",' + \
        '"description":' + '"For full information, see: ' + \
          redmine_url + '  and for cleaning instructions, see: ' + \
          wikipage + '",'\
        '"u_category":' + '"Information Security",' + \
        '"u_subcategory":' + '"Malware",' + \
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
        
def CheckRMTickets(short_desc):
    # checks for an existing and active Redmine ticket, based on the
    # provided short description
    redmine, project = bindRedmine()
    i = 0
    while i < len(project.issues):
        if str(project.issues[i]) == short_desc:
            incident_id = project.issues[i].id
            print("Found a matching ticket in Redmine")
            return incident_id
        i += 1
    return None

            
def CreateRedmineTicket(subject, priority, body, category, tracker):
    redmine, project = bindRedmine()
    new_issue = redmine.issue.create(project_id = rm_project, \
         subject = subject, tracker_id = tracker, priority_id = \
         priority, description = body, category_id = category)
    redmine_issue_id = str(new_issue.id)
    redmine_url = rm_server + "/issues/" + redmine_issue_id
    print("Created ticket " + str(new_issue))
    return redmine_url, redmine_issue_id 


def UpdateRedmineTicket(ticket, notes):
    redmine.issue.update(ticket, notes = notes)
    print("Updated ticket" + str(ticket))
    return None

# Logs the ticket reference information so it can be used for
# subsequent updates.  The log files should reside in the .incmgmt
# dir. The ticket_log is a running log of all tickets created, opentix
# is the currently active tickets
def log(redmine_issue_id, sn_ticket, sys_id):
    # Write log file of tickets created
    ticket_log = open('ticketlog.csv','a')
    opentix_log = open('opentix.csv','a')
    ticket_log.write(redmine_issue_id + ',' + sn_ticket + ',' + \
        sys_id + '\n')
    opentix_log.write(redmine_issue_id + ',' + sn_ticket + ',' + \
        sys_id + '\n')
    ticket_log.close()
    opentix_log.close()


## determine criticality factors
# impact and urgency are used for Service Now
# priority is used for Redmine
def criticality(severity):
    if severity.lower() == "crit":
        impact = 2
        urgency = 1
        priority = 5
    elif severity.lower() == "majr":
        impact = 2
        urgency = 2
        priority = 4
    else:
        impact = 3
        urgency = 3
        priority = 3
    return impact, urgency, priority

