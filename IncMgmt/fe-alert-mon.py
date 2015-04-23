#!/usr/bin/python3

# This monitors the FireEye CMS for new malware alerts and then
# creates tickets in the ServiceNow and Redmine systems

import os
from feapi import cmsauth
from feapi import cmsalerts
from feapi import genIndex
from feapi import ExtractFEAlerts
import ticketing as tkt
#from ticketing import CheckRMTickets

# Set wd
os.chdir(os.path.expanduser("~") + "/.incmgmt/")


# import preferences from file and
# Extract the credentials from the relevant lines
prefs = []
for line in open('mw-prefs.txt'):
    prefs.append(line)
user = prefs[9].rstrip()
pwd = prefs[10].rstrip()

# Set the proper category. In my installation, #61 is "Malicious Code"
category = 61  

# retrieve an API token from the CMS
print("Authenticating against the CMS as " + user)
token = cmsauth(user, pwd)

# retrieve alerts from the past hour
data = cmsalerts(token, "24_hours")

index = genIndex("src", data)
for host in index:
    print("\n \n processing: " + host)
    dst, hostname, malware, severity, activity, time, alert_url = \
      ExtractFEAlerts(host, "src", data)
    print(host  + " was observed communicating with " + dst + " criticality:  " + severity + " And type: " + activity + " with malware: " + malware)
    old = tkt.CheckRMTickets("Malicious code activity detected on " + host)
    if old is not None:
        # If there is an active ticket, update it with new info
        print("A Redmine ticket exists for this host " + old)
    else:
        # If there is no existing ticket, create one
        print("No ticket exists, working to fix that\n")
        # construct the subject/short description
        subject = "Malicious code activity detected on " + hos
        # determine criticality for ticketing systems based on sev
        impact, urgency, priority = tkt.criticality(severity)
        # construct the body of the ticket from the alert information
        body = "Information Security network monintoring devices \
        have identified a potential compromise on the network. \n \
        Please check the following system for the following: \n \
        * Affected Host: " + host + "\n" \
        "* Last identified hostname: " + hostname + " (please verify)\n" \
        "* Destination: " + dst + "\n" \
        "* Malware family: [[" + malware + "]] \n" \ 
        "* Activity Observed: " + activity + "\n" \
        "* Detection Occurred at: " + time + "\n" \
        "* FireEye alert URL: " + alert_url + "\n \n" # \
        # TODO:  add some OS-INT lookups into the ticket
        # "Open Source Intel: \n" + intel + "\n"
        rm_url, rm_issue = tkt.CreateRedmineTicket(subject, priority,\
                body, category)
        # URL for the Wiki page related to the detected malware family
        wikipage = rm_server + "/projects/incident_management/wiki/" \
          + malware.translate({ord(i):None for i in '.'})
        sn_ticket, sys_id = tkt.sn_issue(subject, rm_url, impact, \
                        urgency, wikipage)
        tkt.log(rm_issue, sn_ticket, sys_id)  # log the ticket info
