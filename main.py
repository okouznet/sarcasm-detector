import requests
import json
import sys
import urllib2
import time
import numpy as np
from pandas import Series, DataFrame
import pandas as pd
import praw
"""
urls:
r/sarcasm
r/sarcasticcrazyideas
r/sarcasticdiscussion

"""

client_id = "dj8omXNrlb5wbw"
client_secret = "48OiWsAhbWlwA7gQgRthUJzwHuY"

def is_ascii(s):
    return all(ord(c) < 128 for c in s)

def get_raw_data(subreddit_title, file="data.csv"):
    """
    extracts all data from a specific subreddit channel and saves to csv
    :param subreddit_title: title of subreddit channel to extract data from
    :param file: name of file to be written to
    :return:
    """
    hdr = {'User-Agent': 'osx:r/sarcasm.multiple.results:v1.0 (by /u/skouznet)'}
    url = 'https://www.reddit.com/r/'+subreddit_title+'/top/.json?sort=top&t=all&limit=1'
    req = urllib2.Request(url, headers=hdr)
    text_data = urllib2.urlopen(req).read()
    data = json.loads(text_data)
    data_all = data.values()[1]['children']

    while (len(data_all) <= 20): #BUG: data length
        time.sleep(2)  # Required by API
        last = data_all[-1]['data']['name']
        url = 'https://www.reddit.com/r/'+subreddit_title+'/top/.json?sort=top&t=all&limit=100&after=%s' % last
        req = urllib2.Request(url, headers=hdr)
        text_data = urllib2.urlopen(req).read()
        data = json.loads(text_data)
        data_all += data.values()[1]['children']


    article_title = []
    article_id = []
    article_date = []

    for i in range(0, len(data_all)):
        article_title.append(data_all[i]['data']['title'])
        article_id.append(data_all[i]['data']['id'])
        article_date.append(data_all[i]['data']['created_utc'])

    rel_df = DataFrame({'Date': article_date,
                        'Title': article_title,
                        'ID': article_id})
    rel_df = rel_df[['Date', 'Title', 'ID']]
    rel_df.to_csv(path_or_buf=file, sep=",")
    return

def get_comment_data(file_in, file_out, username, password):
    """
    extracts comments from all subreddit channels in the file
    :param file: name of file to be read
    :param username: username for reddit account
    :param password: password for reddit account
    :return: comments: all comments for each title in subreddit channel
    """
    data = DataFrame.from_csv(file_in)
    reddit = praw.Reddit(client_id=client_id,
                         client_secret=client_secret,
                         password=password,
                         user_agent='sarcasm.multiple.results:v1.0 by /u/' + username,
                         username=username)

    id = data['ID']
    title = data['Title']
    comment_body = []
    comment_title = []
    for i in range(0, len(data)):
        submission = reddit.get_submission(submission_id=id[i])
        # submission.comments.replace_more(limit=None)
        for top_level_comment in submission.comments:
            if is_ascii(s=top_level_comment.body):
                print(top_level_comment.body)
                comment_body.append(top_level_comment.body)
                comment_title.append(title[i])

    x = [('title', comment_title),
         ('comment', comment_body)]
    comments = pd.DataFrame.from_items(x)
    comments.to_csv(path_or_buf=file_out, sep=",")
    return comments

if __name__ == "__main__":
    get_raw_data(subreddit_title='sarcasm', file='reddit-data-sarcasm.csv')
    #get_raw_data(subreddit_title='sarcasticcrazyideas', file='reddit-data-sarcasticcrazyideas.csv')
    #get_raw_data(subreddit_title='sarcasticdiscussion', file='reddit-data-sarcasticdiscussion.csv')

    #enter username and password
    username = ''
    password = ''
    get_comment_data(file_in='reddit-data-sarcasm.csv',
                     file_out='reddit-data-sarcasm-comments.csv',
                     username=username, password=password)
    get_comment_data(file_in='reddit-data-sarcasticcrazyideas.csv',
                     file_out='reddit-data-sarcasticcrazyideas-comments.csv',
                     username=username, password=password)
