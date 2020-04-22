# legacy code
# scraper for google sheets

import time
import pandas as pd
from pathlib import Path

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

def scrape_sheet(google_sheet, sheet_id, raw_data):
    # load previous raw_data and get prior date
    df = pd.read_csv(raw_data, parse_dates=['date'])
    prior_date = df['date'].max().tz_localize('EST').date()

    # load data from RI - DOH spreadsheet
    url = f'https://docs.google.com/spreadsheets/d/{google_sheet}{sheet_id}'
    df = pd.read_csv(url)
    if sheet_id == '0':
        date = list(df)[0].split(': ')[-1:][0].strip()
    else:
        date = list(df)[2].split(' ')[-1:][0]
    date = pd.to_datetime(date).tz_localize('EST').date()

    while not prior_date < date:
        print(f'[status] waiting for update...{time.time()}', end='\r')
        df = pd.read_csv(url)
        if sheet_id == '0':
            date = list(df)[0].split(': ')[-1:][0].strip()
        else:
            date = list(df)[2].split(' ')[-1:][0]
        date = pd.to_datetime(date).tz_localize('EST').date()
        time.sleep(15 * 60)
    else:
        print('[status] found new update pausing for 5 mins')
        time.sleep(5 * 60)
        # transform data into table & save
        if sheet_id == '0':
            df['date'] = list(df)[0].split(': ')[-1:][0].strip()
            df.columns = ['metric', 'count', 'date']
        else:
            df['date'] = list(df)[2].split(' ')[-1:][0]
            df = df.dropna(axis=1)
            df.columns = ['city_town', 'count', 'date']
        save_file(df, raw_data, date)
