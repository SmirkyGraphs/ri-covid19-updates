import time
import numpy as np
import pandas as pd

import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.patches as mpatches
import matplotlib.lines as mlines
import matplotlib.ticker as tick

plt.style.use('seaborn')
plt.style.use('fivethirtyeight')
date_format = mdates.DateFormatter('%#m/%#d')
pd.plotting.register_matplotlib_converters()

footer = f'made by: SmirkyGraphs  |  site: ivizri.com  |  source: RIDOH  |  updated: {time.strftime("%#m/%d/%Y")}'

def fit_trend(df, y):
    temp_df = df[df[y].notnull()].copy()
    z = np.polyfit(temp_df['date_ts'], temp_df[y], 1)
    p = np.poly1d(z)
    
    return p(df['date_ts'])

def testing_trend_plot(df):
    print('\n[status] creating testing plots')
    df = df[-14:] # last 14 days

    min_date = df['date'].min().strftime("%#m/%d/%y")
    max_date = df['date'].max().strftime("%#m/%d/%y")
    date_range = f'between {min_date} - {max_date}'

    fig, axs = plt.subplots(nrows=2, ncols=2, sharex=True)
    fig.suptitle("14-Day Trend: Testing", fontsize=16)
    
    # plot data
    axs[0,0].plot(df['date_ts'].to_numpy(), df['new positive labs'].to_numpy(), c='dodgerblue', linewidth=2)
    axs[0,1].plot(df['date_ts'].to_numpy(), df['new negative labs'].to_numpy(), c='dodgerblue', linewidth=2)
    axs[1,0].plot(df['date_ts'].to_numpy(), df['new total labs'].to_numpy(), c='dodgerblue', linewidth=2)
    axs[1,1].plot(df['date_ts'].to_numpy(), df['%_positive_labs'].to_numpy(), c='dodgerblue', linewidth=2)

    # add trendline
    axs[0,0].plot(df['date_ts'].to_numpy(), fit_trend(df, 'new positive labs'), c='coral', linewidth=2, linestyle='--')
    axs[0,1].plot(df['date_ts'].to_numpy(), fit_trend(df, 'new negative labs'), c='coral', linewidth=2, linestyle='--')
    axs[1,0].plot(df['date_ts'].to_numpy(), fit_trend(df, 'new total labs'), c='coral', linewidth=2, linestyle='--')
    axs[1,1].plot(df['date_ts'].to_numpy(), fit_trend(df, '%_positive_labs'), c='coral', linewidth=2, linestyle='--')

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

def hospital_trend_plot(df):
    print('[status] creating hospital plots')
    df = df[-14:] # last 14 days

    min_date = df['date'].min().strftime("%#m/%d/%y")
    max_date = df['date'].max().strftime("%#m/%d/%y")
    date_range = f'between {min_date} - {max_date}'

    fig, axs = plt.subplots(nrows=2, ncols=2, sharex=True)
    fig.suptitle("14-Day Trend: Hospital", fontsize=16)

    # plot data
    axs[0,0].plot(df['date_ts'].to_numpy(), df['new hospital admissions'].to_numpy(), c='dodgerblue', linewidth=2)
    axs[0,1].plot(df['date_ts'].to_numpy(), df['new hospital discharges'].to_numpy(), c='dodgerblue', linewidth=2)
    axs[1,0].plot(df['date_ts'].to_numpy(), df['hospital deaths'].to_numpy(), c='dodgerblue', linewidth=2)
    axs[1,1].plot(df['date_ts'].to_numpy(), df['deaths'].to_numpy(), c='dodgerblue', linewidth=2)

    # add trendline
    axs[0,0].plot(df['date_ts'].to_numpy(), fit_trend(df, 'new hospital admissions'), c='coral', linewidth=2, linestyle='--')
    axs[0,1].plot(df['date_ts'].to_numpy(), fit_trend(df, 'new hospital discharges'), c='coral', linewidth=2, linestyle='--')
    axs[1,0].plot(df['date_ts'].to_numpy(), fit_trend(df, 'hospital deaths'), c='coral', linewidth=2, linestyle='--')
    axs[1,1].plot(df['date_ts'].to_numpy(), fit_trend(df, 'deaths'), c='coral', linewidth=2, linestyle='--')

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

def testing_combo_ma_plot(df):
    print('[status] creating testing ma combo plots')

    min_date = df['date'].min().strftime("%#m/%d/%y")
    max_date = df['date'].max().strftime("%#m/%d/%y")
    date_range = f'between {min_date} - {max_date}'

    fig, axs = plt.subplots(nrows=2, ncols=2, sharex=True)
    fig.suptitle("7-Day Moving Avg: Testing", fontsize=16)

    # plot data
    axs[0,0].plot(df['date_ts'].to_numpy(), df['new positive labs'].rolling(7).mean().to_numpy(), c='dodgerblue', linewidth=2)
    axs[0,1].plot(df['date_ts'].to_numpy(), df['new negative labs'].rolling(7).mean().to_numpy(), c='dodgerblue', linewidth=2)
    axs[1,0].plot(df['date_ts'].to_numpy(), df['new total labs'].rolling(7).mean().to_numpy(), c='dodgerblue', linewidth=2)
    axs[1,1].plot(df['date_ts'].to_numpy(), df['%_positive_labs'].rolling(7).mean().to_numpy(), c='dodgerblue', linewidth=2)

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

def hospital_combo_ma_plot(df):
    print('[status] creating hospital ma combo plots')

    min_date = df['date'].min().strftime("%#m/%d/%y")
    max_date = df['date'].max().strftime("%#m/%d/%y")
    date_range = f'between {min_date} - {max_date}'

    fig, axs = plt.subplots(nrows=2, ncols=2, sharex=True)
    fig.suptitle("7-Day Moving Avg: Hospital", fontsize=16)

    # plot data
    axs[0,0].plot(df['date_ts'].to_numpy(), df['new hospital admissions'].rolling(7).mean().to_numpy(), c='dodgerblue', linewidth=2)
    axs[0,1].plot(df['date_ts'].to_numpy(), df['new hospital discharges'].rolling(7).mean().to_numpy(), c='dodgerblue', linewidth=2)
    axs[1,0].plot(df['date_ts'].to_numpy(), df['hospital deaths'].rolling(7).mean().to_numpy(), c='dodgerblue', linewidth=2)
    axs[1,1].plot(df['date_ts'].to_numpy(), df['deaths'].rolling(7).mean().to_numpy(), c='dodgerblue', linewidth=2)

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

def city_rate_plot(geo_df):
    print('[status] creating cities/towns rate graphs')
    df = geo_df.sort_values(by=['city_town', 'date'])

    g = sns.FacetGrid(df, col="city_town", col_wrap=7, height=3)
    g = g.map(plt.plot, "date", "rate_per_10k", marker=",", linewidth=2.5)
    g.axes[0].xaxis.set_major_formatter(date_format)
    g.savefig("./figures/cities_rate.png", dpi=150)

def first_vs_current(df):
    print('[status] creating first vs. current')
    lowest = df.groupby('date_ts')['deaths'].min().reset_index().rename(columns={'deaths': 'lowest_deaths'})
    current = df[df['date_scraped'] == df['date_scraped'].max()][['date_ts', 'deaths']].rename(columns={'deaths': 'current_deaths'})
    df = current.merge(lowest)

    fig, axs = plt.subplots(nrows=1, ncols=1, sharex=True)
    fig.suptitle("COVID-19 Deaths, First Reported vs. Current", fontsize=16)
    sub_head = '7-day moving average showing the change between first reported & current number'

    # plot data
    axs.plot(df['date_ts'].to_numpy(), df['lowest_deaths'].rolling(7).mean().to_numpy(), c='dodgerblue', linewidth=2)
    axs.plot(df['date_ts'].to_numpy(), df['current_deaths'].rolling(7).mean().to_numpy(), c='coral', linewidth=2)
    axs.xaxis.set_major_formatter(date_format)

    fig.tight_layout(rect=[0, 0.05, 1, 0.90])
    fig.set_size_inches(15, 7, forward=True)
    fig.text(x=.5, y=0.92, s=sub_head, fontsize=10, ha='center')
    fig.text(x=0.97, y=0.03, s=footer, fontsize=10, ha='right')

    patch = mpatches.Patch(facecolor='dodgerblue', label='trend from first reported')
    fig.legend(handles=[patch], loc='upper left', bbox_to_anchor=[0.78, 1], fontsize=10)   

    patch = mpatches.Patch(facecolor='coral', label='trend from current data')
    fig.legend(handles=[patch], loc='upper left', bbox_to_anchor=[0.78, 0.97], fontsize=10) 

    plt.savefig('./figures/first_vs_current.png', dpi=150)

def first_vs_current_bar(df):
    print('[status] creating first vs. current (bar)')
    lowest = df.groupby('date_ts')['deaths'].min().reset_index().rename(columns={'deaths': 'lowest_deaths'})
    current = df[df['date_scraped'] == df['date_scraped'].max()][['date_ts', 'deaths']].rename(columns={'deaths': 'current_deaths'})
    df = current.merge(lowest)

    fig, axs = plt.subplots(nrows=1, ncols=1, sharex=True)
    fig.suptitle("COVID-19 Deaths, First Reported vs. Current", fontsize=16)
    sub_head = 'stacked bargraph showing change from first reported vs. current values'

    # plot data
    axs.bar(df['date_ts'].to_numpy(), df['lowest_deaths'], color='dodgerblue')
    axs.bar(df['date_ts'].to_numpy(), (df['current_deaths']-df['lowest_deaths']), color='coral', bottom=df['lowest_deaths'])
    axs.xaxis.set_major_formatter(date_format)

    fig.tight_layout(rect=[0, 0.05, 1, 0.90])
    fig.set_size_inches(15, 7, forward=True)
    fig.text(x=.5, y=0.92, s=sub_head, fontsize=10, ha='center')
    fig.text(x=0.97, y=0.03, s=footer, fontsize=10, ha='right')

    patch = mpatches.Patch(facecolor='dodgerblue', label='first reported deaths for date')
    fig.legend(handles=[patch], loc='upper left', bbox_to_anchor=[0.78, 1], fontsize=10)   

    patch = mpatches.Patch(facecolor='coral', label='updated new deaths')
    fig.legend(handles=[patch], loc='upper left', bbox_to_anchor=[0.78, 0.97], fontsize=10) 
    plt.savefig('./figures/first_vs_current_bar.png', dpi=150)

def icu_ma_daily(df):
    print('[status] creating hospital: icu graph')
    fig, axs = plt.subplots(nrows=1, ncols=1, sharex=True)
    fig.suptitle("Hospital: ICU", fontsize=16)
    sub_head = 'daily number of people in an icu bed'

    # plot data
    axs.bar(df['date_ts'].to_numpy(), df['icu'].to_numpy(), color='dodgerblue')
    axs.plot(df['date_ts'].to_numpy(), df['icu'].rolling(7).mean().to_numpy(), c='coral', linewidth=2)
    axs.xaxis.set_major_formatter(date_format)

    fig.tight_layout(rect=[0, 0.05, 1, 0.90])
    fig.set_size_inches(15, 7, forward=True)
    fig.text(x=.5, y=0.92, s=sub_head, fontsize=10, ha='center')
    fig.text(x=0.97, y=0.03, s=footer, fontsize=10, ha='right')

    patch = mpatches.Patch(facecolor='dodgerblue', label='daily total in icu')
    fig.legend(handles=[patch], loc='upper left', bbox_to_anchor=[0.78, 1], fontsize=10)   

    patch = mpatches.Patch(facecolor='coral', label='7-day moving average')
    fig.legend(handles=[patch], loc='upper left', bbox_to_anchor=[0.78, 0.97], fontsize=10) 
    plt.savefig('./figures/hospital_icu_daily_ma.png', dpi=150)

def vent_ma_daily(df):
    print('[status] creating hospital: vent graph')
    fig, axs = plt.subplots(nrows=1, ncols=1, sharex=True)
    fig.suptitle("Hospital: Ventilator", fontsize=16)
    sub_head = 'daily number of people on a vent'

    # plot data
    axs.bar(df['date_ts'].to_numpy(), df['vented'].to_numpy(), color='dodgerblue')
    axs.plot(df['date_ts'].to_numpy(), df['vented'].rolling(7).mean().to_numpy(), c='coral', linewidth=2)
    axs.xaxis.set_major_formatter(date_format)

    fig.tight_layout(rect=[0, 0.05, 1, 0.90])
    fig.set_size_inches(15, 7, forward=True)
    fig.text(x=.5, y=0.92, s=sub_head, fontsize=10, ha='center')
    fig.text(x=0.97, y=0.03, s=footer, fontsize=10, ha='right')

    patch = mpatches.Patch(facecolor='dodgerblue', label='daily total on vent')
    fig.legend(handles=[patch], loc='upper left', bbox_to_anchor=[0.78, 1], fontsize=10)   

    patch = mpatches.Patch(facecolor='coral', label='7-day moving average')
    fig.legend(handles=[patch], loc='upper left', bbox_to_anchor=[0.78, 0.97], fontsize=10) 
    plt.savefig('./figures/hospital_vent_daily_ma.png', dpi=150)

def hospitalized_ma_daily(df):
    print('[status] creating hospital: admissions graph')
    fig, axs = plt.subplots(nrows=1, ncols=1, sharex=True)
    fig.suptitle("Hospital: Admissions", fontsize=16)
    sub_head = 'daily number of new hospital admissions'

    # plot data
    axs.bar(df['date_ts'].to_numpy(), df['new hospital admissions'].to_numpy(), color='dodgerblue')
    axs.plot(df['date_ts'].to_numpy(), df['new hospital admissions'].rolling(7).mean().to_numpy(), c='coral', linewidth=2)
    axs.xaxis.set_major_formatter(date_format)

    fig.tight_layout(rect=[0, 0.05, 1, 0.90])
    fig.set_size_inches(15, 7, forward=True)
    fig.text(x=.5, y=0.92, s=sub_head, fontsize=10, ha='center')
    fig.text(x=0.97, y=0.03, s=footer, fontsize=10, ha='right')

    patch = mpatches.Patch(facecolor='dodgerblue', label='daily admissions')
    fig.legend(handles=[patch], loc='upper left', bbox_to_anchor=[0.78, 1], fontsize=10)   

    patch = mpatches.Patch(facecolor='coral', label='7-day moving average')
    fig.legend(handles=[patch], loc='upper left', bbox_to_anchor=[0.78, 0.97], fontsize=10)   
    plt.savefig('./figures/hospital_admission_daily_ma.png', dpi=150)

def new_ppl_tested(df):
    print('[status] creating testing: new people tested')
    fig, axs1 = plt.subplots(nrows=1, ncols=1, sharex=True)
    fig.suptitle("Testing: New People Tested", fontsize=16)
    sub_head = 'daily number of first tests (only counts first test per person)'

    # plot data
    axs1.bar(df['date_ts'].to_numpy(), df['new people positive'], color='coral')
    axs1.bar(df['date_ts'].to_numpy(), df['new people negative'], color='dodgerblue', bottom=df['new people positive'])
    axs1.xaxis.set_major_formatter(date_format)

    fig.tight_layout(rect=[0, 0.05, 1, 0.90])
    fig.set_size_inches(15, 7, forward=True)
    fig.text(x=.5, y=0.92, s=sub_head, fontsize=10, ha='center')
    fig.text(x=0.97, y=0.03, s=footer, fontsize=10, ha='right')

    patch = mpatches.Patch(facecolor='dodgerblue', label='new people tested negative')
    fig.legend(handles=[patch], loc='upper left', bbox_to_anchor=[0.78, 1], fontsize=10)   

    patch = mpatches.Patch(facecolor='coral', label='new people tested positive')
    fig.legend(handles=[patch], loc='upper left', bbox_to_anchor=[0.78, 0.97], fontsize=10)  
    plt.savefig('./figures/test_new_people_tested_stacked.png', dpi=150)

def labs_tested(df):
    print('[status] creating testing: new labs tested')
    fig, axs1 = plt.subplots(nrows=1, ncols=1, sharex=True)
    fig.suptitle("Testing: Total Labs Tested", fontsize=16)
    sub_head = 'daily number of labs tested (includes people tested mutliple times)'

    # plot data
    axs1.bar(df['date_ts'].to_numpy(), df['new positive labs'], color='coral')
    axs1.bar(df['date_ts'].to_numpy(), df['new negative labs'], color='dodgerblue', bottom=df['new positive labs'])
    axs1.xaxis.set_major_formatter(date_format)

    fig.tight_layout(rect=[0, 0.05, 1, 0.90])
    fig.set_size_inches(15, 7, forward=True)
    fig.text(x=.5, y=0.92, s=sub_head, fontsize=10, ha='center')
    fig.text(x=0.97, y=0.03, s=footer, fontsize=10, ha='right')

    patch = mpatches.Patch(facecolor='dodgerblue', label='daily negative labs')
    fig.legend(handles=[patch], loc='upper left', bbox_to_anchor=[0.78, 1], fontsize=10)   

    patch = mpatches.Patch(facecolor='coral', label='daily positive labs')
    fig.legend(handles=[patch], loc='upper left', bbox_to_anchor=[0.78, 0.97], fontsize=10)  
    plt.savefig('./figures/test_labs_tested_stacked.png', dpi=150)

def new_ppl_percent_pos(df):
    print('[status] creating testing: new people % pos')
    fig, axs = plt.subplots(nrows=1, ncols=1, sharex=True)
    fig.suptitle("Testing: New People Percent Positive", fontsize=16)
    sub_head = 'daily percent positive of people being tested for the first time'

    colors = ['dodgerblue' if (x < 0.05) else 'coral' for x in df['%_new_people_positive']]

    # plot data
    axs.bar(df['date_ts'].to_numpy(), df['%_new_people_positive'], color=colors)
    axs.xaxis.set_major_formatter(date_format)

    # 5% static line
    plt.axhline(y=0.05, color='#333333', linestyle='dashed', linewidth=1)

    fig.tight_layout(rect=[0, 0.05, 1, 0.90])
    fig.set_size_inches(15, 7, forward=True)
    fig.text(x=.5, y=0.92, s=sub_head, fontsize=10, ha='center')
    fig.text(x=0.97, y=0.03, s=footer, fontsize=10, ha='right')
    plt.gca().yaxis.set_major_formatter(tick.PercentFormatter(1))

    patch = mpatches.Patch(facecolor='dodgerblue', label='under 5% daily positive')
    fig.legend(handles=[patch], loc='upper left', bbox_to_anchor=[0.78, 1], fontsize=10)   

    patch = mpatches.Patch(facecolor='coral', label='over 5% daily positive')
    fig.legend(handles=[patch], loc='upper left', bbox_to_anchor=[0.78, 0.97], fontsize=10)

    patch = mlines.Line2D([], [], linewidth=2, linestyle="dashed", color='#333333', label='5% daily positive tests')
    fig.legend(handles=[patch], loc='upper left', bbox_to_anchor=[0.78, 0.94], fontsize=10) 
    plt.savefig('./figures/test_new_percent_pos.png', dpi=150)

def total_labs_percent_pos(df):
    print('[status] creating testing: new labs % pos')
    fig, axs = plt.subplots(nrows=1, ncols=1, sharex=True)
    fig.suptitle("Testing: Total Labs Percent Positive", fontsize=16)
    sub_head = 'daily percent positive of all labs tested'

    colors = ['dodgerblue' if (x < 0.05) else 'coral' for x in df['%_positive_labs']]

    # plot data
    axs.bar(df['date_ts'].to_numpy(), df['%_positive_labs'], color=colors)
    axs.xaxis.set_major_formatter(date_format)

    # 5% static line
    plt.axhline(y=0.05, color='#333333', linestyle='dashed', linewidth=1)

    fig.tight_layout(rect=[0, 0.05, 1, 0.90])
    fig.set_size_inches(15, 7, forward=True)
    fig.text(x=.5, y=0.92, s=sub_head, fontsize=10, ha='center')
    fig.text(x=0.97, y=0.03, s=footer, fontsize=10, ha='right')
    plt.gca().yaxis.set_major_formatter(tick.PercentFormatter(1))

    patch = mpatches.Patch(facecolor='dodgerblue', label='under 5% daily positive')
    fig.legend(handles=[patch], loc='upper left', bbox_to_anchor=[0.78, 1], fontsize=10)   

    patch = mpatches.Patch(facecolor='coral', label='over 5% daily positive')
    fig.legend(handles=[patch], loc='upper left', bbox_to_anchor=[0.78, 0.97], fontsize=10)

    patch = mlines.Line2D([], [], linewidth=2, linestyle="dashed", color='#333333', label='5% daily positive tests')
    fig.legend(handles=[patch], loc='upper left', bbox_to_anchor=[0.78, 0.94], fontsize=10) 
    plt.savefig('./figures/test_labs_percent_pos.png', dpi=150)

def daily_positive(df):
    print('[status] creating testing: daily positive')
    fig, axs = plt.subplots(nrows=1, ncols=1, sharex=True)
    fig.suptitle("Testing: Daily Positive Cases", fontsize=16)
    sub_head = 'daily number of positive labs'

    # plot data
    axs.bar(df['date_ts'].to_numpy(), df['new positive labs'].to_numpy(), color='dodgerblue')
    axs.plot(df['date_ts'].to_numpy(), df['new positive labs'].rolling(7).mean().to_numpy(), c='coral', linewidth=2)
    axs.xaxis.set_major_formatter(date_format)

    fig.tight_layout(rect=[0, 0.05, 1, 0.90])
    fig.set_size_inches(15, 7, forward=True)
    fig.text(x=.5, y=0.92, s=sub_head, fontsize=10, ha='center')
    fig.text(x=0.97, y=0.03, s=footer, fontsize=10, ha='right')

    patch = mpatches.Patch(facecolor='dodgerblue', label='daily positive cases')
    fig.legend(handles=[patch], loc='upper left', bbox_to_anchor=[0.78, 1], fontsize=10)   

    patch = mpatches.Patch(facecolor='coral', label='7-day moving average')
    fig.legend(handles=[patch], loc='upper left', bbox_to_anchor=[0.78, 0.97], fontsize=10) 
    plt.savefig('./figures/test_daily_positive.png', dpi=150)

def daily_ppl_positive(df):
    print('[status] creating testing: daily people positive')
    fig, axs = plt.subplots(nrows=1, ncols=1, sharex=True)
    fig.suptitle("Testing: People Positive", fontsize=16)
    sub_head = 'daily number of new people who tested positive'

    # plot data
    axs.bar(df['date_ts'].to_numpy(), df['new people positive'].to_numpy(), color='dodgerblue')
    axs.plot(df['date_ts'].to_numpy(), df['new people positive'].rolling(7).mean().to_numpy(), c='coral', linewidth=2)
    axs.xaxis.set_major_formatter(date_format)

    fig.tight_layout(rect=[0, 0.05, 1, 0.90])
    fig.set_size_inches(15, 7, forward=True)
    fig.text(x=.5, y=0.92, s=sub_head, fontsize=10, ha='center')
    fig.text(x=0.97, y=0.03, s=footer, fontsize=10, ha='right')

    patch = mpatches.Patch(facecolor='dodgerblue', label='daily positive people')
    fig.legend(handles=[patch], loc='upper left', bbox_to_anchor=[0.78, 1], fontsize=10)   

    patch = mpatches.Patch(facecolor='coral', label='7-day moving average')
    fig.legend(handles=[patch], loc='upper left', bbox_to_anchor=[0.78, 0.97], fontsize=10) 
    plt.savefig('./figures/test_daily_ppl_positive.png', dpi=150)

def daily_deaths(df):
    print('[status] creating daily deaths')
    fig, axs = plt.subplots(nrows=1, ncols=1, sharex=True)
    fig.suptitle("COVID-19 Daily Deaths", fontsize=16)
    sub_head = 'daily number of deaths related to covid-19'

    # plot data
    axs.bar(df['date_ts'].to_numpy(), df['deaths'].to_numpy(), color='dodgerblue')
    axs.plot(df['date_ts'].to_numpy(), df['deaths'].rolling(7).mean().to_numpy(), c='coral', linewidth=2)
    axs.xaxis.set_major_formatter(date_format)

    fig.tight_layout(rect=[0, 0.05, 1, 0.90])
    fig.set_size_inches(15, 7, forward=True)
    fig.text(x=.5, y=0.92, s=sub_head, fontsize=10, ha='center')
    fig.text(x=0.97, y=0.03, s=footer, fontsize=10, ha='right')

    patch = mpatches.Patch(facecolor='dodgerblue', label='daily deaths')
    fig.legend(handles=[patch], loc='upper left', bbox_to_anchor=[0.78, 1], fontsize=10)   

    patch = mpatches.Patch(facecolor='coral', label='7-day moving average')
    fig.legend(handles=[patch], loc='upper left', bbox_to_anchor=[0.78, 0.97], fontsize=10) 
    plt.savefig('./figures/daily_deaths.png', dpi=150)

def percent_tests_new(df):
    print('[status] creating % of tests new people')
    fig, axs = plt.subplots(nrows=1, ncols=1, sharex=True)
    fig.suptitle("Testing: Daily % First-Time Tested", fontsize=16)
    sub_head = 'percent of daily labs who are people being tested for the first time'

    # plot data
    axs.bar(df['date_ts'].to_numpy(), df['%_new_labs_new_people'].to_numpy(), color='dodgerblue')
    axs.plot(df['date_ts'].to_numpy(), df['%_new_labs_new_people'].rolling(7).mean().to_numpy(), c='coral', linewidth=2)
    axs.xaxis.set_major_formatter(date_format)
    plt.gca().yaxis.set_major_formatter(tick.PercentFormatter(1))

    fig.tight_layout(rect=[0, 0.05, 1, 0.90])
    fig.set_size_inches(15, 7, forward=True)
    fig.text(x=.5, y=0.92, s=sub_head, fontsize=10, ha='center')
    fig.text(x=0.97, y=0.03, s=footer, fontsize=10, ha='right')

    patch = mpatches.Patch(facecolor='dodgerblue', label='daily % first-time')
    fig.legend(handles=[patch], loc='upper left', bbox_to_anchor=[0.78, 1], fontsize=10)   

    patch = mpatches.Patch(facecolor='coral', label='7-day moving average')
    fig.legend(handles=[patch], loc='upper left', bbox_to_anchor=[0.78, 0.97], fontsize=10) 
    plt.savefig('./figures/percent_first_time_tested.png', dpi=150)

def todays_new_deaths(df):
    print('[status] creating newly reported deaths')
    df2 = pd.read_csv('./data/reports/full_death_change.csv', parse_dates=['date', 'date_scraped'])
    df2 = df2[df2['date_scraped']==df2['date_scraped'].max()].rename(columns={'deaths': 'new_deaths'})
    
    df = df.merge(df2, how='left', on=['date', 'date_scraped']).fillna(0)
    df['old_deaths'] = df['deaths'] - df['new_deaths']
    
    fig, axs = plt.subplots(nrows=1, ncols=1, sharex=True)
    fig.suptitle("Daily New Reported Deaths", fontsize=16)
    sub_head = "shows the exact dates of today's newly reported deaths"

    # plot data
    axs.bar(df['date_ts'].to_numpy(), df['old_deaths'], color='dodgerblue')
    axs.bar(df['date_ts'].to_numpy(), df['new_deaths'], color='coral', bottom=df['old_deaths'])
    axs.xaxis.set_major_formatter(date_format)

    fig.tight_layout(rect=[0, 0.05, 1, 0.90])
    fig.set_size_inches(15, 7, forward=True)
    fig.text(x=.5, y=0.92, s=sub_head, fontsize=10, ha='center')
    fig.text(x=0.97, y=0.03, s=footer, fontsize=10, ha='right')

    patch = mpatches.Patch(facecolor='dodgerblue', label='previously reported deaths')
    fig.legend(handles=[patch], loc='upper left', bbox_to_anchor=[0.78, 1], fontsize=10)   

    patch = mpatches.Patch(facecolor='coral', label='new deaths reported today')
    fig.legend(handles=[patch], loc='upper left', bbox_to_anchor=[0.78, 0.97], fontsize=10)
    plt.savefig('./figures/new_reported_deaths.png', dpi=150)

def ridoh_vaccination_trend(df):
    print('[status] creating vaccine trend')
    fig, axs = plt.subplots(nrows=1, ncols=1, sharex=True)
    fig.suptitle("RIDOH Vaccination Trend", fontsize=16)
    sub_head = 'daily number of first and second vaccine doses administered'

    # plot data
    axs.bar(df['date_ts'].to_numpy(), df['new first vaccine doses admin (includes single-dose vaccines)'], color='dodgerblue')
    axs.bar(df['date_ts'].to_numpy(), df['new second vaccine doses admin (only applicable for two-dose vaccines)'], color='coral', 
            bottom=df['new first vaccine doses admin (includes single-dose vaccines)'])
    axs.plot(df['date_ts'].to_numpy(), df['new vaccine doses admin'].rolling(7).mean().to_numpy(), linewidth=2, c='#333333', linestyle='dashed')
    axs.xaxis.set_major_formatter(date_format)

    fig.tight_layout(rect=[0, 0.05, 1, 0.90])
    fig.set_size_inches(15, 7, forward=True)
    fig.text(x=.5, y=0.92, s=sub_head, fontsize=10, ha='center')
    fig.text(x=0.97, y=0.03, s=footer, fontsize=10, ha='right')

    patch = mpatches.Patch(facecolor='dodgerblue', label='first dose administered')
    fig.legend(handles=[patch], loc='upper left', bbox_to_anchor=[0.78, 1], fontsize=10)   

    patch = mpatches.Patch(facecolor='coral', label='second dose administered')
    fig.legend(handles=[patch], loc='upper left', bbox_to_anchor=[0.78, 0.97], fontsize=10)

    patch = mlines.Line2D([], [], linewidth=2, linestyle="dashed", color='#333333', label='7-day moving average')
    fig.legend(handles=[patch], loc='upper left', bbox_to_anchor=[0.78, 0.94], fontsize=10) 
    plt.savefig('./figures/ridoh_vaccine_trend.png', dpi=150)

def vaccine_rank_states(df, method, title, save_file, pct=False):
    df = df.sort_values(by=method, ascending=False).reset_index(drop=True)
    # get ri rank among new england states 
    states = ['CT', 'RI', 'MA', 'NH', 'ME', 'VT']
    ne_rnk = [df.loc[df['Location']==st].index[0] + 1 for st in states]
    _, states = zip(*sorted(zip(ne_rnk, states)))
    ne_rank = states.index('RI') + 1
    
    # highlight ri and return overall state rank
    c = ['coral' if (x == 'RI') else 'dodgerblue' for x in df['Location']]
    st_rank = c.index('coral') + 1

    value = df[df['Location']=='RI'][method].iloc[0]
    if value > 1:
        value = f"{int(value):,}"
    else:
        value = f"{value:.1%}"

    # make plot
    fig, axs = plt.subplots(nrows=1, ncols=1, sharex=True)
    fig.suptitle(title, fontsize=16)
    rects = axs.bar(df['Location'], df[method], color=c)
    
    if pct != False:
        plt.gca().yaxis.set_major_formatter(tick.PercentFormatter(1))

    sub_title = f"RI ranked {st_rank} of all states  |  RI ranked {ne_rank} of New England states  |  RI exact number: {value}"
    _footer = footer.replace('source: RIDOH', 'source: CDC')
    fig.tight_layout(rect=[0, 0.05, 1, 0.90])
    fig.set_size_inches(15, 7, forward=True)
    fig.text(x=.5, y=0.92, s=sub_title, fontsize=10, ha='center')
    fig.text(x=0.97, y=0.03, s=_footer, fontsize=10, ha='right')
    plt.savefig(f'./figures/{save_file}.png', dpi=150)

def make_plots():
    # load revised daily updated data and geographic data
    df = pd.read_csv('./data/clean/revised-data-clean.csv', parse_dates=['date', 'date_scraped'])
    geo_df = pd.read_csv('./data/clean/geo-ri-covid-19-clean.csv', parse_dates=['date'])
    recent_df = df[df['date_scraped'] == df['date_scraped'].max()]

    vaccine_id = recent_df['cumulative people partially vaccinated'].ne(0).idxmax()
    ri_vac_df = recent_df[recent_df.index > vaccine_id]

    testing_trend_plot(recent_df)
    hospital_trend_plot(recent_df)
    testing_combo_ma_plot(recent_df)
    hospital_combo_ma_plot(recent_df)
    city_rate_plot(geo_df)
    first_vs_current(df)
    first_vs_current_bar(df)
    icu_ma_daily(recent_df)
    vent_ma_daily(recent_df)
    hospitalized_ma_daily(recent_df)
    daily_ppl_positive(recent_df)
    new_ppl_tested(recent_df)
    labs_tested(recent_df)
    new_ppl_percent_pos(recent_df)
    total_labs_percent_pos(recent_df)
    daily_positive(recent_df)
    daily_deaths(recent_df)
    percent_tests_new(recent_df)
    todays_new_deaths(recent_df)
    ridoh_vaccination_trend(ri_vac_df)

    # vaccine rankings
    df = pd.read_csv('./data/clean/vaccine-vaccination_states-clean.csv', parse_dates=['date'])
    df = df[df['date'] == df['date'].max()]

    title = 'Percent of People 18+ Receiving 1 or More Doses'
    vaccine_rank_states(df, 'Administered_Dose1_Recip_18PlusPop_Pct', title, 'cdc_one_dose_pct_18', True)

    title = 'Percent of People 18+ Receiving 2 Doses'
    vaccine_rank_states(df, 'Administered_Dose2_Recip_18PlusPop_Pct', title, 'cdc_two_dose_pct_18', True)

    title = 'Percent of All People Receiving 1 or More Doses'
    vaccine_rank_states(df, 'Administered_Dose1_Recip_Pct', title, 'cdc_one_dose_pct', True)

    title = 'Percent of All People Receiving 2 Doses'
    vaccine_rank_states(df, 'Administered_Dose2_Recip_Pct', title, 'cdc_two_dose_pct', True)

    title = 'Percent of Distributed Vaccine Used'
    vaccine_rank_states(df, 'pct_doses_used_recip', title, 'cdc_vaccine_used_pct', True)

