#!/usr/bin/python3

# Reads from a dir of OpenVAS XML reports and extracts summary information
#  Version 0.0.0.0.1   i.e. work in progress

#modules
import os
import glob
import socket
import xml.etree.ElementTree as ET

#data_dir = 'Directory where Data exists'
data_dir = '/media/sf_Aruba/InfoSec/Metrics/Data/OpenVAS/External'
#severity_filter = 2 # filter the data; 0 = all
months = ['2014-09', '2014-10', '2014-11', '2015-01', '2015-02']
severities = {'All':0, 'Low':2, 'Medium':4, 'High':7 }
# Read the reports
os.chdir(data_dir)

# Function to address the reports on a monthly basis.  Reports must be
# named "report-YYYY-MM" until I stop being lazy and fix that issue
def get_reports(month):
    period = 'report-' + month + '-*.xml'
    return glob.glob(period)

# In the future, I need to construct a pd.Dataframe from the data.
#But that is hard and I don't have the time to do that right now, so
#brute force, it is!!
# columns = ['cvss', 'host_ip', 'system_type', 'cve'] #pandas.df cols

def reverse_lookup(ip):
    try:
        hostname = socket.gethostbyaddr(ip)[0]
    except socket.herror:
        hostname = " "
    return hostname

# Process an XML-formatted report
def parse_report(report, severity_filter):
    vulns = 0
    root = ET.parse(report)
    for result in root.findall("./report/results/result"):
    # only process vulnerabilities of a certain severity or higher
        if result.find('overrides/override/new_severity') is not None:
            cvss = result.find('overrides/override/new_severity').text
        else:
            cvss = result.find('nvt/cvss_base').text
        if float(cvss) >= severity_filter:
            # Extract the elements from the XML
            host_ip = result.find('host').text
            severity = result.find('severity').text  # not used?
            short_desc = result.find('nvt/name').text
            cvss = result.find('nvt/cvss_base').text
            cve = result.find('nvt/cve').text
            system_type = result.find('nvt/family')
            full_desc = result.find('nvt/tags').text
            vulns += 1 
            hosts.append(host_ip)
#            print(host_ip, short_desc)  # debug
    return vulns, hosts


def uniqify(things):
    return list(set(things))

for month in months:
    reports = get_reports(month)
    print("Reporting period: " + month)
    for i in severities:
        total = 0
        hosts = []
        print("Severity: " + i)
        for report in reports:
            total_add, hosts_add = parse_report(report, severities[i])
            total += total_add
            hosts = hosts + hosts_add
        print("total identified vulns: " + str(total))
        print("total unique hosts: " + str(len(uniqify(hosts))))



