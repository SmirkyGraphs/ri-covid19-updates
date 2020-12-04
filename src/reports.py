import pandas as pd

def full_death_change(df):
    df = df[['date_scraped', 'date', 'deaths']]

    min_date = df['date'].min()
    max_date = df['date'].max()
    index = pd.date_range(min_date, max_date)
    multi_index = pd.MultiIndex.from_product([df['date_scraped'].unique(), index])

    df = df.set_index(['date_scraped', 'date'])
    df = df.reindex(multi_index).fillna(0)

    chng = df.groupby(level=1).diff()
    chng = chng[chng['deaths'] != 0].dropna().reset_index()
    chng.columns = ['date_scraped', 'date', 'deaths']
    chng.to_csv('./data/reports/full_death_change.csv', index=False)

def first_death_change(df):
    df = df[['date_scraped', 'date', 'deaths']]

    # get first recorded value
    fst = df.drop_duplicates(subset=['date'], keep='first')
    fst = fst.rename(columns={'deaths': 'first_reported_deaths', 'date_scraped': 'first_date_scraped'})

    # get current value
    df = df[df['date_scraped'] == df['date_scraped'].max()]
    df = df.rename(columns={'deaths': 'current_deaths'})

    # merge, get difference, order columns, save
    df = df.merge(fst, on='date')
    df['diff'] = df['current_deaths'] - df['first_reported_deaths']
    df = df[['date', 'first_date_scraped', 'first_reported_deaths', 'date_scraped', 'current_deaths', 'diff']]
    df.to_csv('./data/reports/first_death_change.csv', index=False)

def hosp_capacity(df):
    print('[status] getting hospital capacity % covid')

    # get hospital total icu/clincal beds
    cap = pd.read_csv('./data/external/hosp-capacity.csv')
    cap = cap.rename(columns={'ICU Total Beds': 'icu_beds', 'Clinical Total Beds': 'clinical_beds'})
    cap = cap[['icu_beds', 'clinical_beds']].sum().reset_index()
    cap.columns = ['metric', 'capacity']

    # get current hospital stats
    df = df[['currently hospitalized', 'icu']].dropna(axis=0, how='all')[-1:]
    df = df.rename(columns={'currently hospitalized': 'clinical_beds', 'icu': 'icu_beds'})
    df = df.squeeze().reset_index()
    df.columns = ['metric', 'current']

    # combine & save
    df = df.merge(cap, how='left', on='metric')
    df['%_capacity_covid'] = df['current']/df['capacity']
    df.to_csv('./data/reports/hospital_capacity.csv', index=False)

def run_reports():
    df = pd.read_csv('./data/clean/revised-data-clean.csv', parse_dates=['date_scraped', 'date'])
    
    # change in deaths
    full_death_change(df)
    first_death_change(df)
    hosp_capacity(df)