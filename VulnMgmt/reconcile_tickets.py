#!/usr/bin/python


#modules
import requests
import os
import json
from redmine import Redmine

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

prefs = open('ov-prefs.txt','r')
redmine_project = prefs.next().rstrip()
redmine_server = prefs.next().rstrip()
redmine_key = prefs.next().rstrip()
sn_server = prefs.next().rstrip()
user = prefs.next().rstrip()
pwd = prefs.next().rstrip()
severity_filter = prefs.next().rstrip()
ov_report = prefs.next().rstrip()
preamble =  prefs.next().rstrip()
prefs.close()

ticket_log = open('ticketlog.csv','r')
Read ServiceNow and Redmine tickets from ticket_log
ticket_log.close()

def CheckSNStatus():
    

def UpdateRedmineTicket():


# Main    
for ServiceNowTicketNumber:
    check status
    update and close RedmineTicket
    
