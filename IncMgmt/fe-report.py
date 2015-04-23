#!/usr/bin/python3

import os
from feapi import cmsauth
from feapi import cmsreport

# Set wd
os.chdir(os.path.expanduser("~") + "/.incmgmt/")

# import preferences from file and
# Extract the credentials from the relevant lines
prefs = []
for line in open('mw-prefs.txt'):
    prefs.append(line)
user = prefs[9].rstrip()
pwd = prefs[10].rstrip()

# retrieve an API token from the CMS
print("Authenticating against the CMS as " + user)
token = cmsauth(user, pwd)

# Generate and retrive the report
data = cmsreport(token)
print(data)
