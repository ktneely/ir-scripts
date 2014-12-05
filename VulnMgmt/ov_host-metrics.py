#!/usr/bin/python3

# Reads from a dir of OpenVAS XML reports and extracts summary information
#  Version 0.0.0.0.1   i.e. work in progress

#modules
import os
import glob
import socket
import xml.etree.ElementTree as ET

data_dir = 'Directory where Data exists'

severity_filter = 6 # arbitrary filter to limit the data
# Read the reports
os.chdir(data_dir)
reports = glob.glob('report*.xml')

total = 0
hosts = []

def reverse_lookup(ip):
    try:
        hostname = socket.gethostbyaddr(ip)[0]
    except socket.herror:
        hostname = " "
    return hostname

# Process an XML-formatted report
def parse_report(report):
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
        # get some additional info based on extracted values
#            hostname = reverse_lookup(host_ip)  # perform name lookup
#        impact, urgency, priority = criticality(severity)
#        category, subcategory = categorize(system_type)
            full_desc = result.find('nvt/tags').text
            global total; total = total + 1 
            global hosts; hosts.append(host_ip)
            print(cvss, host_ip, short_desc)

def uniqify(things):
    return list(set(things))
                                    
for report in reports:
    parse_report(report)
print("total identified vulns: " + str(total))
print("total unique hosts: " + str(len(uniqify(hosts))))


