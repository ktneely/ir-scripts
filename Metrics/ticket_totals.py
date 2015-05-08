#!/usr/bin/python3

import os
import re
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import datetime as dt
import matplotlib.dates as dates


# Specify the data files and create a pandas dataframe for each
vulns_file = '/path/to/some.file'
incs_file = '/path/to/some.file'
vulns = pd.read_csv(vulns_file, index_col='created_on', parse_dates=True)
incs = pd.read_csv(incs_file, index_col='created_on', parse_dates=True)

# Create a list of interesting attributes in the dataframe
data_points = ['tracker', 'priority', 'status']

# Simple function for creating sums
def sums(df, cat):
    series = df[cat]


'''
# Function to determine the frequent internal offenders  TODO
def offenders():
    use re to extract the host IPs
    calculate totals of tickets with specific IP
    perform reverse lookup
    output a table with data
'''

'''
# function to calculate the sume of various categories  TODO
for cat in data_points:
    calculate sum
    append to df
    '''

# identify the categories of interest
web_apps = v_categories.str.contains('Web Application')
networking = v_categories.str.contains('Networking')
database = v_categories.str.contains('Database')
windows = v_categories.str.contains('Server - Windows')
unix = v_categories.str.contains('Server - UNIX')
virt = v_categories.str.contains('Virtual Infrastructure')
dos = i_categories.str.contains('Denial of Service')
docs = i_categories.str.contains('Documentation') # administrative
in_usage = i_categories.str.contains('Inappropriate Usage')
lost = i_categories.str.contains('Lost Equipment')
malware = i_categories.str.contains('Malicious Code')

# sum up the string data on a monthly basis
web_data = web_apps.astype(float).resample('M', how=np.sum).fillna('0')
net_data = networking.astype(float).resample('M', how=np.sum)
db_data = database.astype(float).resample('M', how=np.sum)
windows_data = windows.astype(float).resample('M', how=np.sum)
unix_data = unix.astype(float).resample('M', how=np.sum)
virt_data = virt.astype(float).resample('M', how=np.sum)
dos_data = dos.astype(float).resample('M', how=np.sum)
in_usage_data = in_usage.astype(float).resample('M', how=np.sum)
lost_data = lost.astype(float).resample('M', how=np.sum)
malware_data = malware.astype(float).resample('M', how=np.sum)


# Create the legend
networking.name = "Networking"
web_apps.name = "Web Apps"
db_data.name = "Database"
windows_data.name = "Windows Servers"
unix_data.name = "UNIX Servers"
virt_data.name = "Virtual Infrastructure"

# Group the df by category
vulns.groupby('category')
