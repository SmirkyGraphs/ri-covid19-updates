import time
import pandas as pd
from pathlib import Path

drop_cols = [
    '3-day average of daily number of positive tests (may count people more than once)',
    'daily total tests completed (may count people more than once)',
    '3-day average of new people who tested positive (counts first positive lab per person)',
    '3-day average of currently hospitalized'
]

def save_file(df, file_path, current_date):
    # save/update file
    if not Path(file_path).exists():
        df.to_csv(file_path, index=False)
    else:
        # get prior file date
        prior = pd.read_csv(file_path, parse_dates=['date'])
        prior_date = pd.to_datetime(prior['date'].max()).date()  
        if current_date > prior_date:
            df.to_csv(file_path, mode='a', header=False, index=False)
        return

def scrape_sheet(sheet_id):
    # load previous raw_data and get prior date
    raw_general = './data/raw/ri-covid-19.csv'
    df = pd.read_csv(raw_general, parse_dates=['date'])
    prior_date = df['date'].max().tz_localize('EST').date()

    # wait till 12:05 then check every 15 mins for update
    target = pd.datetime.now().replace(hour=12).replace(minute=5)
    while pd.datetime.now() < target:
        print(f"[status] waiting for 12pm", end='\r')
        time.sleep(60)

    # load data from RI - DOH spreadsheet
    gen_url = f'https://docs.google.com/spreadsheets/d/{sheet_id}264100583'
    df = pd.read_csv(gen_url).dropna(axis=1, how='all')
    date = list(df)[1].strip()
    date = pd.to_datetime(date).tz_localize('EST').date()

    while not prior_date < date:
        print(f"[status] waiting for update...{time.strftime('%H:%M')}", end='\r')
        time.sleep(5 * 60)
        df = pd.read_csv(gen_url)
        date = list(df)[1].strip()
        date = pd.to_datetime(date).tz_localize('EST').date()
    else:
        print('[status] found new update pausing for 5 mins')
        time.sleep(5 * 60)

        ## transform general sheet
        df['date'] = date
        df.columns = ['metric', 'count', 'date']
        save_file(df, raw_general, date)

        ## scrape geographic sheet
        geo_url = f'https://docs.google.com/spreadsheets/d/{sheet_id}901548302'
        geo_df = pd.read_csv(geo_url)

        # get grographic date & fix cols
        geo_date = geo_df.iloc[-1][1]
        geo_date = pd.to_datetime(geo_date).tz_localize('EST').date()
        geo_df['date'] = geo_date

        cols = [x for x in list(geo_df) if 'Rate' not in x]
        geo_df = geo_df[cols]

        geo_df = geo_df.dropna(axis=0)
        geo_df.columns = ['city_town', 'count', 'hostpialized', 'deaths', 'date']

        # save file
        raw_geo = './data/raw/geo-ri-covid-19.csv'
        save_file(geo_df, raw_geo, geo_date)

        ## scrape demographics sheet
        dem_url = f'https://docs.google.com/spreadsheets/d/{sheet_id}31350783'
        dem_df = pd.read_csv(dem_url)

        # make sure no columns were added/removed
        if not dem_df.shape == (31, 9):
            print('[error] demographics format changed')
            return
        else:
            # get demographics updated date
            dem_date = dem_df.iloc[-1][1]
            dem_date = pd.to_datetime(dem_date).tz_localize('EST').date()

            # drop percentage columns & rename
            dem_df = dem_df.drop(dem_df.columns[[1, 2, 4, 6, 8]], axis=1)
            dem_df.columns = ['metric', 'case_count', 'hosptialized', 'deaths']
            
            # get data
            sex = dem_df[1:4]
            age = dem_df[5:17]
            race = dem_df[18:24]

            dem_df = pd.concat([sex, age, race])
            dem_df['date'] = dem_date

            raw_dem = './data/raw/demographics-covid-19.csv'
            save_file(dem_df, raw_dem, dem_date)

def scrape_revised(sheet_id):
    # load previous revised_data and get prior date
    raw_revised = './data/raw/revised-data.csv'
    df = pd.read_csv(raw_revised, parse_dates=['date'])
    prior_date = df['date'].max().tz_localize('EST').date()

    # load revised sheet & fix column names
    url = f'https://docs.google.com/spreadsheets/d/{sheet_id}1592746937'
    df = pd.read_csv(url, parse_dates=['Date'])
    df.columns = [x.lower() for x in list(df)]

    # test to try and make sure columns dont change
    if df.shape[1] != 26 or list(df)[6] != 'daily total tests completed (may count people more than once)':
        print('[error] revised sheet columns changed')
        return

    # check if updated
    if df['date'].max() > prior_date:
        df = df.drop(columns=drop_cols)

        # re order columns
        move_cols = list(df)[6:11]
        cols = [x for x in list(df) if x not in move_cols]
        cols.extend(move_cols)
        df = df[cols]

        df['date_scraped'] = pd.datetime.strftime(pd.datetime.now(), '%m/%d/%Y')
        save_file(df, raw_revised, df['date'].max())

def scrape_nursing_homes(sheet_id):
    # load prior date
    raw_facility = './data/raw/nurse-homes-covid-19.csv'
    df = pd.read_csv(raw_facility, parse_dates=['date'])
    prior_date = df['date'].max().tz_localize('EST').date()

    url = f'https://docs.google.com/spreadsheets/d/{sheet_id}500394186'
    df = pd.read_csv(url)

    # get date of last update 
    date = df.iloc[0,0].split(' ')[-1]
    date = pd.to_datetime(date).tz_localize('EST').date()
    if not date > prior_date:
        print('\n[status] nursing homes:\tno update')
        return
    else:
        # fix headers
        df.columns = df.iloc[1]

        # drop past 14 days column
        df = df.drop(columns='New Resident Cases (in past 14 days)')
        df['Facility Name'] = df['Facility Name'].str.replace(u'\xa0', ' ') # random unicode appeared

        # fix dataframe shape
        assisted = df[df['Facility Name'] == 'Assisted Living Facilities'].index[0]
        nursing_homes = df[3:assisted].copy()
        assisted_living = df[assisted+1:-1].copy()

        # add facility type & recombine
        nursing_homes['type'] = 'nursing home'
        assisted_living['type'] = 'assisted living'
        df = pd.concat([nursing_homes, assisted_living]).reset_index(drop=True)

        # add date
        df['date'] = date
        save_file(df, raw_facility, date)
        print('[status] nursing homes:\tupdated')

def scrape_zip_codes(sheet_id):
    # load prior date
    raw_zip = './data/raw/zip-codes-covid-19.csv'
    df = pd.read_csv(raw_zip, parse_dates=['date'])
    prior_date = df['date'].max().tz_localize('EST').date()

    url = f'https://docs.google.com/spreadsheets/d/{sheet_id}365656702'
    df = pd.read_csv(url)

    # check if updated
    date = df.iloc[-1][1].strip()
    date = pd.to_datetime(date).tz_localize('EST').date()
    if not date > prior_date:
        print('[status] zip codes:\tno update')
        return
    else:
        # stop # pending more info
        df.columns = ['zip_code', 'count', 'rate']
        df = df[:df[df.zip_code == 'Pending further info'].index[0]]
        df = df[['zip_code', 'count']]

        # add date & save
        df['date'] = date
        save_file(df, raw_zip, date)
        print('[status] zip codes:\tupdated')