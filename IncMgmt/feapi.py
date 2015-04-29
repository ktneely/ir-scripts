#!/usr/bin/python3

# FireEye CMS API interaction modules.  These are some commonly used
# functions for interacting with the FireEye CMS system.  API access
# must be enabled on the CMS system and you must have created some
# credentials with at least the api_monitor role.  Some functions may
# require the api_analyst role
#
# Results are in JSON format.  If you want XML, fork this and remove
# the 'Accept' : 'application/json' header from the calls; the API
# will use XML as the default

# Required modules
import requests
import json
from uniqify import uniqify

# Global variables  TODO: move hard requirements out of this script
baseurl = 'https://sjccms01/wsapis/v1.0.0/'


# The FireEye API works by generating a limited API token.  This must
# be retrieved by authenticating with the server with valid
# credentials, and then using the token for subsequent requests

# Authenticate against the CMS server, skipping SSL checking
def cmsauth(user, pwd):
    # Authenticate with the CMS and return a temporary API token
    authurl = baseurl + 'auth/login'
    cms = requests.post(authurl, auth=(user, pwd), verify=False)
    if cms.status_code is 200:
        print("Authentication successful")
    else:
        print("Authentication Failure")
    token = cms.headers['x-feapi-token']
    return token

def cmsalerts(token, duration):
    import sys
    # Query the system for alerts in the specified duration
    queryurl = baseurl + 'alerts?info_level=concise&duration=' + duration 
    alerts = requests.get(queryurl, verify=False, \
                          headers = {'X-FeApi-Token' : token, \
                          'Accept' : 'application/json'})
    # Decode the response to text, parse the json and return it
    data = json.loads(alerts.content.decode('utf-8'))
    # Check to see if there are alerts in the data, exit if not
    if data["alertsCount"] == 0: 
        sys.exit()
    else:
        return data

def cmsreport(token): # report_type, report_format, start, end):
    # Pulls a report from the CMS, based on time parameters
    import datetime as dt
    queryurl = baseurl + 'reports/report?report_type=mpsMalwareActivity&type=csv&frame=pastThreeMonth'
    data = requests.get(queryurl, verify=False, headers = \
            {'X-FeApi-Token' : token})
    return data.content
    # TODO - not finished

def md5search(token, md5):
    # Queries the CMS for previously-seen files matching a md5 sum
    queryurl = baseurl + 'alerts?md5=' + md5
    data = requests.get(queryurl, verify=False, headers = \
            {'X-FeApi-Token' : token, 'Accept' : 'application/json'})
    return json.loads(datalcontent.decode('utf-8'))


# The following functions are not specifically a part of the FireEye
#API, rather, they are used in conjunction with the information
#collectd from the API calls

# Generate an index of alerted-upon hosts based on their IP
#extrated from JSON-formatted alert information.  It takes 'host' as
#an argument, so the call can specify 'src' (usually internal) or
#'dst' (usually external C2 or infection vector) as the index key.
def genIndex(host, data):
    hosts = []
    i = 0
    while i < len(data["alert"]):
        hosts.append(data["alert"][i][host]["ip"])
        i += 1
    index = uniqify(hosts)
    return index


# Extract all relevant information for a particular host by iterating
# through the extracted JSON data.  This takes three arguments: the
# host of interest, the system type upon which we are pivoting
# (usually the source IP) and the extracted JSON data blob
#
# TODO: extract ALL information if a particular host appears
# more than once in the data
def ExtractFEAlerts(host, sys_type, data):
    import datetime as dt
    i = 0
    # iterate through the alerts to find the interesting host
    while i < len(data["alert"]):    
        #print(data["alert"][i][sys_type])  #DEBUG, pls remove
        # if match, collect the relevant alert data
        if str(data["alert"][i][sys_type]["ip"]) == str(host):
            try:
                hostname = data["alert"][i]["src"]["host"]
            except KeyError:
                hostname = "reverse lookup failed"
            try:
                dst = data["alert"][i]["dst"]["ip"]
            except KeyError:
                dst = "none"
            try:
                severity = data["alert"][i]["severity"]
            except KeyError:
                break # no need to continue severity = "none"
            try: 
                malware = data["alert"][i]["explanation"]\
                  ["malwareDetected"]["malware"][0]["name"]
            except TypeError:
                malware = "unknown_malware"
            try:
                activity = data["alert"][i]["name"]
            except TypeError:
                activity = "No Data"
            except KeyError:
                activity = "No Data"
            alertUrl = data["alert"][i]["alertUrl"]
            # Time extracted from the CMS is in miliseconds, so we
            # need to divide by 1000 and then convert fromtimestamp.
            # Finally, format the time in an easy-to-read way
            alerttime = dt.datetime.fromtimestamp(data["alert"][i]["occurred"] / 1000)
            time = alerttime.strftime('%Y-5m-%d %H:%M:%s')
            return dst, hostname, malware, severity, activity, \
                time, alertUrl  
        i += 1
