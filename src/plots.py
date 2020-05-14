import numpy as np
import pandas as pd

import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

plt.style.use('seaborn')
plt.style.use('fivethirtyeight')
date_format = mdates.DateFormatter('%#m/%#d')

footer = 'made by: SmirkyGraphs  |  site: ivizri.com  |  source: RIDOH'

def testing_plot():
    print('\n[status] creating testing plots')
    df = pd.read_csv('./data/clean/revised-data-clean.csv', parse_dates=['Date'])
    df = df[-14:] # last 14 days

    min_date = df['Date'].min().strftime("%#m/%d/%y")
    max_date = df['Date'].max().strftime("%#m/%d/%y")
    date_range = f'between {min_date} - {max_date}'

    def fit_trend(y):
        temp_df = df[df[y].notnull()].copy()
        z = np.polyfit(temp_df['Date_ts'], temp_df[y], 1)
        p = np.poly1d(z)
        
        return p(df['Date_ts'])

    fig, axs = plt.subplots(nrows=2, ncols=2, sharex=True)
    fig.suptitle("14-Day Trend: Testing", fontsize=16)

    # plot data
    axs[0,0].plot(df['Date'], df['New positive labs'], c='dodgerblue', linewidth=2)
    axs[0,1].plot(df['Date'], df['New negative labs'], c='dodgerblue', linewidth=2)
    axs[1,0].plot(df['Date'], df['New total labs'], c='dodgerblue', linewidth=2)
    axs[1,1].plot(df['Date'], df['%_positive'], c='dodgerblue', linewidth=2)

    # add trendline
    axs[0,0].plot(df['Date'], fit_trend('New positive labs'), c='coral', linewidth=2, linestyle='--')
    axs[0,1].plot(df['Date'], fit_trend('New negative labs'), c='coral', linewidth=2, linestyle='--')
    axs[1,0].plot(df['Date'], fit_trend('New total labs'), c='coral', linewidth=2, linestyle='--')
    axs[1,1].plot(df['Date'], fit_trend('%_positive'), c='coral', linewidth=2, linestyle='--')

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
    df = pd.read_csv('./data/clean/revised-data-clean.csv', parse_dates=['Date'])
    df = df[-14:] # last 14 days

    min_date = df['Date'].min().strftime("%#m/%d/%y")
    max_date = df['Date'].max().strftime("%#m/%d/%y")
    date_range = f'between {min_date} - {max_date}'

    def fit_trend(y):
        temp_df = df[df[y].notnull()].copy()
        z = np.polyfit(temp_df['Date_ts'], temp_df[y], 1)
        p = np.poly1d(z)
        
        return p(df['Date_ts'])

    fig, axs = plt.subplots(nrows=2, ncols=2, sharex=True)
    fig.suptitle("14-Day Trend: Hospital", fontsize=16)

    # plot data
    axs[0,0].plot(df['Date'], df['New hospital admissions'], c='dodgerblue', linewidth=2)
    axs[0,1].plot(df['Date'], df['New hospital discharges'], c='dodgerblue', linewidth=2)
    axs[1,0].plot(df['Date'], df['Hospital Deaths'], c='dodgerblue', linewidth=2)
    axs[1,1].plot(df['Date'], df['Deaths'], c='dodgerblue', linewidth=2)

    # add trendline
    axs[0,0].plot(df['Date'], fit_trend('New hospital admissions'), c='coral', linewidth=2, linestyle='--')
    axs[0,1].plot(df['Date'], fit_trend('New hospital discharges'), c='coral', linewidth=2, linestyle='--')
    axs[1,0].plot(df['Date'], fit_trend('Hospital Deaths'), c='coral', linewidth=2, linestyle='--')
    axs[1,1].plot(df['Date'], fit_trend('Deaths'), c='coral', linewidth=2, linestyle='--')

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
    df = pd.read_csv('./data/clean/revised-data-clean.csv', parse_dates=['Date'])

    min_date = df['Date'].min().strftime("%#m/%d/%y")
    max_date = df['Date'].max().strftime("%#m/%d/%y")
    date_range = f'between {min_date} - {max_date}'

    fig, axs = plt.subplots(nrows=2, ncols=2, sharex=True)
    fig.suptitle("7-Day Moving Avg: Testing", fontsize=16)

    # plot data
    axs[0,0].plot(df['Date'], df['New positive labs'].rolling(7).mean(), c='dodgerblue', linewidth=2)
    axs[0,1].plot(df['Date'], df['New negative labs'].rolling(7).mean(), c='dodgerblue', linewidth=2)
    axs[1,0].plot(df['Date'], df['New total labs'].rolling(7).mean(), c='dodgerblue', linewidth=2)
    axs[1,1].plot(df['Date'], df['%_positive'].rolling(7).mean(), c='dodgerblue', linewidth=2)

    axs[0,0].set_title('New positive labs')
    axs[0,1].set_title('New negative labs')
    axs[1,0].set_title('New total labs')
    axs[1,1].set_title('% new labs - positive')

    axs[1,0].xaxis.set_major_formatter(date_format)
    axs[1,1].xaxis.set_major_formatter(date_format)

    fig.tight_layout(rect=[0, 0.05, 1, 0.90])
    fig.set_size_inches(9, 7, forward=True)
    fig.text(x=.5, y=0.92, s=date_range, fontsize=10, ha='center')
    fig.text(x=0.97, y=0.03, s=footer, fontsize=10, ha='right')

    plt.savefig('./figures/testing_7_day_ma.png', dpi=150)

def hospital_ma_plot():
    df = pd.read_csv('./data/clean/revised-data-clean.csv', parse_dates=['Date'])

    min_date = df['Date'].min().strftime("%#m/%d/%y")
    max_date = df['Date'].max().strftime("%#m/%d/%y")
    date_range = f'between {min_date} - {max_date}'

    fig, axs = plt.subplots(nrows=2, ncols=2, sharex=True)
    fig.suptitle("7-Day Moving Avg: Hospital", fontsize=16)

    # plot data
    axs[0,0].plot(df['Date'], df['New hospital admissions'].rolling(7).mean(), c='dodgerblue', linewidth=2)
    axs[0,1].plot(df['Date'], df['New hospital discharges'].rolling(7).mean(), c='dodgerblue', linewidth=2)
    axs[1,0].plot(df['Date'], df['Hospital Deaths'].rolling(7).mean(), c='dodgerblue', linewidth=2)
    axs[1,1].plot(df['Date'], df['Deaths'].rolling(7).mean(), c='dodgerblue', linewidth=2)

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

    g = sns.FacetGrid(df, col="city_town", col_wrap=5, height=5)
    g = g.map(plt.plot, "date", "rate_per_10k", marker=",")
    g.axes[0].xaxis.set_major_formatter(date_format)
    
    g.savefig("./figures/cities_rate.png", dpi=150)