# Rhode Island COVID-19 Daily Updates

The goal of this project is to collect the daily data from [RIDOH](https://health.ri.gov/data/covid-19/) on COVID-19 cases within Rhode Island. The raw data will be saved then cleaned to get daily changes and uploaded to google sheets to automate a Tableau graph. Lastly the change from the previous day & daily totals will be tweeted out automatically by a twitter bot [@RI_COVID19](https://twitter.com/RI_COVID19/).

## Prerequisites

You must have **Python 3** installed.  You can download it
[here](https://www.python.org/downloads/).  

To automate the sending of tweets you will need to apply for a [Twitter Developer](https://developer.twitter.com/en) account.  
This will be the account name sending the tweets, and edit the config with your twitter authentication info.

Lastly to automate the uploading to google sheets you will need to create a [google service account](https://pygsheets.readthedocs.io/en/stable/authorization.html#service-account).  
Then edit the config with the saved location of your service file.

## Usage

Code is run from the command line by simply typing `python main.py`.

The code will check every 15 minutes to see if the google spreadsheet has been updated. Once an update is found the program will again pause for 2 minutes incase the file was currently being updated.

## Data Features

**Daily Totals:**  
\- positive cases  
\- negative cases  
\- number hospitalized  
\- related fatalities  
\- number in intensive care  

**City/Town Totals:**  
\- city/town  
\- positive cases

**Nursing Home Totals:**  
\- facility name
\- high/low range cases
\- high/low range fatalities
\- facility type

## Dashboards

Current dashboards created using the cleaned datasets.
- [daily update comparison](https://ivizri.com/posts/2020/03/rhode-island-covid-19-cases/)
- [timelines tracking key information](https://ivizri.com/posts/2020/03/timeline-of-covid-19-cases/)
- [map of case rate by city/town](https://ivizri.com/posts/2020/03/covid-19-cases-by-location/)

## References

- Spatial Boundaries: [RIGIS](http://www.rigis.org/)
- Daily Numbers: [RIDOH](https://docs.google.com/spreadsheets/d/1n-zMS9Al94CPj_Tc3K7Adin-tN9x1RSjjx2UzJ4SV7Q/edit#gid=0)
- City/Town Breakdown: [RIDOH](https://docs.google.com/spreadsheets/d/1n-zMS9Al94CPj_Tc3K7Adin-tN9x1RSjjx2UzJ4SV7Q/edit#gid=1679077334)
- City/Town Population: [Census 2017 ACS 5-Year Estimates](https://factfinder.census.gov/faces/tableservices/jsf/pages/productview.xhtml)
- Zip Population: [Census 2010 Decennial Population](https://data.census.gov/cedsci/)