import pandas as pd
import pygsheets
import json

with open('./config.json') as config:
    creds = json.load(config)['google']

def convert_int(value):
    value = str(value).replace('approximately', '')
    value = value.replace('approx.', '').strip()
    value = value.replace(',', '').replace('.0', '').replace('.', '')
    
    return int(value)

def clean_statewide(raw_state):
    df = pd.read_csv(raw_state)
    # re name metrics to shorten them
    df.loc[df['metric'].str.contains('positive'), 'metric'] = 'RI positive cases'
    df.loc[df['metric'].str.contains('negative'), 'metric'] = 'RI negative results'
    df.loc[df['metric'].str.contains('self-quarantine'), 'metric'] = 'instructed to self-quarantine'
    df.loc[df['metric'].str.contains('hospitalized'), 'metric'] = 'currently hospitalized'
    df.loc[df['metric'].str.contains('die'), 'metric'] = 'total deaths'
    df.loc[df['metric'].str.contains('fatalities'), 'metric'] = 'total deaths'
    df.loc[df['metric'].str.contains('intensive care'), 'metric'] = 'currently in icu'

    # convert count to intiger
    df['count'] = df['count'].apply(convert_int)

    # pivot to get total tests given out then un-pivot 
    df = df.pivot(index='date', columns='metric', values='count').reset_index()
    df['RI total tests'] = df['RI positive cases'] + df['RI negative results']
    df = df.melt(col_level=0, id_vars=['date'], value_name='count').sort_values(by=['date', 'metric'])

    # get daily changes
    df['count'] = df['count'].fillna(0)
    df['new_cases'] = df.groupby('metric')['count'].diff().fillna(0).astype(int)
    df['change_%'] = df.groupby('metric')['count'].pct_change().replace(pd.np.inf, 0).fillna(0)

    return df

def clean_geographic(raw_geo):
    df = pd.read_csv(raw_geo)
    pop = pd.read_csv('./data/files/population_est_2017.csv')

    # remove under 5 surpressed values
    df['count'] = df['count'].replace('fewer than 5', 0)
    df['count'] = df['count'].replace('<5', 0).astype(int)

    # get daily changes
    df['change'] = df.groupby('city_town')['count'].diff().fillna(0).astype(int)
    df['change_%'] = df.groupby('city_town')['count'].pct_change().replace(pd.np.inf, 0).fillna(0)

    # merge population & calculate rate per 10,000 people
    df = df.merge(pop, on='city_town').sort_values(by='date')
    df['rate_per_10k'] = (df['count']/df['2017_population']) * 10000

    # filter for wanted columns
    df = df[['city_town', 'count', 'change', 'change_%', 'rate_per_10k', 'date']]

    return df   

def sync_sheets(sh, df, sheet_name):
    print(f'[status] syncing google sheet {sheet_name}')
    # open the google spreadsheet
    sheet = sh.worksheet_by_title(f'{sheet_name}')
    sheet.set_dataframe(df, (1,1))

def clean_data(raw_state, raw_geo):
    print('[status] cleaning data & calculating changes')
    clean_state = clean_statewide(raw_state)
    clean_geo = clean_geographic(raw_geo)   

    # save files to clean data folder
    clean_state.to_csv('./data/clean/ri-covid-19-clean.csv', index=False)
    clean_geo.to_csv('./data/clean/geo-ri-covid-19-clean.csv', index=False)

    # sync to google sheets
    api = pygsheets.authorize(service_file=creds)
    sh = api.open('ri-covid-19')
    sync_sheets(sh, clean_state, 'statewide')
    sync_sheets(sh, clean_geo, 'city_town')
