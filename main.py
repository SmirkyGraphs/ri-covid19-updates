from src import scraper
from src import cleaner
from src import tweeter

raw_general = './data/raw/ri-covid-19.csv'
raw_geo = './data/raw/geo-ri-covid-19.csv'

google_sheet = '1n-zMS9Al94CPj_Tc3K7Adin-tN9x1RSjjx2UzJ4SV7Q/export?format=csv&gid='

if __name__ == "__main__":
    # scrape, clean & tweet out general information
    #scraper.scrape_sheet(google_sheet, raw_general, raw_geo)
    cleaner.clean_general(raw_general)
    cleaner.clean_geographic(raw_geo)
    tweeter.send_tweet()
