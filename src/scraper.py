import json
import time
import pandas as pd
from pathlib import Path
from selenium import webdriver

# setup chromedriver options
options = webdriver.ChromeOptions() 
options.add_argument('--headless')
options.add_argument('--disable-gpu')

# load css selectors
with open('./data/files/selectors.json') as f:
    sel = json.load(f)

# load chrome info
with open('./config.json') as config:
    chromedriver = json.load(config)['driver']

# load browser and request webpage
browser = webdriver.Chrome(chromedriver, options=options)
url = 'https://ri-department-of-health-covid-19-data-rihealth.hub.arcgis.com/'

def save_file(df, file_path, current_date):
    # save/update file
    if not Path(file_path).exists():
        df.to_csv(file_path, index=False)
    else:
        # get prior file date
        prior = pd.read_csv(file_path)
        prior_date = pd.to_datetime(prior['date'].max()).date()  
        if current_date > prior_date:
            df.to_csv(file_path, mode='a', header=False, index=False)
        return

def scrape_cities(date):
    cities_table_1 = browser.find_element_by_css_selector(sel['cities_css_1'])
    cities_1 = [x for x in cities_table_1.text.split('\n')]
    cities_table_2 = browser.find_element_by_css_selector(sel['cities_css_2'])
    cities_2 = [x for x in cities_table_2.text.split('\n')]

    values_table_1 = browser.find_element_by_css_selector(sel['values_css_1'])
    values_1 = [x for x in values_table_1.text.split('\n')]
    values_table_2 = browser.find_element_by_css_selector(sel['values_css_2'])
    values_2 = [x for x in values_table_2.text.split('\n')]

    cities = list(cities_1 + cities_2)
    values = list(values_1 + values_2)
    data = {"city_town": cities, "count": values, "date": date}

    return pd.DataFrame(data)

def scrape_general(date):
    negative = browser.find_element_by_css_selector(sel['negative_css']).text
    positive = browser.find_element_by_css_selector(sel['positive_css']).text
    deaths = browser.find_element_by_css_selector(sel['deaths_css']).text
    hospital = browser.find_element_by_css_selector(sel['hospitalized_css']).text
    icu = browser.find_element_by_css_selector(sel['icu_css']).text
    vent = browser.find_element_by_css_selector(sel['vent_css']).text
    discharge = browser.find_element_by_css_selector(sel['discharge_css']).text

    data = {
        'total positive cases': positive,
        'total negative cases': negative,
        'currently hospitalized': hospital,
        'currently in intensive care': icu,
        'total fatalities': deaths,
        'total on ventilators': vent,
        'total discharged': discharge
    }    
     
    df = pd.Series(data).reset_index()
    df.columns = ['metric', 'count']
    df['date'] = date

    return df

def scrape_powerbi(raw_geo, raw_general):
    df = pd.read_csv(raw_general, parse_dates=['date'])
    prior_date = df['date'].max().tz_localize('EST').date()

    # wait till 12:05 then check every 15 mins for update
    target = pd.datetime.now().replace(hour=12).replace(minute=5)
    while pd.datetime.now() < target:
        print(f"[status] waiting for 12pm", end='\r')
        time.sleep(60)

    browser.get(url)
    time.sleep(60)
    report_url = browser.find_element_by_css_selector('#ember46 > iframe').get_attribute("src")
    browser.get(report_url)
    time.sleep(60)

    date = browser.find_element_by_css_selector(sel['date_css']).text
    date = pd.to_datetime(date).tz_localize('EST').date()

    while not prior_date < date:
        print(f"[status] waiting for update...{time.strftime('%H:%M')}", end='\r')
        time.sleep(15 * 60)

        browser.get(url)
        time.sleep(60)
        report_url = browser.find_element_by_css_selector('#ember46 > iframe').get_attribute("src")
        browser.get(report_url)
        time.sleep(60)

        date = browser.find_element_by_css_selector(sel['date_css']).text
        date = pd.to_datetime(date).tz_localize('EST').date()
    else:
        print('[status] found new update scraping geographic')
        cities = scrape_cities(date)
        save_file(cities, raw_geo, date)

        print('[status] scraping general info')
        general = scrape_general(date)
        save_file(general, raw_general, date)