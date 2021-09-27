import pandas as pd
import numpy as np

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

def run_trend_reports():
    df = pd.read_csv('./data/clean/revised-data-clean.csv', parse_dates=['date_scraped', 'date'])
    
    # change in deaths
    full_death_change(df)
    first_death_change(df)
    hosp_capacity(df)

def schools_count_report(df):

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

def nursing_weekly_short_staffed(df):
    print('[status] getting cms short staffed')
    cols = [
        'week_ending',
        'provider_name',
        'shortage_of_nursing_staff',
        'shortage_of_clinical_staff',
        'shortage_of_aides',
        'shortage_of_other_staff'
    ]

    weekly = df[cols].dropna(axis=0).replace('Y', True).replace('N', False)
    df = weekly.groupby('week_ending').sum()
    df['total_providers_reporting'] = weekly.groupby('week_ending').size()
    
    df_dif = df.div(df['total_providers_reporting'], axis=0).drop(columns='total_providers_reporting')
    df_dif.columns = df_dif.columns.str.replace('shortage_of_', '%_short_')

    change = df.diff().fillna(0).drop(columns='total_providers_reporting')
    change.columns = change.columns.str.replace('shortage_of_', 'change_')
    df = df.merge(change, on='week_ending').merge(df_dif, on='week_ending')
    df.to_csv('./data/reports/nursing_home_weekly_staffing.csv')

def count_short_staffed(df):
    # most recent 
    df = df[df['week_ending'] == df['week_ending'].max()].reset_index()

    # filter columns
    cols = [
        'provider_name',
        'shortage_of_nursing_staff', 
        'shortage_of_clinical_staff',
        'shortage_of_aides',
        'shortage_of_other_staff'
    ]

    df = df[cols].dropna(axis=0).replace('Y', True).replace('N', False)

    # count of how many positions each home is short staffed
    df['total nursing homes'] = df.sum(axis=1)
    count_short = df['total nursing homes'].value_counts()

    count_short = count_short.reset_index().sort_values(by='index')
    count_short.columns = ['positions short staffed', 'homes short staffed']
    count_short['total nursing homes'] = df.shape[0]
    count_short['% short staffed'] = count_short['homes short staffed']/count_short['total nursing homes']
    count_short = count_short.drop(columns=['total nursing homes'])
    count_short.to_csv('./data/reports/nursing_home_staff_shortage_count.csv', index=False)
    
def nursing_weekly_ppe(df):
    print('[status] getting lacking ppe supply')
    cols = [
        'week_ending',
        'provider_name',
        'one_week_supply_of_n95_masks',
        'one_week_supply_of_surgical',
        'one_week_supply_of_eye',
        'one_week_supply_of_gowns',
        'one_week_supply_of_gloves',
        'one_week_supply_of_hand',
    ]

    weekly = df[cols]
    weekly = weekly.dropna(axis=0).replace('Y', True).replace('N', False)
    df = weekly.groupby('week_ending').sum()
    total_reporting = weekly.groupby('week_ending').size()
    
    # get reverse (lack of supply instead of has)
    df_neg = df.rsub(total_reporting, axis=0)
    df_neg['total_providers_reporting'] = total_reporting
    
    df_pct = df_neg.div(df_neg['total_providers_reporting'], axis=0).drop(columns='total_providers_reporting')
    df_pct.columns = df_pct.columns.str.replace('one_week_supply_of', '%_lacking_1week')

    df_dif = df_neg.diff().fillna(0).drop(columns='total_providers_reporting')
    df_dif.columns = df_dif.columns.str.replace('one_week_supply_of', 'change')
    
    df_neg['total_shortage'] = df_neg.sum(axis=1)
    df = df_neg.merge(df_pct, on='week_ending').merge(df_dif, on='week_ending')
    df.to_csv('./data/reports/nursing_home_weekly_ppe.csv')

def nursing_home_metrics(df):
    print('[status] getting nursing home cases/deaths metrics')
    cols = [
        'week_ending',
        'provider_name',
        'residents_weekly_admissions_covid_19',
        'residents_total_admissions_covid_19',
        'residents_weekly_all_deaths',
        'residents_total_all_deaths', 
        'residents_weekly_covid_19_deaths',
        'residents_total_covid_19_deaths',
        'residents_weekly_confirmed_covid_19',
        'residents_total_confirmed_covid_19',
        'staff_weekly_confirmed_covid_19',
        'staff_total_confirmed_covid_19',
        'staff_weekly_covid_19_deaths',
        'staff_total_covid_19_deaths'
    ]

    df = df[cols]
    df = df.dropna(axis=0).replace('Y', True).replace('N', False)
    df = df.groupby('week_ending').sum()
    df.to_csv('./data/reports/nursing_home_metrics.csv')

def nursing_weekly_deaths(df):
    print('[status] getting cms weekly deaths')
    cols = [
        'week_ending',
        'provider_name',
        'residents_total_all_deaths',
        'residents_total_covid_19_deaths'
    ]

    df = df[cols].dropna(axis=0)
    df = df.groupby('week_ending').sum()
    df['%_total_covid'] = df['residents_total_covid_19_deaths']/df['residents_total_all_deaths']
    df.to_csv('./data/reports/nursing_home_weekly_deaths.csv')

def nursing_weekly_capacity(df):
    cols = [
        'week_ending',
        'provider_name',
        'total_number_of_occupied_beds',
        'number_of_all_beds'
    ]

    weekly = df[cols].groupby(['week_ending']).sum()
    weekly['total_reporting'] = df.groupby(['week_ending']).size()
    weekly['percent_occupied'] = weekly['total_number_of_occupied_beds']/weekly['number_of_all_beds']
    weekly.to_csv('./data/reports/nursing_home_weekly_capacity.csv')

def nursing_weekly_cases(df):
    cols = [
        'week_ending',
        'provider_name',
        'residents_total_confirmed_covid_19',
        'staff_total_confirmed_covid_19'
    ]

    weekly = df[cols].groupby(['week_ending']).sum()
    weekly.to_csv('./data/reports/nursing_home_weekly_cases.csv')

def nursing_provider_deaths(df):
    cols = [
        'week_ending',
        'provider_name',
        'total_number_of_occupied_beds',
        'residents_total_all_deaths',
        'residents_total_covid_19_deaths',
        'residents_weekly_covid_19_deaths',
        'staff_weekly_covid_19_deaths',
        'staff_total_covid_19_deaths',
        'weekly_resident_covid_19_deaths_per_1_000_residents',
        'total_resident_covid_19_deaths_per_1_000_residents',
        'total_residents_covid_19_deaths_as_a_percentage_of_confirmed_covid_19_cases'
    ]

    prov = df[cols]
    max_date = prov['week_ending'].max()
    prov = prov[prov['week_ending'] == max_date].dropna(axis=0)
    prov = prov.groupby('provider_name').sum()
    prov['%_total_covid'] = prov['residents_total_covid_19_deaths']/prov['residents_total_all_deaths']
    prov['week_ending'] = max_date
    prov.to_csv('./data/reports/nursing_home_provider_deaths.csv')

def nursing_provider_capacity(df):
    cols = [
        'week_ending',
        'provider_name',
        'number_of_all_beds',
        'total_number_of_occupied_beds'
    ]

    prov = df[cols]
    max_date = prov['week_ending'].max()
    prov = prov[prov['week_ending'] == prov['week_ending'].max()]
    prov = prov.groupby('provider_name').sum()
    prov['percent_occupied'] = prov['total_number_of_occupied_beds']/prov['number_of_all_beds']

    prov = prov.dropna()
    prov['week_ending'] = max_date
    prov.to_csv('./data/reports/nursing_home_provider_capacity.csv')

def nursing_provider_cases(df):
    cols = [
        'week_ending',
        'provider_name',
        'total_number_of_occupied_beds',
        'residents_total_confirmed_covid_19',
        'residents_weekly_confirmed_covid_19',
        'staff_total_confirmed_covid_19',
        'staff_weekly_confirmed_covid_19',
        'weekly_resident_confirmed_covid_19_cases_per_1_000_residents',
        'total_resident_confirmed_covid_19_cases_per_1_000_residents'
    ]

    prov = df[cols]
    max_date = prov['week_ending'].max()
    prov = prov[prov['week_ending'] == prov['week_ending'].max()]
    prov = prov.groupby('provider_name').sum()
    prov['week_ending'] = max_date
    prov.to_csv('./data/reports/nursing_home_provider_cases.csv')

def nursing_provider_ppe(df):
    cols = [
        'week_ending',
        'provider_name',
        'one_week_supply_of_n95_masks',
        'one_week_supply_of_surgical',
        'one_week_supply_of_eye',
        'one_week_supply_of_gowns',
        'one_week_supply_of_gloves',
        'one_week_supply_of_hand'
    ]

    prov = df[cols]
    max_date = prov['week_ending'].max()
    prov = prov[prov['week_ending'] == prov['week_ending'].max()]
    prov = prov.dropna(axis=0).replace('Y', True).replace('N', False)
    prov = prov.groupby('provider_name').sum()

    # get reverse (lack of supply instead of has)
    df_neg = prov.rsub(1, axis=0)
    df_neg['total_shortage'] = df_neg.sum(axis=1)
    df_neg['week_ending'] = max_date
    df_neg.to_csv('./data/reports/nursing_home_provider_ppe.csv')

def nursing_provider_staffing(df):
    cols = [
        'week_ending',
        'provider_name',
        'shortage_of_nursing_staff', 
        'shortage_of_clinical_staff',
        'shortage_of_aides',
        'shortage_of_other_staff'
    ]

    prov = df[cols]
    max_date = prov['week_ending'].max()
    prov = prov[prov['week_ending'] == prov['week_ending'].max()]
    prov = prov.dropna(axis=0).replace('Y', True).replace('N', False)
    prov = prov.groupby('provider_name').sum()

    # get reverse (lack of supply instead of has)
    prov['total_shortage'] = prov.sum(axis=1)
    prov['week_ending'] = max_date
    prov.to_csv('./data/reports/nursing_home_provider_staffing.csv')

def nursing_prov_staff_vaccination(df):
    cols = [
        'provider_name',
        'week_ending',
        'number_of_all_healthcare_personnel_eligible_to_work_in_this_facility_for_at_least_1_day_this_week',
        'number_of_all_healthcare_personnel_eligible_to_work_in_this_facility_for_at_least_1_day_this_week_who_received_a_completed_covid_19_vaccination_at_any_time',
        'number_of_all_healthcare_personnel_eligible_to_work_in_this_facility_for_at_least_1_day_this_week_who_received_a_partial_covid_19_vaccination_at_any_time',
        'recent_percentage_of_current_healthcare_personnel_who_received_a_completed_covid_19_vaccination_at_any_time',
        'percentage_of_current_healthcare_personnel_who_received_a_completed_covid_19_vaccination_at_any_time',
        'percentage_of_current_healthcare_personnel_who_received_a_partial_covid_19_vaccination_at_any_time'
    ]

    col_names = [
        'provider_name', 
        'week_ending', 
        'all_employees', 
        'employees_fully_vac', 
        'employees_part_vac', 
        'recent_pct_fully_vac',
        'pct_fully_vac',
        'pct_part_vac'
    ]

    df = df[cols].sort_values(by=['provider_name', 'week_ending'])
    df.columns = col_names

    df = df.replace('', np.nan)

    df.loc[df['all_employees'].isnull(), 'prior_week_used'] = True
    df[col_names[2:]] = df[col_names[2:]].astype(float)
    for col in col_names[2:]: # forward fill if a provider didn't update most recent week
        df[col] = df.groupby(['provider_name'])[col].ffill()

    df.loc[df['prior_week_used'] == True, 'provider_name'] = df['provider_name'] + '*'
    df = df.drop(columns='prior_week_used')

    df[col_names[-3:]] = df[col_names[-3:]] / 100
    df['not_vac'] = df['all_employees'] - df['employees_fully_vac']

    dates = df['week_ending'].drop_duplicates().nlargest(2).values
    df = df[df['week_ending'].isin(dates)].reset_index(drop=True)
    
    cols = [
        'all_employees',
        'employees_fully_vac',
        'employees_part_vac',
        'recent_pct_fully_vac',
        'pct_fully_vac'
    ]

    for col in cols:
        df[f'{col}_change'] = df[col] - df.groupby('provider_name')[col].shift()

    df = df[df['week_ending']==df['week_ending'].max()].fillna(0).reset_index(drop=True)
    df.to_csv('./data/reports/nursing_home_staff_vaccination.csv', index=False)

def nursing_home_staff_weekly_vac(df):
    cols = [
        'provider_name',
        'week_ending',
        'number_of_all_healthcare_personnel_eligible_to_work_in_this_facility_for_at_least_1_day_this_week',
        'number_of_all_healthcare_personnel_eligible_to_work_in_this_facility_for_at_least_1_day_this_week_who_received_a_completed_covid_19_vaccination_at_any_time',
        'number_of_all_healthcare_personnel_eligible_to_work_in_this_facility_for_at_least_1_day_this_week_who_received_a_partial_covid_19_vaccination_at_any_time',
    ]

    col_names = [
        'provider_name', 
        'week_ending', 
        'all_employees', 
        'employees_fully_vac', 
        'employees_part_vac', 
    ]

    df = df[cols].sort_values(by=['provider_name', 'week_ending'])
    df.columns = col_names

    df = df.replace('', np.nan)
    df[col_names[2:]] = df[col_names[2:]].astype(float)

    # mark any homes that didn't report in the most recent week & fill with prior week
    df.loc[df['all_employees'].isnull(), 'prior_week_used'] = True
    for col in col_names[2:]:
        df[col] = df.groupby(['provider_name'])[col].ffill()
        
    df.loc[df['prior_week_used'] == True, 'provider_name'] = df['provider_name'] + '*'
    df = df.drop(columns='prior_week_used')

    df['not_vac'] = df['all_employees'] - df['employees_fully_vac'] # get not vac count

    df = df.groupby('week_ending', as_index=False).sum()
    df['percent_fully'] = df['employees_fully_vac']/df['all_employees']

    df.dropna(how='any', axis=0).to_csv('./data/reports/nursing_home_staff_weekly_vac.csv', index=False)

def run_cms_reports():
    df = pd.read_csv('./data/raw/cms-nursing-homes.csv', parse_dates=['week_ending'], low_memory=False)

    count_short_staffed(df)
    nursing_weekly_short_staffed(df)
    nursing_weekly_deaths(df)
    #nursing_weekly_ppe(df)
    nursing_weekly_capacity(df)
    nursing_weekly_cases(df)

    nursing_home_metrics(df)
    nursing_provider_deaths(df)
    nursing_provider_capacity(df)
    nursing_provider_cases(df)
    #nursing_provider_ppe(df)
    nursing_provider_staffing(df)

    nursing_prov_staff_vaccination(df)
    nursing_home_staff_weekly_vac(df)
