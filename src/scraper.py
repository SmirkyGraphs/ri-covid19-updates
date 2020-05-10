import time
import pandas as pd
from pathlib import Path

keep_rows = [
    'Total number of positive labs received by RIDOH',
    'Total number of negative labs received by RIDOH',
    'currently hospitalized in Rhode Island',
    'currently in an intensive care unit',
    'COVID-19 associated fatalities \(cumulative\)',
    'discharged from a hospital in Rhode Island',
    'were admitted to a hospital',
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

def scrape_sheet(sheet_id, raw_general, raw_geo, raw_dem):
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

        ## transform general sheet
        df['date'] = date
        df.columns = ['metric', 'count', 'date']
        df = df[df['metric'].str.contains(keep_list)]
        save_file(df, raw_general, date)

        ## scrape geographic sheet
        geo_url = f'https://docs.google.com/spreadsheets/d/{sheet_id}1759341227'
        geo_df = pd.read_csv(geo_url)

        # get grographic date & fix cols
        geo_date = list(geo_df)[-1].split(':')[-1].strip()
        geo_df['date'] = geo_date
        geo_df = geo_df.dropna(axis=1)
        geo_df.columns = ['city_town', 'count', 'date']
        save_file(geo_df, raw_geo, date)

        ## scrape demographics sheet
        dem_url = f'https://docs.google.com/spreadsheets/d/{sheet_id}771623753'
        dem_df = pd.read_csv(dem_url)

        # make sure no columns were added/removed
        if not dem_df.shape == (27, 7):
            print('[error] demographics format changed')
            return
        else:
            # get demographics updated date
            dem_date = list(dem_df)[0].split(':')[-1].strip()

            # drop percentage columns & rename
            dem_df = dem_df.drop(dem_df.columns[[2, 4, 6]], axis=1)
            dem_df.columns = ['metric', 'case_count', 'hosptialized', 'deaths']
            
            # get data
            sex = dem_df[1:3]
            age = dem_df[5:16]
            race = dem_df[18:23]

            # combine & save
            dem_df = pd.concat([sex, age, race])
            dem_df['date'] = dem_date
            save_file(dem_df, raw_dem, date)

def scrape_revised_data(sheet_id):
    """
    The revised data is updated daily and contains all prior dates.
    This will download & overwrite prior revised data file.
    """
    url = f'https://docs.google.com/spreadsheets/d/{sheet_id}1998687529'
    df = pd.read_csv(gen_url)
    df.to_csv('./data/raw/revised_data.csv', index=False)


def scrape_nursing_homes(sheet_id, raw_facility):
    # load prior date
    df = pd.read_csv(raw_facility, parse_dates=['date'])
    prior_date = df['date'].max().tz_localize('EST').date()

    url = f'https://docs.google.com/spreadsheets/d/e/{sheet_id}/pubhtml?gid=0&single=true'
    df = pd.read_html(url)[0]

    # get date of last update 
    date = df.iloc[0,1].split(' ')[-1]
    date = pd.to_datetime(date).tz_localize('EST').date()
    if not date > prior_date:
        print('\n[status] nursing homes:\tno update')
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
        print('[status] nursing homes:\tupdated')

def scrape_zip_codes(sheet_id, raw_zip):
    # load prior date
    df = pd.read_csv(raw_zip, parse_dates=['date'])
    prior_date = df['date'].max().tz_localize('EST').date()

    url = f'https://docs.google.com/spreadsheets/d/{sheet_id}932150337'
    df = pd.read_csv(url)

    # check if updated
    date = df.iloc[0][1].strip()
    date = pd.to_datetime(date).tz_localize('EST').date()
    if not date > prior_date:
        print('[status] zip codes:\tno update')
        return
    else:
        # skip first 3 rows and stop # pending more info
        df.columns = ['zip_code', 'count', 'rate']
        df = df[3:df[df.zip_code == 'Pending further info'].index[0]]
        df = df[['zip_code', 'count']]

        # add date & save
        df['date'] = date
        save_file(df, raw_zip, date)
        print('[status] zip codes:\tupdated')