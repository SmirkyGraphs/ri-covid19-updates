import pandas as pd
import requests
import tweepy
import json

with open('./config.json') as config:
    config = json.load(config)['twitter']
    consumer_key = config['consumer_key']
    consumer_secret = config['consumer_secret']
    access_token = config['access_token']
    access_secret = config['access_secret']

def add_plus(value):
    if value >= 0:
       return f"+{value}"
    else:
        return value

def send_tweet():
    # auth with twitter
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_secret)
    api = tweepy.API(auth)

    # load the clean data and variables
    df = pd.read_csv('./data/clean/ri-covid-19-clean.csv')
    current_date = df['date'].max()

    # filter on current_date
    df = df[df['date'] == current_date]
    count = df.set_index('metric')['count']
    change = df.set_index('metric')['new_cases']

    # load data totals
    total = int(count['RI total tests'])
    positive = int(count['RI positive cases'])
    quarantine = int(count['instructed to self-quarantine'])
    hospital = int(count['currently hospitalized'])
    deaths = int(count['total deaths'])

    # load data changes
    total_diff = add_plus(change['RI total tests'])
    pos_diff = add_plus(change['RI positive cases'])
    quar_diff = add_plus(change['instructed to self-quarantine'])
    hosp_diff = add_plus(change['currently hospitalized'])
    death_diff = add_plus(change['total deaths'])

    tweet = [
        f'{current_date} update:',
        f'positive results: {positive} ({pos_diff})',
        f'total tests: {total} ({total_diff})',
        f'self-quarantine: {quarantine} ({quar_diff})',
        f'hospitalized: {hospital} ({hosp_diff})',
        f'total deaths {deaths} ({death_diff})',
         '#COVID19 #RI #coronavirus'
    ]

    tweet = '\n'.join(tweet)
   
    # send tweet
    api.update_status(status=tweet)
    print('[status] tweet sent')