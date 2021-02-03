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
    hosp_capacity(df)def schools_count_report(df):

    def count_schools_u5(df, col):
        df = df[df['type'] == col]

        total_schools = df.groupby('date').size()
        df_stu = df[df['total_student_cases_high']<5].groupby('date').size()
        df_staff = df[df['total_staff_cases_high']<5].groupby('date').size()

        df = pd.concat([df_stu, df_staff, total_schools], axis=1)
        df.columns = ['u5_student_cases', 'u5_staff_cases', 'total_schools']

        df['%_schools_u5_student'] = df['u5_student_cases']/df['total_schools']
        df['%_schools_u5_staff'] = df['u5_staff_cases']/df['total_schools']

        df['type'] = col

        return df

    in_person = count_schools_u5(df, 'in person')
    virtual = count_schools_u5(df, 'virtual')
    df = pd.concat([in_person, virtual]).sort_values(by=['date', 'type'])

    diff = df.groupby(['type']).diff().fillna(0).iloc[:, 0:3]
    diff.columns = [f"chng_{col}" for col in list(diff)]

    df = pd.concat([df, diff], axis=1).reset_index()
    df.to_csv('./data/reports/schools_count.csv', index=False)

def school_update_tables(df):
    cols = ['school', 'lea', 'type', 'total_student_cases_avg', 'total_staff_cases_avg', 'date']
    df = df[cols]

    df = df.groupby(['school', 'type', 'date']).sum()

    diff = df.groupby(['school', 'type']).diff().fillna(0)
    diff.columns = [f"chng_{col}" for col in list(diff)]

    df = pd.concat([df, diff], axis=1).reset_index()
    df.to_csv('./data/reports/school_cases.csv', index=False)

    # get wanted columns & seperate vr & person
    df2 = df[df['date']==df['date'].max()]
    value_cols = list(df2)[3:]
    col_order = [
        'school',
        'total_student_cases_avg',
        'chng_total_student_cases_avg',
        'total_staff_cases_avg',
        'chng_total_staff_cases_avg'
    ]

    per = df2[df2['type']=='in person'].copy()
    per[value_cols] = per[value_cols].astype(int)
    per[col_order].to_csv('./data/reports/in_person_schools.csv', index=False)

    vr = df2[df2['type']=='virtual'].copy()
    vr[value_cols] = vr[value_cols].astype(int)
    vr[col_order].to_csv('./data/reports/virtual_schools.csv', index=False)


def run_school_reports():
    df = pd.read_csv('./data/clean/schools-covid-19-clean.csv', parse_dates=['date'])
    df = df[~df['school'].isin(['Other', 'Total'])]
    schools_count_report(df)
    school_update_tables(df)