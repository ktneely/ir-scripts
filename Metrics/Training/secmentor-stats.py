#!/usr/bin/python3

# This script reads a directory of "completed" and "not started"
# training reports exported from the online Security Mentor web-based
# training service.  It then calculates a number of metrics and graphs
# based on those reports.


import os
import re
import glob
import datetime as dt
import pandas as pd
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.lines import Line2D 


# General Options and settings
# Make Pandas plots prettier
pd.options.display.mpl_style = 'default'
a = 0.7 # transparency for figures
today = dt.date.today()

# For diplay when running in iPython3 Notebook
# %matplotlib inline

# Ingest the data
data_dir = '/path/to/data/dir'
os.chdir(data_dir)

t_files = glob.glob('trainees-completed*.csv') # identify complete logs
u_files = glob.glob('trainees-not-started*.csv') # identify not started logs

# Take all the files in the directory and combine into one pd.DataFrame
def merge_logs(data_files, index):
    df_master = pd.DataFrame()  # empty "master" dataframe
    data_list = []    # empty list for all dataframes
    if index is not None:
        for files in data_files:
            df = pd.read_csv(files, header=0, encoding='latin-1', index_col=[index], parse_dates=True)
            data_list.append(df)
        df_master = pd.concat(data_list)  #merge the data into the master dataframe
        return df_master
    else:
        for files in data_files:
            df = pd.read_csv(files, header=0, encoding='latin-1', parse_dates = True)
            data_list.append(df)
        df_master = pd.concat(data_list)  #merge the data into the master dataframe
        return df_master
            


# return a list of all unique values in a given series 
def active_lessons(df, category):
    topics = []  # initialize an empty list to store the topics
    for i in df[category]:
        topics.append(i)
    return list(set(topics))# return only the unique values


t_data = merge_logs(t_files, 'Completed') # combine all log files
u_data = merge_logs(u_files, None)
topics = active_lessons(t_data, 'Lesson Topic') # extract topics

fig_tots = plt.figure(figsize=(14,10))
# Add a subplot
ax_tots = fig_tots.add_subplot(111)
xlab_tots = "Awareness Lesson"  # Set X-axis label


# Calculate the total completed and incomplete per lesson
totals = pd.DataFrame({ 'Completed': t_data.groupby(t_data['Lesson Topic']).count()['Email'],\
                        'Incomplete': u_data.groupby(u_data['Lesson Topic']).count()['Email']})

plot_tots = totals.plot(kind='bar', title="Complete vs. Incomplete by\
     Lesson", figsize=(12,10), ax=ax_tots)
ax_tots.set_xlabel(xlab_tots, fontsize=20, alpha=a, ha='left')

# Customize title
ax_tots.set_title(ax_tots.get_title(), fontsize=26, ha='left')
plt.subplots_adjust(top=0.9)
ax_tots.title.set_position((0,1.08))

fig_tots = plot_tots.get_figure()
fig_tots.savefig("/tmp/lesson_totals" + str(today) + ".png")

# Calculate completions by topic on a monthly basis

def lesson_complete(df, topic):
    series = df['Lesson Topic']
    lesson = series.str.contains(topic)
    lesson_data = lesson.astype(float).resample('M', how=np.sum)
    return lesson_data

# Convert the qualitative data to quantitative
# create a new dataframe to hold the monthly totals
df_progress = pd.DataFrame()
for topic in topics:
    print("Processing " + topic)  #feedback for debug
    df_progress[topic] = lesson_complete(t_data, topic)

#topic_order = ['Intro to Security Awareness', 'Mobile Security', 'Passwords']
#mapping = {topics: i for i, topics in ennumerate(topic_order)}
#key = df_progress[df_progress.index().map(mapping)
#df_progress.iloc(topic_order.argsort())
# calculate cumulative sums of the lessons completed and plot
#df_progress

# Title
ttl_coms = "Monthly Total Completions by Topic"
fig_coms = plt.figure(figsize=(14,10))
# Add a subplot
ax = fig_coms.add_subplot(111)

plot_coms = df_progress.cumsum().plot(kind='bar', title=ttl_coms,\
            figsize=(12,10), ax=ax, alpha=a)#,\
                    #xlim=(0,max(df_progress)))

fig_coms = plot_coms.get_figure()


# Customize the figure

# Create a horizontal bar plot
ax.grid(axis='y')  # remove X gridline
ax.set_frame_on(False)  # no plot frame
# Customize title, set position, allow space on top of plot for title
ax.set_title(ax.get_title(), fontsize=26, alpha=a, ha='left')
plt.subplots_adjust(top=0.9)
ax.title.set_position((0,1.08))

#dates = pd.date_range('2014-10-10', '2015-02-01')
#xticks = [dates]
#ax_coms.xaxis.set_ticks(xticks)
#ax_coms.set_xticklabels(xticks, fontsize=16, alpha=a)

#ax.set_xlabel(xlab, fontsize=20, alpha=a, ha='left')
#ax.xaxis.set_label_coords(0, 1.04)

# Position x tick labels on top
ax.xaxis.tick_top()
# Remove tick lines in x and y axes
ax.yaxis.set_ticks_position('none')
ax.xaxis.set_ticks_position('bottom')

ax.grid(axis='x')

# Customize x tick lables
#xticks = [item.get_xticklabels for item in ax.get_xticklabels()]
#ax.xaxis.set_ticks(xticks)
#ax.set_xticklabels(xticks, fontsize=16, alpha=a)


# Customize y tick labels
#yticks = [item.get_text() for item in ax.get_yticklabels()]
yticks = [50, 100, 150, 200, 250, 300, 350, 400, 450, 500]
ax.set_yticklabels(yticks, fontsize=16, alpha=a)
ax.yaxis.set_tick_params(pad=12)

fig_coms.savefig("/tmp/completions-by-month" + str(today) + ".png")


# Add a new series for Department name and populate by performing
# partial matches against a lookup dictionary

group_to_OU = {'Eng':'Engineering', 'ales':'Sales', 'IT':'IT', 'TAC':'TAC', \
               'arketing':'Marketing', 'SME':'SME', 'Product Mana':'Engineering',\
               'Ops':'Operations', 'ACE':'Pro Services', 'IA':\
               'Finance', 'essional Ser':'Pro Services','HR':'HR',\
               'Accounting':'Finance', 'FP&A':'Finance','Accounting':'Finance',\
               'Tax':'Finance','CEO':'CEO/ CTO/ Biz Ops','CTO':'CEO/ CTO/ Biz Ops',\
               'QA':'QA','acilit':'Facilities','Bus Dev':'Biz Dev','Training':\
               'Training','Allocation':'Facilities', 'Legal':'Legal','RMA':'Operations',\
               'Purchasing':'Finance','Public Re':'Marketing', 'CMO':'Marketing',\
               'PMO':'CEO/ CTO/ Biz Ops','EBC':'Marketing'}


t_data['Department'] = np.NaN
u_data['Department'] = np.NaN
#while i <= len(t_data['Group']):
def check_group(row):
    for key in group_to_OU:
        if re.search(str(key), str(row['Group'])):
            return group_to_OU[key]
         

'''
    if group_to_OU'ales' in str(row['Group']):
        return 'Sales'
    elif 'TAC' t_data['Group'].str.contains('TAC') is True:
        return 'TAC'
    else:
        return 'Not Found'
'''
# Check the listed group and place into a generic Department
t_data['Department'] = t_data.apply(check_group, axis=1)
u_data['Department'] = u_data.apply(check_group, axis=1)

# Create a new 'Department Totals' dataframe with columns for
# complete, incomplete, total users, and percentage complete
dep_tots = pd.DataFrame({'Completed': \
        t_data.groupby(t_data['Department']).count()['Email'],\
        'Incomplete': u_data.groupby(u_data['Department']).count()['Email']})

# A dirty way to calculate total number of users per department by
# summing the total training modules that have been distributed to
# users and then dividing by the number of unique modules.  Inaccurate
# if the org is experiencing rapid growth or decline
dep_tots['Total Users'] = (dep_tots['Completed'] + \
                        dep_tots['Incomplete']) / len(topics)

# Calculate the percentage complete per department
dep_tots['Percentage'] = dep_tots['Completed'] / (dep_tots['Completed'] + \
                        dep_tots['Incomplete']) *100

# Sort the DataFrame by total users in 
dep_tots = dep_tots.sort('Total Users')

# A quick plot, replaced by the more advanced one below
'''
plot_tots = dep_tots['Percentage'].plot(kind='bar', \
    title="Awareness Training by Completion Percentage")
fig_tots = plot_tots.get_figure()
fig_tots.savefig("/tmp/dept-totals" + str(today) + ".png")
'''

# Create a custom figure representing mutli-dimensional data
# idea and code from: 
# https://datasciencelab.wordpress.com/2013/12/21/beautiful-plots-with-pandas-and-matplotlib/
fig = plt.figure(figsize=(14,10))
# Add a subplot
ax = fig.add_subplot(111)
# Title
ttl = "Departmental Awareness Training Metrics"

a = 0.7 # transparency
customcmap = [(x/24.0, x/48.0, 0.05) for x in range(len(dep_tots))]
# Create a horizontal bar plot
plot_tots = dep_tots['Percentage'].plot(kind='barh', ax=ax, alpha=a, legend=False, color=customcmap,\
                        edgecolor='w', xlim=(0,max(dep_tots['Percentage'])), title=ttl)
ax.grid(axis='y')  # remove X gridline
ax.set_frame_on(False)  # no plot frame
# Customize title, set position, allow space on top of plot for title
ax.set_title(ax.get_title(), fontsize=26, alpha=a, ha='left')
plt.subplots_adjust(top=0.9)
ax.title.set_position((0,1.08))
# Set x axis label on top of plot, set label text
ax.xaxis.set_label_position('top')
xlab = 'Percent of Employees Completing Awareness Training'
ax.set_xlabel(xlab, fontsize=20, alpha=a, ha='left')
ax.xaxis.set_label_coords(0, 1.04)

# Position x tick labels on top
ax.xaxis.tick_top()
# Remove tick lines in x and y axes
ax.yaxis.set_ticks_position('none')
ax.xaxis.set_ticks_position('bottom')

# Customize x tick lables
xticks = [10,20,30,40,50,60]
ax.xaxis.set_ticks(xticks)
ax.set_xticklabels(xticks, fontsize=16, alpha=a)

# Customize y tick labels
yticks = [item.get_text() for item in ax.get_yticklabels()]
ax.set_yticklabels(yticks, fontsize=16, alpha=a)
ax.yaxis.set_tick_params(pad=12)

# Create a fake colorbar to express department population
ctb = LinearSegmentedColormap.from_list('custombar', customcmap, N=2048)
# Trick from http://stackoverflow.com/questions/8342549/
# matplotlib-add-colorbar-to-a-sequence-of-line-plots
sm = plt.cm.ScalarMappable(cmap=ctb, norm=plt.normalize(vmin=20, vmax=800))
# Fake up the array of the scalar mappable
sm._A = []
 
# Set colorbar, aspect ratio
cbar = plt.colorbar(sm, alpha=0.05, aspect=16, shrink=0.4)
cbar.solids.set_edgecolor("face")
# Remove colorbar container frame
cbar.outline.set_visible(False)
# Fontsize for colorbar ticklabels
cbar.ax.tick_params(labelsize=16)
# Customize colorbar tick labels
mytks = range(0,800,100)
cbar.set_ticks(mytks)
cbar.ax.set_yticklabels([str(a) for a in mytks], alpha=a)
 
# Colorbar label, customize fontsize and distance to colorbar
cbar.set_label('Department Population', alpha=a,
               rotation=270, fontsize=20, labelpad=20)
# Remove color bar tick lines, while keeping the tick labels
cbarytks = plt.getp(cbar.ax.axes, 'yticklines')
plt.setp(cbarytks, visible=False)
                        

fig_tots = plot_tots.get_figure()
fig_tots.savefig("/tmp/dept-totals" + str(today) + ".png")
