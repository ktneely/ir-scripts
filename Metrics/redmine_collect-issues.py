#!/usr/bin/python3

import os
import datetime as dt
from redmine import Redmine

# Queries a redmine server for issues created in a specific project
# and generates some basic data around those tickets for further
# analysis.
# Hard-coded to ignore issues in subprojects, so this needs
# to be run against each project to collect the information.

## Configure your environment through preferences file
## 
# load prefs from ~/.incmgmt/ov_prefs.txt
# The parameters should be in the following format
# DO NOT use comments or blank lines.
# Redmine Project
# Redmine URL
# Redmine API key

# Read prefs from the preferences file
os.chdir(os.path.expanduser("~") + "/.incmgmt/")
prefs = []
for line in open('mw-prefs.txt'):
    prefs.append(line)
redmine_server = prefs[1].rstrip()
redmine_key = prefs[2].rstrip()
redmine_project = 'incident_management'

'''
prefs = open('ov_prefs.txt','r')
redmine_project = 'incident_management' #prefs.readline().rstrip()
redmine_server = prefs.readline().rstrip()
redmine_key = prefs.readline().rstrip()
prefs.close()
'''

# The script will collect all incidents created between 'startdate'
# and 'enddate'.  Default setting below is for all the data in my
# system, YMMV
startdate = dt.date(2014, 6, 1)
enddate = dt.date.today()


# Extract data on redmine tickets, on a per-project basis.  This will
# extract the number of opened tickets, closed tickets, on a per
# category basis.
def CalculateTickets(project, startdate, enddate):
    begyear = startdate.year()
    endyear = enddate.year()
    begmonth = startdate.month()
    endmonth = enddate.month()
    
def SetRMParams(project):
    redmine =  Redmine(redmine_server, requests={'verify': False}, \
        key=redmine_key)
    return redmine

def InitializeLogFile(project):
    # Create a new CSV file for storing the ticket information and
    # create the headers.  A previously-created log file will be
    # destroyed, but this will persist after execution for manual
    # inspection.  It is stored in the ~/.incmgmt directory
    logfilename = project + '-' + str(dt.date.today()) + '.csv'
    logfile = open(logfilename, 'w')
    logfile.write("id,category,tracker,project,priority,created_on,\
updated_on,start_date,status,subject\n")
    return logfile


def CreateRedmineIssueLog(project, logfile):
    # create the file, based on project name
    # write the headers
    # pull the incident issues and write as CSV
    for issue in redmine.issue.filter(project_id = project, \
            status_id = '*'): #, subproject_id = '!*'):
        logfile.write(\
            str(issue.id) + ',' \
            + str(getattr(issue, 'category', 'Uncategorized')) + ',' \
            + str(issue.tracker) + ',' \
            + str(issue.project) + ',' \
            + str(issue.priority) + ',' \
            + str(issue.created_on) + ',' \
            + str(issue.updated_on) + ',' \
            + str(issue.start_date) + ',' \
            + str(issue.status) + ',' \
            + '"' + getattr(issue, 'subject', 'No Subject') + '"'\
            + '\n')
    
logfile = InitializeLogFile(redmine_project)   # create empty log file
redmine = SetRMParams(redmine_project)   # access the redmine server
CreateRedmineIssueLog(redmine_project, logfile) # create the data
logfile.close()   # close the logfile
