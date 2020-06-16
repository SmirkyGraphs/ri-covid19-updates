import pandas as pd

def death_change(df, scraped, idx, report_name):
    # get most recent 2 dates
    prior_date = df.loc[df['date_scraped'] == scraped[idx]]
    current = df.loc[df['date_scraped'] == scraped[-1]]

    # set date as index and select only deaths
    prior_date = prior_date.set_index('date')['deaths']
    current = current.set_index('date')['deaths']

    if report_name == 'daily':
        prior_date = prior_date.reindex_like(current).fillna(0)

    # get change between 2 dates
    df = (current - prior_date).reset_index()
    change = df[df['deaths'] != 0].dropna(axis=0)
    change.to_csv(f'./data/reports/{report_name}_death_change.csv', index=False)

def run_reports():
    df = pd.read_csv('./data/clean/revised-data-clean.csv', parse_dates=['date'])
    scraped = df['date_scraped'].unique().tolist()
    
    # change in deaths
    death_change(df, scraped, -2, 'daily')
    death_change(df, scraped, 0, 'start')