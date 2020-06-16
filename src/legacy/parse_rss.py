# legacy code was used to parse press briefings from RSS feed
# prior to the google sheet being updated daily
# rss_feed = 'https://www.ri.gov/rss/8/pressrelease.rss'

import json
import requests
import feedparser
from bs4 import BeautifulSoup

data = {}
geo_data = {}
age_data = {}

with open('./data/files/lists.json') as f:
    lists = json.load(f)
    metric_list = lists['metric_list']
    geo_list = lists['geo_list']
    age_list = lists['age_list']

def get_press_brief(url):
    r = requests.get(url)
    soup = BeautifulSoup(r.text, 'lxml')

    entry = soup.find("div", {"class": "entry-content"})
    lines = entry.find_all('p')

    data = [line.text.strip() for line in lines if (len(line.text) <= 150)]
    data_end = data.index('Key messages for the public')
    data_lines = data[:data_end]
    
    return data_lines

def get_rss_date(press_brief):
    try:
        date = pd.to_datetime(press_brief[0]['published']).tz_convert('EST').date()    
    except:
        time.sleep(2 * 60)
        date = pd.to_datetime(press_brief[0]['published']).tz_convert('EST').date()  
    return date

def find_variable(dic, d, number, date, var, word_list):
    if any(word in d for word in word_list):
        dic.setdefault(f'{var}', []).append(d)
        dic.setdefault('count', []).append(number)
        dic.setdefault('date', []).append(date)
    return
        
def parse_data(data_lines, date):
    for d in data_lines:
        d = d.replace('\x96', ':').replace('- ', '')
        info = d.split(': ')[:1][0].strip()
        number = d.split(': ')[-1:][0].strip()
        find_variable(data, info, number, date, 'metric', metric_list)
        find_variable(geo_data, info, number, date, 'city_town', geo_list)
        find_variable(age_data, info, number, date, 'age_bin', age_list)
        
def scrape_briefing(url, prior_date):
    # get date of most recent feed entry
    feed = feedparser.parse(url)
    press_brief = feed['entries'][:1]
    current_date = get_rss_date(press_brief)
    while not prior_date < current_date:
        # get new press_brief and wait 15 mins
        print('[status] waiting for update...', end='\r')
        feed = feedparser.parse(url)
        press_brief = feed['entries'][:1]
        current_date = get_rss_date(press_brief)
        time.sleep(15 * 60)
    else:
        print('[status] found new update')
        date = current_date.strftime('%#m/%d/%Y')
        url = press_brief[0]['link']
        data_lines = get_press_brief(url)
        parse_data(data_lines, date)

        return {'state_data': data, 'geo_data': geo_data, 'age_data': age_data, 'date': current_date}

def update_briefing(url, prior_date, raw_state, raw_geo, raw_age):
    clean_data = {'approx. ': '', 'approximately ': '', ',': '', 'Fewer than 5': '0', '90 and older': '90+'}

    # scrape data & load data into dataframes
    data = scrape_briefing(url, prior_date)
    state_data = pd.DataFrame(data['state_data']).replace(clean_data, regex=True)
    geo_data = pd.DataFrame(data['geo_data']).replace(clean_data, regex=True)  
    age_data = pd.DataFrame(data['age_data']).replace(clean_data, regex=True)  
    date = data['date']

    # save files
    save_file(state_data, raw_state, date)
    save_file(geo_data, raw_geo, date)
    save_file(age_data, raw_age, date)