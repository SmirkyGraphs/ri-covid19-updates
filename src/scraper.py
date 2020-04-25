import time
import pandas as pd
from pathlib import Path

keep_rows = [
    'Total number of positive labs received by RIDOH',
    'Total number of negative labs received by RIDOH',
    'currently hospitalized in Rhode Island',
    'currently in an intensive care unit',
    'COVID-19 associated fatalities \(cumulative\)',
    'discharged from a hospital in Rhode Island'
]

keep_list = '|'.join(keep_rows)

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

def scrape_sheet(sheet_id, raw_general, raw_geo):
    # load previous raw_data and get prior date
    df = pd.read_csv(raw_general, parse_dates=['date'])
    prior_date = df['date'].max().tz_localize('EST').date()

    # wait till 12:05 then check every 15 mins for update
    target = pd.datetime.now().replace(hour=12).replace(minute=5)
    while pd.datetime.now() < target:
        print(f"[status] waiting for 12pm", end='\r')
        time.sleep(60)

    # load data from RI - DOH spreadsheet
    gen_url = f'https://docs.google.com/spreadsheets/d/{sheet_id}0'
    df = pd.read_csv(gen_url)
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

        # transform general sheet
        df['date'] = date
        df.columns = ['metric', 'count', 'date']
        df = df[df['metric'].str.contains(keep_list)]
        save_file(df, raw_general, date)

        # scrape geographic sheet
        geo_url = f'https://docs.google.com/spreadsheets/d/{sheet_id}1759341227'
        geo_df = pd.read_csv(geo_url)
        geo_df['date'] = date
        geo_df = geo_df.dropna(axis=1)
        geo_df.columns = ['city_town', 'count', 'date']
        save_file(geo_df, raw_geo, date)

def scrape_nursing_homes(sheet_id, raw_facility):
    url = f'https://docs.google.com/spreadsheets/d/e/{sheet_id}/pubhtml?gid=0&single=true'
    df = pd.read_html(url)[0]

    # load prior date
    df = pd.read_csv(raw_facility, parse_dates=['date'])
    prior_date = df['date'].max().tz_localize('EST').date()

    # get date of last update 
    date = df.iloc[0,1][-10:].strip()
    date = pd.to_datetime(date).tz_localize('EST').date()
    if not date > prior_date:
        print('\n[status] nursing homes: no update')
        return
    else:
        # fix headers
        df.columns = df.iloc[1]

        # fix dataframe shape
        assisted = df[df['Facility Name'] == 'Assisted Living Facilities'].index[0]
        nursing_homes = df.drop(columns=[2])[3:assisted]
        assisted_living = df.drop(columns=[2])[assisted+1:-1]

        # add facility type & recombine
        nursing_homes['type'] = 'nursing home'
        assisted_living['type'] = 'assisted living'
        df = pd.concat([nursing_homes, assisted_living]).reset_index(drop=True)

        # add date
        df['date'] = date
        save_file(df, raw_facility, date)
        print('[status] nursing homes: updated')