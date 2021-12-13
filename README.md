### Warning: No Longer Updated 

The constant changing of data features from the state lead to this project eating up too much time to keep updated daily.

The code and data will remain for anyone interested in the full daily dump of numbers in RI up to 9/26/2021.

# Rhode Island COVID-19 Daily Updates

The goal of this project is to collect the daily data from [RIDOH](https://health.ri.gov/data/covid-19/) on COVID-19 cases within Rhode Island. The raw data will be saved then cleaned to get daily changes and uploaded to google sheets to automate a Tableau graph. Lastly the change from the previous day & daily totals will be tweeted out automatically by a twitter bot [@RI_COVID19](https://twitter.com/RI_COVID19/).

## Web App Dashboard

Created a dashboard to provide information about the status of COVID-19 within Rhode Island. All of the data comes from the google sheet provided & updated by the Rhode Island Department of Health and Federal Agencies CMS and CDC. The goal of this dashboard is to provide a fast loading, mobile friendly option to people wanting a daily digest of COVID-19 information. It contains charts, tables and trackers for schools, nursing homes, vaccinations, deaths, testing and hospitalizations. The website can be found at [ivizri.com/covid/](https://ivizri.com/covid/).

## Prerequisites

You must have **Python 3** installed.  You can download it
[here](https://www.python.org/downloads/).  

To automate the sending of tweets you will need to apply for a [Twitter Developer](https://developer.twitter.com/en) account.  
This will be the account name sending the tweets, and edit the config with your twitter authentication info.

Lastly to automate the uploading to google sheets you will need to create a [google service account](https://pygsheets.readthedocs.io/en/stable/authorization.html#service-account).  
Then edit the config with the saved location of your service file.

## Usage

Code is run from the command line by simply typing `python main.py`.

The code will wait till 12:05 5 mins after RIDOH reports the numbers, then checks every 15 minutes to see if the google spreadsheet has been updated. Once an update is found the program will again pause for 2 minutes incase the file was currently being updated.

## Data Features

**Caution** race demographics contains missing info (unknown, pending, refused).

**Daily Totals:**  
\- positive cases  
\- negative cases  
\- number hospitalized  
\- related fatalities  
\- number in intensive care  

**Demographics:**  
\- gender  
\- age bin  
\- race  

**City/Town Totals:**  
\- city/town  
\- positive cases

**Zip Code Totals:**  
\- zip code  
\- positive cases  

**Nursing Home Totals:**  
\- facility name  
\- high/low range cases  
\- high/low range fatalities  
\- facility type

## Visualizations

Current dashboards created using the cleaned datasets.
- [daily update comparison](https://ivizri.com/posts/2020/03/rhode-island-covid-19-cases/)
- [timelines tracking key information](https://ivizri.com/posts/2020/03/timeline-of-covid-19-cases/)
- [map of case rate by city/town](https://ivizri.com/posts/2020/03/covid-19-cases-by-location/)
- [ri nursing home cases/deaths](https://ivizri.com/posts/2020/05/covid19-ri-nursing-homes/)

Current plots created using the cleaned datasets.
- [7-day moving avg: hospitals](https://raw.githubusercontent.com/SmirkyGraphs/ri-covid19-updates/master/figures/hospital_7_day_ma.png)
- [7-day moving avg: testing](https://raw.githubusercontent.com/SmirkyGraphs/ri-covid19-updates/master/figures/testing_7_day_ma.png)
- [14-day trend: hospitals](https://raw.githubusercontent.com/SmirkyGraphs/ri-covid19-updates/master/figures/hospital_14_day_trend.png)
- [14-day trend: testing](https://raw.githubusercontent.com/SmirkyGraphs/ri-covid19-updates/master/figures/testing_14_day_trend.png)
- [cities cases rate by 10k](https://raw.githubusercontent.com/SmirkyGraphs/ri-covid19-updates/master/figures/cities_rate.png)

## References

- Spatial Boundaries: [RIGIS](http://www.rigis.org/)
- Daily Numbers: [RIDOH](https://docs.google.com/spreadsheets/d/1n-zMS9Al94CPj_Tc3K7Adin-tN9x1RSjjx2UzJ4SV7Q/edit#gid=0)
- City/Town Breakdown: [RIDOH](https://docs.google.com/spreadsheets/d/1n-zMS9Al94CPj_Tc3K7Adin-tN9x1RSjjx2UzJ4SV7Q/edit#gid=1679077334)
- City/Town Population: [Census 2017 ACS 5-Year Estimates](https://factfinder.census.gov/faces/tableservices/jsf/pages/productview.xhtml)
- Zip Population: [Census 2010 Decennial Population](https://data.census.gov/cedsci/)
- Nursing Homes: [CMS.gov](https://data.cms.gov/Special-Programs-Initiatives-COVID-19-Nursing-Home/COVID-19-Nursing-Home-Dataset/s2uc-8wxp)
- Vaccination: [CDC.gov](https://covid.cdc.gov/covid-data-tracker/#vaccinations)
