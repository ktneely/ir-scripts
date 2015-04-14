#!/usr/bin/python3

# This takes an XML report extracted from an OpenVAS VA scanner and
# creates issue tickets on ServiceNow and Redmine systems for tracking
# purposes.

# version 0.2

#modules
import requests
import socket
import os
import csv
import json
from redmine import Redmine
import xml.etree.ElementTree as ET

## Configure your environment through preferences file
# load prefs from ~/.incmgmt/prefs.txt
# The parameters should be in the following format
# DO NOT use comments or blank lines.
# Redmine Project
# Redmine URL
# Redmine API key
# ServiceNow URL
# ServiceNow username
# Servicenow password
# severity level
# OpenVAS XML report file
# Preamble: general info you want included in every ticket created

os.chdir(os.path.expanduser("~") + "/.incmgmt/")

ov_prefs = open('ov_prefs.txt','r')
redmine_project = ov_prefs.readline().rstrip()
redmine_server = ov_prefs.readline().rstrip()
redmine_key = ov_prefs.readline().rstrip()
sn_server = ov_prefs.readline().rstrip()
user = ov_prefs.readline().rstrip()
pwd = ov_prefs.readline().rstrip()
severity_filter = ov_prefs.readline().rstrip()
ov_report = ov_prefs.readline().rstrip()
preamble =  ov_prefs.readline().rstrip()
ov_prefs.close()

# Define service now headers
headers = {"Content-Type":"application/json","Accept":"application/json"}


# Input the vulnerability report and parse the XML
root = ET.parse(ov_report)

## determine criticality factors
# impact and urgency are used for Service Now
# priority is used for Redmine
def criticality(cvss):
    global impact
    global urgency
    global priority
    if float(cvss) > 7:
        impact = 2
        urgency = 1
        priority = 5
    elif float(cvss) < 4:
        impact = 3
        urgency = 3
        priority = 3
    else:
        impact = 2
        urgency = 2
        priority = 4
    return impact, urgency, priority

def reverse_lookup(ip):
    try:
        hostname = socket.gethostbyaddr(ip)[0]
    except socket.herror:
        hostname = " "
    return hostname
        

## determine category
""" Redmine reference
0 nothing
53 Database
54 Networking
56 Server - Unix
55 Server - Windows
57 Web Application  """

## Function to categorize the issue for all ticketing systems
# categoy is used for redmine, and subcategory is used for
# ServiceNow because it has a default high-level category for vulns
def categorize(family):
    if family == "Web application abuses" or "Web Servers":
        category = 57
        subcategory = "Internal Application"
    elif family == "Databases":
        category = 53
        subcategory = "Internal Application"
    elif family == "General":
        category = 56
        subcategory = "UNIX"
    elif "CentOS" in family:
        category = 56
        subcategory = "UNIX"
    elif "Windows" in family:
        category = 55
        subcategory = "Windows"
    else:
        category = 0
        subcategory = " "
    return category, subcategory

#Specify Redmine server params
redmine = Redmine(redmine_server, requests={'verify': False}, key=redmine_key, version='2.5.1')

def redmine_issue(priority, subject, body, category):
    ## Create an issue in Redmine to track the vulnerability
    # and return information regarding the created ticket
    new_issue = redmine.issue.create(project_id = redmine_project, \
        priority_id = priority, subject = subject, description = body,\
        tracker_id=19, category_id = category)
    redmine_issue_id = str(new_issue.id)
    redmine_url = redmine_server + "/issues/" + redmine_issue_id
    print("redmine ticket created")
    return redmine_url, redmine_issue_id

def sn_issue(subject, redmine_url, subcategory, impact, urgency):
    ## Create the incident in ServiceNow
    # Construct the incident JSON object
    incident_data = '{'  + \
        '"short_description":' + '"' + subject + '",' + \
        '"description":' + '"For more information, see: ' + redmine_url + '",' + \
        '"u_category":' + '"Vulnerability Management",' + \
        '"u_subcategory":' + '"' + subcategory  + '",' + \
        '"impact":' + '"' + str(impact)  + '",' + \
        '"urgency":' + '"' + str(urgency)  + '",' + \
        '"contact_type":"Alert"' + '}' 
    # Create the incident on the Service Now system
    response = requests.post(sn_server, auth=(user, pwd), \
        headers=headers, data=incident_data)
    # Capture the ticket number and unique identifier
    sn_ticket = response.json()['result']['number']
    sys_id = response.json()['result']['sys_id']
    print("service now ticket created")
    return sn_ticket, sys_id

# Update the Service Now ticket with a comment
def sn_update(sys_id, comment):
    sn_url = sn_server + '/' + sys_id  # REST URL for the ticket
    update = requests.patch(sn_url, auth=(user, pwd), headers=headers,\
            data='{"comments":"' + comment +'"}')
    if update.status_code != 200: 
        print('Status:', response.status_code, 'Headers:',\
               response.headers, 'Error Response:',response.json())
        exit()
    print("Updated Service Now ticket" + " " + sys_id)  # user output


# checks for a ticket with the exact same "subject" or "short
# description" on the Redmine system.
def CheckTickets(subject):
    i = 0
    project = redmine.project.get(redmine_project)
    while i < len(project.issues):
#        print("Checking: " + str(project.issues[i]))
        if str(project.issues[i]) == subject:
            incident_id = project.issues[i].id
            opentix_log = csv.reader(open('opentix.csv'))
            # Generate a dictionary of the known open tickets.  This
            # should really be performed at the beginning so it
            # doesn't run everytime, but meh!
            tix_dict = {}
            for row in opentix_log:
                tix_dict[row[0]]=row[2]
            sn_sysid = tix_dict[str(incident_id)]
            print("Found match: " + tix_dict[str(incident_id)] + " " + str(project.issues[i]))  # debug
            return sn_sysid # return a value for test
        i += 1
    return None  # if the test fails, return nothing
            
 
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

## Main program.  Extract the data, then call functions
# Extract elements from the XML for use in creating the ticket
for result in root.findall("./report/results/result"):
    # only process vulnerabilities of a certain severity or higher
    if result.find('overrides/override/new_severity') is not None:
        cvss = result.find('overrides/override/new_severity').text
    else:
        cvss = result.find('severity').text
    if float(cvss) >= float(severity_filter):
        # Extract the elements from the XML
        host_ip = result.find('host').text
        severity = result.find('severity').text
        description = result.find('description').text
        short_desc = result.find('nvt/name').text
        cvss = result.find('nvt/cvss_base').text
        cve = result.find('nvt/cve').text
        system_type = result.find('nvt/family')
        # get some additional info based on extracted values
        hostname = reverse_lookup(host_ip)  # perform name lookup
        impact, urgency, priority = criticality(severity)
        category, subcategory = categorize(system_type)
        full_desc = result.find('nvt/tags').text
        criticality(cvss)    # calc criticality levels
        subject = short_desc + " detected on " + hostname + " " + host_ip
        # Create the body of the ticket by combining multiple elements from 
        # the report file.
        body = preamble + "\n \n" + full_desc + "\n \n CVEs:" + cve +\
            "\n \n Description: \n" + description 
        # Check for currently active ticket for same issue.  This
        previous = CheckTickets(subject)
        # Create a new ticket if one does not exist.
        if previous is not None:
            sn_update(previous, "Please provide an update for this ticket")
        else:
            # create the issues in redmine and return info        
            redmine_url, redmine_issue_id = redmine_issue(priority, \
                subject, body, category)
            # create the issues in ServiceNow and return info
            sn_ticket, sys_id = sn_issue(subject, redmine_url, \
                subcategory, impact, urgency)
            log (redmine_issue_id, sn_ticket, sys_id, redmine_url)

