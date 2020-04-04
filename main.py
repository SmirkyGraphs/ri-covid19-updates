from src import scraper
from src import cleaner
from src import tweeter

google_sheet = '1n-zMS9Al94CPj_Tc3K7Adin-tN9x1RSjjx2UzJ4SV7Q/export?format=csv&gid='

raw_general = './data/raw/ri-covid-19.csv'
raw_geo = './data/raw/geo-ri-covid-19.csv'

if __name__ == "__main__":
    # scrape, clean & tweet out general information
    scraper.scrape_sheet(google_sheet, '0', raw_general)
    cleaner.clean_general(raw_general)
    tweeter.send_tweet()
    
    # scrape & clean breakdown by city/town
    scraper.scrape_sheet(google_sheet, '1679077334', raw_geo)
    cleaner.clean_geographic(raw_geo)
