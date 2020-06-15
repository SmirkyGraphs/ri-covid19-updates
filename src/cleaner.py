import pandas as pd
import pygsheets
import json

with open('./config.json') as config:
    creds = json.load(config)['google']

# google sheets authentication
api = pygsheets.authorize(service_file=creds, retries=5)
wb = api.open('ri-covid-19')

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

def sync_sheets(wb, df, sheet_name):
    print(f'[status] syncing google sheet {sheet_name}')
    # open the google spreadsheet
    sheet = wb.worksheet_by_title(f'{sheet_name}')
    sheet.set_dataframe(df, (1,1))

def clean_general(fname):
    print('[status] cleaning statwide general info')
    df = pd.read_csv(f'./data/raw/{fname}.csv')
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
    df['change_%'] = df.groupby('city_town')['count'].pct_change().replace(pd.np.inf, 0).fillna(0)

    # merge population & calculate rate per 10,000 people
    df = df.merge(pop, on='city_town').sort_values(by='date')
    df['rate_per_10k'] = (df['count']/df['2017_population']) * 10000

    # filter for wanted columns
    df = df[['city_town', 'county', 'count', 'change', 'change_%', 'rate_per_10k', 'date']]

    # save & sync to google sheets
    df.to_csv('./data/clean/geo-ri-covid-19-clean.csv', index=False)
    sync_sheets(wb, df, 'city_town')

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
    df['change_%'] = df.groupby('zip_code')['count'].pct_change().replace(pd.np.inf, 0).fillna(0)

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

    recent_dates = pd.np.sort(df['date'].unique())[-2:]
    df.loc[df['date'] == recent_dates[1], 'date_bin'] = 'Most Recent'
    df.loc[df['date'] == recent_dates[0], 'date_bin'] = 'Prior Week'

    # save file
    df.to_csv('./data/clean/nurse-homes-covid-19-clean.csv', index=False)

def clean_revised(fname):
    print('[status] cleaning revised data')
    df = pd.read_csv(f'./data/raw/{fname}.csv', parse_dates=['date'])

    # replace null label -- with 0
    df['deaths'] = df['deaths'].replace('--', 0)
    df['total deaths'] = df['total deaths'].replace('--', 0)

    df['new total labs'] = df['new positive labs'] + df['new negative labs']
    df['%_positive'] = df['new positive labs']/df['new total labs']
    df['date_ts'] = df['date'].apply(lambda x: pd.datetime.toordinal(x))

    df.to_csv('./data/clean/revised-data-clean.csv', index=False)