import numpy as np
import pandas as pd

import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.patches as mpatches

pd.plotting.register_matplotlib_converters()

plt.style.use('seaborn')
plt.style.use('fivethirtyeight')
date_format = mdates.DateFormatter('%#m/%#d')

footer = 'made by: SmirkyGraphs  |  site: ivizri.com  |  source: RIDOH'

def fit_trend(df, y):
    temp_df = df[df[y].notnull()].copy()
    z = np.polyfit(temp_df['date_ts'], temp_df[y], 1)
    p = np.poly1d(z)
    
    return p(df['date_ts'])

def testing_plot():
    print('\n[status] creating testing plots')
    df = pd.read_csv('./data/clean/revised-data-clean.csv', parse_dates=['date'])
    df = df[-14:] # last 14 days

    min_date = df['date'].min().strftime("%#m/%d/%y")
    max_date = df['date'].max().strftime("%#m/%d/%y")
    date_range = f'between {min_date} - {max_date}'

    fig, axs = plt.subplots(nrows=2, ncols=2, sharex=True)
    fig.suptitle("14-Day Trend: Testing", fontsize=16)
    
    # plot data
    axs[0,0].plot(df['date'], df['new positive labs'], c='dodgerblue', linewidth=2)
    axs[0,1].plot(df['date'], df['new negative labs'], c='dodgerblue', linewidth=2)
    axs[1,0].plot(df['date'], df['new total labs'], c='dodgerblue', linewidth=2)
    axs[1,1].plot(df['date'], df['%_positive'], c='dodgerblue', linewidth=2)

    # add trendline
    axs[0,0].plot(df['date'], fit_trend(df, 'new positive labs'), c='coral', linewidth=2, linestyle='--')
    axs[0,1].plot(df['date'], fit_trend(df, 'new negative labs'), c='coral', linewidth=2, linestyle='--')
    axs[1,0].plot(df['date'], fit_trend(df, 'new total labs'), c='coral', linewidth=2, linestyle='--')
    axs[1,1].plot(df['date'], fit_trend(df, '%_positive'), c='coral', linewidth=2, linestyle='--')

    axs[0,0].set_title('new positive labs')
    axs[0,1].set_title('new negative labs')
    axs[1,0].set_title('new total labs')
    axs[1,1].set_title('% new labs - positive')

    axs[1,0].xaxis.set_major_formatter(date_format)
    axs[1,1].xaxis.set_major_formatter(date_format)

    fig.tight_layout(rect=[0, 0.05, 1, 0.90])
    fig.set_size_inches(9, 7, forward=True)
    fig.text(x=.5, y=0.92, s=date_range, fontsize=10, ha='center')
    fig.text(x=0.97, y=0.03, s=footer, fontsize=10, ha='right')

    plt.savefig('./figures/testing_14_day_trend.png', dpi=150)

def hospital_plot():
    print('[status] creating hospital plots')
    df = pd.read_csv('./data/clean/revised-data-clean.csv', parse_dates=['date'])
    df = df[-14:] # last 14 days

    min_date = df['date'].min().strftime("%#m/%d/%y")
    max_date = df['date'].max().strftime("%#m/%d/%y")
    date_range = f'between {min_date} - {max_date}'

    fig, axs = plt.subplots(nrows=2, ncols=2, sharex=True)
    fig.suptitle("14-Day Trend: Hospital", fontsize=16)

    # plot data
    axs[0,0].plot(df['date'], df['new hospital admissions'], c='dodgerblue', linewidth=2)
    axs[0,1].plot(df['date'], df['new hospital discharges'], c='dodgerblue', linewidth=2)
    axs[1,0].plot(df['date'], df['hospital deaths'], c='dodgerblue', linewidth=2)
    axs[1,1].plot(df['date'], df['deaths'], c='dodgerblue', linewidth=2)

    # add trendline
    axs[0,0].plot(df['date'], fit_trend(df, 'new hospital admissions'), c='coral', linewidth=2, linestyle='--')
    axs[0,1].plot(df['date'], fit_trend(df, 'new hospital discharges'), c='coral', linewidth=2, linestyle='--')
    axs[1,0].plot(df['date'], fit_trend(df, 'hospital deaths'), c='coral', linewidth=2, linestyle='--')
    axs[1,1].plot(df['date'], fit_trend(df, 'deaths'), c='coral', linewidth=2, linestyle='--')

    axs[0,0].set_title('hospital admissions')
    axs[0,1].set_title('hospital discharges')
    axs[1,0].set_title('hospital deaths')
    axs[1,1].set_title('all deaths')

    axs[1,0].xaxis.set_major_formatter(date_format)
    axs[1,1].xaxis.set_major_formatter(date_format)

    fig.tight_layout(rect=[0, 0.05, 1, 0.90])
    fig.set_size_inches(9, 7, forward=True)
    fig.text(x=.5, y=0.92, s=date_range, fontsize=10, ha='center')
    fig.text(x=0.97, y=0.03, s=footer, fontsize=10, ha='right')

    plt.savefig('./figures/hospital_14_day_trend.png', dpi=150)

def testing_ma_plot():
    df = pd.read_csv('./data/clean/revised-data-clean.csv', parse_dates=['date'])

    min_date = df['date'].min().strftime("%#m/%d/%y")
    max_date = df['date'].max().strftime("%#m/%d/%y")
    date_range = f'between {min_date} - {max_date}'

    fig, axs = plt.subplots(nrows=2, ncols=2, sharex=True)
    fig.suptitle("7-Day Moving Avg: Testing", fontsize=16)

    # plot data
    axs[0,0].plot(df['date'], df['new positive labs'].rolling(7).mean(), c='dodgerblue', linewidth=2)
    axs[0,1].plot(df['date'], df['new negative labs'].rolling(7).mean(), c='dodgerblue', linewidth=2)
    axs[1,0].plot(df['date'], df['new total labs'].rolling(7).mean(), c='dodgerblue', linewidth=2)
    axs[1,1].plot(df['date'], df['%_positive'].rolling(7).mean(), c='dodgerblue', linewidth=2)

    axs[0,0].set_title('new positive labs')
    axs[0,1].set_title('new negative labs')
    axs[1,0].set_title('new total labs')
    axs[1,1].set_title('% new labs - positive')

    axs[1,0].xaxis.set_major_formatter(date_format)
    axs[1,1].xaxis.set_major_formatter(date_format)

    fig.tight_layout(rect=[0, 0.05, 1, 0.90])
    fig.set_size_inches(9, 7, forward=True)
    fig.text(x=.5, y=0.92, s=date_range, fontsize=10, ha='center')
    fig.text(x=0.97, y=0.03, s=footer, fontsize=10, ha='right')

    plt.savefig('./figures/testing_7_day_ma.png', dpi=150)

def hospital_ma_plot():
    df = pd.read_csv('./data/clean/revised-data-clean.csv', parse_dates=['date'])

    min_date = df['date'].min().strftime("%#m/%d/%y")
    max_date = df['date'].max().strftime("%#m/%d/%y")
    date_range = f'between {min_date} - {max_date}'

    fig, axs = plt.subplots(nrows=2, ncols=2, sharex=True)
    fig.suptitle("7-Day Moving Avg: Hospital", fontsize=16)

    # plot data
    axs[0,0].plot(df['date'], df['new hospital admissions'].rolling(7).mean(), c='dodgerblue', linewidth=2)
    axs[0,1].plot(df['date'], df['new hospital discharges'].rolling(7).mean(), c='dodgerblue', linewidth=2)
    axs[1,0].plot(df['date'], df['hospital deaths'].rolling(7).mean(), c='dodgerblue', linewidth=2)
    axs[1,1].plot(df['date'], df['deaths'].rolling(7).mean(), c='dodgerblue', linewidth=2)

    axs[0,0].set_title('hospital admissions')
    axs[0,1].set_title('hospital discharges')
    axs[1,0].set_title('hospital deaths')
    axs[1,1].set_title('all deaths')

    axs[1,0].xaxis.set_major_formatter(date_format)
    axs[1,1].xaxis.set_major_formatter(date_format)

    fig.tight_layout(rect=[0, 0.05, 1, 0.90])
    fig.set_size_inches(9, 7, forward=True)
    fig.text(x=.5, y=0.92, s=date_range, fontsize=10, ha='center')
    fig.text(x=0.97, y=0.03, s=footer, fontsize=10, ha='right')

    plt.savefig('./figures/hospital_7_day_ma.png', dpi=150)

def city_rate_plot():
    df = pd.read_csv('./data/clean/geo-ri-covid-19-clean.csv', parse_dates=['date'])
    df = df.sort_values(by=['city_town', 'date'])

    g = sns.FacetGrid(df, col="city_town", col_wrap=7, height=3)
    g = g.map(plt.plot, "date", "rate_per_10k", marker=",", linewidth=2.5)
    g.axes[0].xaxis.set_major_formatter(date_format)
    
    g.savefig("./figures/cities_rate.png", dpi=150)

def then_v_now():
    df = pd.read_csv('./data/clean/revised-data-clean.csv', parse_dates=['date'])

    dates = df['date_scraped'].unique()
    start = df.loc[df['date_scraped'] == dates[0]]
    current = df.loc[df['date_scraped'] == dates[-1]]

    # save date_scraped for each set
    start_date = start['date_scraped'].values[0]
    current_date = current['date_scraped'].values[0]

    # set date as index and select only deaths
    start = start.set_index('date')['deaths']
    current = current.set_index('date')['deaths']
    current = current.reindex_like(start)

    # combine data sets
    df = pd.concat([start, current], axis=1).reset_index()
    df.columns = ['date', start_date, current_date]

    # 7 day moving average
    df[df.columns[1]] = df[df.columns[1]].rolling(7).mean()
    df[df.columns[2]] = df[df.columns[2]].rolling(7).mean()

    fig, axs = plt.subplots(nrows=1, ncols=1, sharex=True)
    fig.suptitle("COVID-19 Deaths Then vs. Now", fontsize=16)
    sub_head = '7-day moving average deaths up to 5/9'

    # plot data
    axs.plot(df['date'], df[df.columns[1]], c='dodgerblue', linewidth=2)
    axs.plot(df['date'], df[df.columns[2]], c='coral', linewidth=2)
    axs.xaxis.set_major_formatter(date_format)

    fig.tight_layout(rect=[0, 0.05, 1, 0.90])
    fig.set_size_inches(9, 7, forward=True)
    fig.text(x=.5, y=0.92, s=sub_head, fontsize=10, ha='center')
    fig.text(x=0.97, y=0.03, s=footer, fontsize=10, ha='right')

    patch = mpatches.Patch(facecolor='dodgerblue', label='data from 5/10/2020')
    fig.legend(handles=[patch], loc='upper left', bbox_to_anchor=[0.78, 1], fontsize=10)    

    patch = mpatches.Patch(facecolor='coral', label='data from 6/15/2020')
    fig.legend(handles=[patch], loc='upper left', bbox_to_anchor=[0.78, 0.97], fontsize=10) 
    plt.savefig('./figures/daily_deaths_then_vs_now.png', dpi=150)