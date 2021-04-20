#!/usr/bin/python3

import os, sys
import tweepy
# import configparser  #todo
import requests
import datetime as dt

# How-to
usage = "./twitter-checkmydump.py retrieves recent posts by the CheckMyDump twitter account \
        and drops them into a directory, creating a directory based on the date the script \
        is executed. \n \n \
        ./twitter-checkmydump.py /path/to/destination"



# Twitter keys
consumer_key = "HXZSTg9yesNCmO5GdIUNLw"
consumer_secret = "jz2ElWSProgXIR7Rqot23UPKACbiLOQ26tMwMO8mP44"
access_token = "15318975-L84zQeUMsKITMPp6drn4fTh5ygFuopTwb8BTZQcU"
access_token_secret = "dHLQkpfOa2vaDW6SMkw1obr2oFMpVVelseLi9H4Ods"

# Check for required 

# Import the data directory from the command line
datadir = sys.argv[1]

# Get today's date for file naming reasons
def date():
        today = dt.datetime.today()
        return today.strftime("%Y%m%d")

def createdir(date):
        if not os.path.exists(date):
                os.makedirs(

# Function to extract tweets 
def get_tweets(username): 
          
        # Authorization to consumer key and consumer secret 
        auth = tweepy.OAuthHandler(consumer_key, consumer_secret) 
        # Access to user's access key and access secret 
        auth.set_access_token(access_token, access_token_secret) 
        # Calling api 
        api = tweepy.API(auth) 

        # How many tweets to extract
        number_of_tweets=20
        tweets = api.user_timeline(screen_name=username) 
  
        # Create a list to store the tweets
        tmp=[]  
  
        # create array of tweet information: username,  
        # tweet id, date/time, text 
        tweets_for_csv = [tweet.text for tweet in tweets] # CSV file created  
        for j in tweets_for_csv: 
            tmp.append(j)  # append tweets to the list
        i = 1
        for t in tmp:
#            print(t)   # debug
            x,y = t.split(':', 1)
            r = requests.get(y)
            filename = str(i) + '.txt'
            dump_file = open(filename, 'w')
            dump_file.write(r.text)
            i += 1
            

  
  
# Driver code 
if __name__ == '__main__': 
  
    # Here goes the twitter handle for the user 
    # whose tweets are to be extracted. 
    get_tweets("checkmydump")
