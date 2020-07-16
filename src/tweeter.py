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
    total = int(count['people tested'])
    positive = int(count['people positive'])
    icu = int(count['currently in icu'])
    vent = int(count['currently on ventilator'])
    hospital = int(count['currently hospitalized'])
    deaths = int(count['total deaths'])

    # load data changes
    total_diff = add_plus(change['people tested'])
    pos_diff = add_plus(change['people positive'])
    icu_diff = add_plus(change['currently in icu'])
    vent_diff = add_plus(change['currently on ventilator'])
    hosp_diff = add_plus(change['currently hospitalized'])
    death_diff = add_plus(change['total deaths'])

    tweet = [
        f'{current_date} update:',
        f'people tested: {total} ({total_diff})',
        f'people positive: {positive} ({pos_diff})',
        f'hospitalized: {hospital} ({hosp_diff})',
        f'intensive care: {icu} ({icu_diff})',
        f'on ventilator: {vent} ({vent_diff})',
        f'total deaths {deaths} ({death_diff})',
         'data from @RIHEALTH'
    ]

    tweet = '\n'.join(tweet)
   
    # send tweet
    api.update_status(status=tweet)
    print('[status] tweet sent')