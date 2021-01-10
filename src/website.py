import pandas as pd
import json

with open('./config.json') as config:
    fp = json.load(config)['api']

def pad_num(num):
    num = str(int(num))
    num = num.zfill(2).replace('0', '&nbsp;')

    return num

def change_fmt(num):
    if num >= 0:
        return f"( +{num} )"
    else:
        return f"( {num} )"
    
def daily_death_dates():
    df = pd.read_csv('./data/reports/full_death_change.csv', parse_dates=['date_scraped', 'date'])
    df = df[df['date_scraped'] == df['date_scraped'].max()].drop(columns='date_scraped')

    df['deaths'] = df['deaths'].apply(pad_num)
    df['date'] = df['date'].dt.strftime('%m/%d/%Y')
    
    df = df.to_json(orient="records").replace("\\","")
    
    return df

def hospital_capacity():
    df = pd.read_csv('./data/reports/hospital_capacity.csv')
    df['%_capacity_covid'] = df['%_capacity_covid'].map("{:.1%}".format)

    df.loc[df['metric']=='clinical_beds', 'metric'] = 'Clinical Beds'
    df.loc[df['metric']=='icu_beds', 'metric'] = 'ICU Beds'
    df = df.drop(columns=['current', 'capacity'])

    df = df.to_json(orient="records")
    
    return df

def daily_update(data):
    
    def update_json(lookup, v1, v2=''):
        if d['id'] == lookup:
            d['total'] = v1
            d['change'] = v2
    
    # get most recent date
    df = pd.read_csv('./data/clean/ri-covid-19-clean.csv', parse_dates=['date'])
    df = df[df['date']==df['date'].max()]

    # get values
    hosp = int(df[df['metric']=='currently hospitalized']['count'].iloc[0])
    hosp_chng = change_fmt(df[df['metric']=='currently hospitalized']['new_cases'].iloc[0])
    icu = int(df[df['metric']=='currently in icu']['count'].iloc[0])
    icu_chng = change_fmt(df[df['metric']=='currently in icu']['new_cases'].iloc[0])
    vent = int(df[df['metric']=='currently on ventilator']['count'].iloc[0])
    vent_chng = change_fmt(df[df['metric']=='currently on ventilator']['new_cases'].iloc[0])

    # non-hospital data
    df = pd.read_csv('./data/clean/revised-data-clean.csv', parse_dates=['date_scraped', 'date'])
    dates = df['date_scraped'].unique()[-2:]

    prior = df[df['date_scraped']==dates[0]].tail(1)
    current = df[df['date_scraped']==dates[1]].tail(1)

    # get values
    deaths = current['total deaths'].iloc[0] - prior['total deaths'].iloc[0]
    pos_labs = current['total positive labs'].iloc[0] - prior['total positive labs'].iloc[0]
    pct_labs = current['%_positive_labs'].iloc[0]
    pos_people = current['total people positive'].iloc[0] - prior['total people positive'].iloc[0]
    pct_people = current['%_new_people_positive'].iloc[0]
    
    # add data to json
    for d in data:   
        update_json('daily-admissions', hosp, hosp_chng)
        update_json('daily-icu', icu, icu_chng)
        update_json('daily-vent', vent, vent_chng)
        
        update_json('daily-deaths', int(deaths))
        update_json('daily-positive-labs', f'{int(pos_labs):,}')
        update_json('daily-labs-pct', f'{pct_labs:.1%}')
        update_json('daily-positive-people', f'{int(pos_people):,}')
        update_json('daily-people-pct', f'{pct_people:.1%}')
        
    return data

def current_total(data):
    
    def update_json(lookup, v1, v2=''):
        if d['id'] == lookup:
            d['total'] = v1
            d['sub'] = v2

    df = pd.read_csv('./data/clean/revised-data-clean.csv', parse_dates=['date_scraped', 'date'])
    df = df.fillna(method='ffill')
    df = df[df['date_scraped']==df['date_scraped'].max()].tail(1)
    
    total_tests = f'{df["total tested"].iloc[0]:,}'
    total_neg = f'{df["total negative labs"].iloc[0]:,} total negative labs'
    total_pos = f'{df["total positive labs"].iloc[0]:,}'
    pct_labs_pos = f'{df["total positive labs"].iloc[0]/df["total tested"].iloc[0]:.1%} of total tests were positive'
    total_ppl = f'{int(df["total people tested"].iloc[0]):,}'
    total_ppl_neg = f'{int(df["total people negative"].iloc[0]):,} total negative people'
    total_ppl_pos = f'{int(df["total people positive"].iloc[0]):,}'
    pct_ppl_pos = f'{df["total people positive"].iloc[0]/df["total people tested"].iloc[0]:.1%} of people tested were positive'
    total_deaths = f'{df["total deaths"].iloc[0]:,}'
    total_hosp_deaths = f'{int(df["cumulative hospital deaths"].iloc[0]):,} hospital deaths'
    total_hosp_adm = f'{int(df["cumulative hospital admissions"].iloc[0]):,}'
    total_hosp_dis = f'{int(df["cumulative hospital discharges"].iloc[0]):,} hospital discharges'
    
    # add data to json
    for d in data:   
        update_json('total-labs', total_tests, total_neg)
        update_json('total-pos-labs', total_pos, pct_labs_pos)
        update_json('total-people-tested', total_ppl, total_ppl_neg)
        update_json('total-people-positive', total_ppl_pos, pct_ppl_pos)
        update_json('total-deaths', total_deaths, total_hosp_deaths)
        update_json('total-hosp-admittied', total_hosp_adm, total_hosp_dis)
        
    return data

def update_data():

    with open(f'{fp}/daily_update.json', 'r') as f:
        data = json.load(f)
        update = daily_update(data)
        
    with open(f'{fp}/daily_update.json', 'w') as f:
        f.write(json.dumps(update))
        
    with open(f'{fp}/totals.json', 'r') as f:
        data = json.load(f)
        update = current_total(data)

    with open(f'{fp}/totals.json', 'w') as f:
        f.write(json.dumps(update))
    
    with open(f'{fp}/daily_death_dates.json', 'w') as f:
        f.write(daily_death_dates())
        
    with open(f'{fp}/capacity.json', 'w') as f:
        f.write(hospital_capacity())
    