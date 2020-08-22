from datetime import datetime
import numpy as np
import pandas as pd
import pygsheets
import json

with open('./config.json') as config:
    creds = json.load(config)['google']

def convert_int(value):
    value = str(value).lower()
    value = value.replace('fewer than five', '0')
    value = value.replace('fewer than 5', '0')
    value = value.replace('<5', '0')
    value = value.replace('approximately', '')
    value = value.replace('approx.', '').strip()
    value = value.replace(',', '').replace('.0', '').replace('.', '')
    
    return int(value)

def clean_facility_city(string):
    if string == None:
        return
    string = string.replace(')','')
    string = string.split('-')[0]
    
    return string.strip()

def sync_sheets(df, sheet_name):
    print(f'[status] syncing google sheet {sheet_name}')
    # google sheets authentication
    api = pygsheets.authorize(service_file=creds, retries=5)
    wb = api.open('ri-covid-19')

    # open the google spreadsheet
    sheet = wb.worksheet_by_title(f'{sheet_name}')
    sheet.set_dataframe(df, (1,1))

def clean_general(fname):
    print('[status] cleaning statwide general info')
    df = pd.read_csv(f'./data/raw/{fname}.csv', parse_dates=['date'])

    # remove total causing errors
    df = df[df['metric'] != 'Cumulative people who tested positive (counts first positive lab per person) plus cumulative negative tests (may count people more than once)']

    # re name metrics to shorten them
    df.loc[(df['metric'].str.contains('positive')) & (df['date'] < '2020-07-13'), 'metric'] = 'RI positive cases'
    df.loc[(df['metric'].str.contains('negative')) & (df['date'] < '2020-07-13'), 'metric'] = 'RI negative results'
    df.loc[(df['metric'].str.contains('self-quarantine')) & (df['date'] < '2020-07-13'), 'metric'] = 'instructed to self-quarantine'
    df.loc[(df['metric'].str.contains('hospitalized')) & (df['date'] < '2020-07-13'), 'metric'] = 'currently hospitalized'
    df.loc[(df['metric'].str.contains('die')) & (df['date'] < '2020-07-13'), 'metric'] = 'total deaths'
    df.loc[(df['metric'].str.contains('fatalities')) & (df['date'] < '2020-07-13'), 'metric'] = 'total deaths'
    df.loc[(df['metric'].str.contains('ventilators')) & (df['date'] < '2020-07-13'), 'metric'] = 'currently on ventilator'
    df.loc[(df['metric'].str.contains('on a vent')) & (df['date'] < '2020-07-13'), 'metric'] = 'currently on ventilator'
    df.loc[(df['metric'].str.contains('intensive care')) & (df['date'] < '2020-07-13'), 'metric'] = 'currently in icu'
    df.loc[(df['metric'].str.contains('discharged')) & (df['date'] < '2020-07-13'), 'metric'] = 'total discharged'

    df.loc[df['metric'].str.contains('Cumulative people who tested positive '), 'metric'] = 'people positive'
    df.loc[df['metric'].str.contains('Cumulative people tested '), 'metric'] = 'people tested'
    df.loc[df['metric'].str.contains('New people who tested positive'), 'metric'] = 'new positive'
    df.loc[df['metric'].str.contains('Cumlative people who tested positive'), 'metric'] = 'RI positive cases'
    df.loc[df['metric'].str.contains('Cumlative people who have only tested negative'), 'metric'] = 'RI negative results'
    df.loc[df['metric'].str.contains('Currently hospitalized'), 'metric'] = 'currently hospitalized'
    df.loc[df['metric'].str.contains('Currently in ICU'), 'metric'] = 'currently in icu'
    df.loc[df['metric'].str.contains('Currently vented'), 'metric'] = 'currently on ventilator'
    df.loc[df['metric'].str.contains('Total deaths'), 'metric'] = 'total deaths'


    # convert types count -> int, date -> datetime str
    df['count'] = df['count'].apply(convert_int)
    df['date'] = pd.to_datetime(df['date']).dt.strftime('%m/%d/%Y')

    # pivot to get total tests given out then un-pivot 
    df = df.pivot_table(index='date', columns='metric', values='count').reset_index()
    df['RI total tests'] = df['RI positive cases'] + df['RI negative results']
    df = df.melt(col_level=0, id_vars=['date'], value_name='count').sort_values(by=['date', 'metric'])

    # get daily changes
    df['count'] = df['count'].fillna(0)
    df['new_cases'] = df.groupby('metric')['count'].diff().fillna(0).astype(int)
    df['change_%'] = df.groupby('metric')['count'].pct_change().replace(np.inf, 0).fillna(0)

    # save & sync to google sheets
    df.to_csv('./data/clean/ri-covid-19-clean.csv', index=False)
    sync_sheets(df, 'statewide')

def clean_geographic(fname):
    print('[status] cleaning city/town info')
    df = pd.read_csv(f'./data/raw/{fname}.csv')
    pop = pd.read_csv('./data/external/population_est_2017.csv')

    # remove under 5 surpressed values
    df['count'] = df['count'].apply(convert_int)
    df['count'] = df['count'].fillna(0)

    # sort by date
    df['date'] = pd.to_datetime(df['date']).dt.strftime('%m/%d/%Y')
    df = df.sort_values(by=['date'])

    # get daily changes
    df['change'] = df.groupby('city_town')['count'].diff().fillna(0).astype(int)
    df['change_%'] = df.groupby('city_town')['count'].pct_change().replace(np.inf, 0).fillna(0)

    # merge population & calculate rate per 10,000 people
    df = df.merge(pop, on='city_town').sort_values(by='date')
    df['rate_per_10k'] = (df['count']/df['2017_population']) * 10000

    # filter for wanted columns
    df = df[['city_town', 'county', 'count', 'change', 'change_%', 'rate_per_10k', 'date']]

    # save & sync to google sheets
    df.to_csv('./data/clean/geo-ri-covid-19-clean.csv', index=False)
    sync_sheets(df, 'city_town')

def clean_zip_codes(fname):
    print('[status] cleaning zip codes data')
    df = pd.read_csv(f'./data/raw/{fname}.csv')
    pop = pd.read_csv('./data/external/zip_code_pop_2010.csv')

    # remove under 5 surpressed values
    df['count'] = df['count'].apply(convert_int)
    df['count'] = df['count'].fillna(0)

    # sort by date
    df['date'] = pd.to_datetime(df['date']).dt.strftime('%m/%d/%Y')
    df = df.sort_values(by=['date'])

    # get daily changes
    df['change'] = df.groupby('zip_code')['count'].diff().fillna(0).astype(int)
    df['change_%'] = df.groupby('zip_code')['count'].pct_change().replace(np.inf, 0).fillna(0)

    # add rank & change in rank

    # merge population & calculate rate per 10,000 people
    df = df.merge(pop, on='zip_code').sort_values(by='date')
    df['rate_per_10k'] = (df['count']/df['population']) * 10000
    
    # save file
    df.to_csv('./data/clean/zip-codes-covid-19-clean.csv', index=False)

def clean_nursing_homes(fname):
    print('\n[status] cleaning nursing homes')
    df = pd.read_csv(f'./data/raw/{fname}.csv')

    # remove total cases & fatalities rows
    df = df[~df['Facility Name'].str.contains("Total Cases")]

    # normalize delimiter
    df['Cases'] = df['Cases'].str.replace('-', ' to ')
    df["Fatalities"] = df["Fatalities"].str.replace('-', ' to ')

    # split low/high cases & fatalities
    cases = df["Cases"].str.split(" to ", n=1, expand=True).fillna(0)
    fatalities = df["Fatalities"].str.split(" to ", n=1, expand=True).fillna(0)
    df['cases_low'] = cases[0].apply(convert_int)
    df['cases_high'] = cases[1].apply(convert_int)
    df['fatalities_low'] = fatalities[0].apply(convert_int)
    df['fatalities_high'] = fatalities[1].apply(convert_int)

    # add average value 
    df['cases_avg'] = (df['cases_low'] + df['cases_high'])/2
    df['fatalities_avg'] = (df['fatalities_low'] + df['fatalities_high'])/2

    # split facility name & city/town
    facility = df["Facility Name"].str.split("(", n=1, expand=True)
    df['facility_name'] = facility[0]
    df['city_town'] = facility[1].apply(clean_facility_city)
    df = df.drop(columns=['Cases', 'Fatalities', 'Facility Name'])

    # load & merge county
    county = pd.read_csv('./data/external/population_est_2017.csv')
    df = df.merge(county[['city_town', 'county']], on='city_town', how='left')

    # create date col and sort by date
    df['date'] = pd.to_datetime(df['date']).dt.strftime('%m/%d/%Y')
    df = df.sort_values(by=['type', 'facility_name', 'date'])

    recent_dates = np.sort(df['date'].unique())[-2:]
    df.loc[df['date'] == recent_dates[1], 'date_bin'] = 'Most Recent'
    df.loc[df['date'] == recent_dates[0], 'date_bin'] = 'Prior Week'

    # save file
    df.to_csv('./data/clean/nurse-homes-covid-19-clean.csv', index=False)

def clean_revised(fname):
    print('[status] cleaning revised data')
    df = pd.read_csv(f'./data/raw/{fname}.csv', parse_dates=['date', 'date_scraped'])

    # replace null label -- with 0
    df = df.replace('--', 0)

    df['new total labs'] = (df['new positive labs'] + df['new negative labs'])
    df['%_positive_labs'] = (df['new positive labs']/df['new total labs'])
    df['new people tested'] = (df['new people positive'] + df['new people negative'])
    df['%_new_people_positive'] = (df['new people positive']/df['new people tested'])
    df['date_ts'] = df['date'].apply(lambda x: datetime.toordinal(x))

    # sort by date & save
    df['date'] = pd.to_datetime(df['date']).dt.strftime('%m/%d/%Y')
    df = df.sort_values(by=['date_scraped', 'date'])
    df.to_csv('./data/clean/revised-data-clean.csv', index=False)

    # export to google sheets most recent date
    df = df[df['date_scraped'] == df['date_scraped'].max()]
    df['date_scraped'] = df['date_scraped'].dt.strftime('%m/%d/%Y')
    sync_sheets(df, 'trend_data')