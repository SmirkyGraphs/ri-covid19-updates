import pandas as pd
import pygsheets
import json

with open('./config.json') as config:
    creds = json.load(config)['google']

# google sheets authentication
api = pygsheets.authorize(service_file=creds)
wb = api.open('ri-covid-19')

def convert_int(value):
    value = str(value).replace('approximately', '')
    value = value.replace('approx.', '').strip()
    value = value.replace(',', '').replace('.0', '').replace('.', '')
    
    return int(value)

def clean_facility_city(string):
    string = string.replace(')','')
    string = string.split('-')[0]
    
    return string

def sync_sheets(wb, df, sheet_name):
    print(f'[status] syncing google sheet {sheet_name}')
    # open the google spreadsheet
    sheet = wb.worksheet_by_title(f'{sheet_name}')
    sheet.set_dataframe(df, (1,1))

def clean_general(raw_general):
    print('[status] cleaning statwide general info')
    df = pd.read_csv(raw_general)
    # re name metrics to shorten them
    df.loc[df['metric'].str.contains('positive'), 'metric'] = 'RI positive cases'
    df.loc[df['metric'].str.contains('negative'), 'metric'] = 'RI negative results'
    df.loc[df['metric'].str.contains('self-quarantine'), 'metric'] = 'instructed to self-quarantine'
    df.loc[df['metric'].str.contains('hospitalized'), 'metric'] = 'currently hospitalized'
    df.loc[df['metric'].str.contains('die'), 'metric'] = 'total deaths'
    df.loc[df['metric'].str.contains('fatalities'), 'metric'] = 'total deaths'
    df.loc[df['metric'].str.contains('ventilators'), 'metric'] = 'currently on ventilator'
    df.loc[df['metric'].str.contains('on a vent'), 'metric'] = 'currently on ventilator'
    df.loc[df['metric'].str.contains('intensive care'), 'metric'] = 'currently in icu'
    df.loc[df['metric'].str.contains('discharged'), 'metric'] = 'total discharged'

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
    df['change_%'] = df.groupby('metric')['count'].pct_change().replace(pd.np.inf, 0).fillna(0)

    # save & sync to google sheets
    df.to_csv('./data/clean/ri-covid-19-clean.csv', index=False)
    sync_sheets(wb, df, 'statewide')

def clean_geographic(raw_geo):
    print('[status] cleaning city/town info')
    df = pd.read_csv(raw_geo)
    pop = pd.read_csv('./data/files/population_est_2017.csv')

    # remove under 5 surpressed values
    df['count'] = df['count'].replace('fewer than 5', 0)
    df['count'] = df['count'].replace('<5', 0).astype(int)

    # sort by date
    df['date'] = pd.to_datetime(df['date']).dt.strftime('%m/%d/%Y')
    df = df.sort_values(by=['date'])

    # get daily changes
    df['change'] = df.groupby('city_town')['count'].diff().fillna(0).astype(int)
    df['change_%'] = df.groupby('city_town')['count'].pct_change().replace(pd.np.inf, 0).fillna(0)

    # merge population & calculate rate per 10,000 people
    df = df.merge(pop, on='city_town').sort_values(by='date')
    df['rate_per_10k'] = (df['count']/df['2017_population']) * 10000

    # filter for wanted columns
    df = df[['city_town', 'county', 'count', 'change', 'change_%', 'rate_per_10k', 'date']]

    # save & sync to google sheets
    df.to_csv('./data/clean/geo-ri-covid-19-clean.csv', index=False)
    sync_sheets(wb, df, 'city_town')

def clean_zip_codes(raw_zip):
    pint('[status] cleaning zip codes data')

def clean_facilities(raw_facility):
    pint('[status] cleaning facilties')
    df = pd.read_csv(raw_facility)

    # split low/high cases & fatalities
    cases = df["Cases"].str.split(" to ", n=1, expand=True) 
    fatalities = df["Fatalities"].str.split(" to ", n=1, expand=True) 
    df['cases_low'] = cases[0]
    df['cases_high'] = cases[1]
    df['fatalities_low'] = fatalities[0]
    df['fatalities_high'] = fatalities[1]

    # split facility name & city/town
    facility = df["Facility Name"].str.split("(", n=1, expand=True)
    df['facility_name'] = facility[0]
    df['city_town'] = facility[1].apply(clean_facility_city)
    df = df.drop(columns=['Cases', 'Fatalities', 'Facility Name'])

    # save file
    df.to_csv('./data/clean/facility-covid-19-clean.csv', index=False)