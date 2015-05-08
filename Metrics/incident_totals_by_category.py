#!/usr/bin/python3

import os
import pandas as pd
import datetime as dt
import matplotlib.dates as dates

# Specify the source data
ticket_data = 'path/to/data.file'

tickets = pd.read_csv(ticket_Data, index_col = 'created_on', parse_dates=True)
vuln_cats = ['Networking', 'Server - UNIX', 'Server - Windows', \
              'Virtual Infrastructure', 'Database', 'Web Application']
inc_cats = ['Denial of Service', 'Inappropriate Usage', \
            'Lost Equipment', 'Malicious Code', 'Uncategorized']

pd.options.display.mpl_style = 'default'
inc_totals = pd.DataFrame()
monthly_totals = pd.DataFrame()
for category in vuln_cats:
    cat_match = tickets['category'] == category
    print("Processing Vulnerabilty data for: " + category)
    monthly_totals[category] = cat_match.astype(int).resample('M', how=np.sum).fillna('0')
 
for category in inc_cats:
    cat_match = tickets['category'] == category
    inc_totals[category] = cat_match.astype(int).resample('M', how=np.sum).fillna('0')
 
    
def create_barplot(data):
    fig = plt.figure(figsize=(14,10))
    ax = fig.add_subplot(111)
    data.plot(kind='bar', figsize=(12,10), ax=ax)
    #ax.set_xticklabels([dt.strftime('%m-%Y') for dt in tickets.index.to_pydatetime()])
    fig, ax = plt.subplots()
    #ax.plot_date(tickets.index.to_pydatetime(), [10,20,30,40,50,60,70,80,90], ydate=False)
    ax.xaxis.set_minor_formatter(dates.DateFormatter('%m-%Y'))
    ax.xaxis.grid(True, which="minor")
    ax.xaxis.set_major_locator(dates.MonthLocator())
    ax.xaxis.set_major_formatter(dates.DateFormatter('%m-%Y'))

create_barplot(monthly_totals)
create_barplot(inc_totals)

# TODO: save those pretty pictures to a file
