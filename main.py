from src import scraper
from src import cleaner
from src import tweeter

raw_general = './data/raw/ri-covid-19.csv'
raw_geo = './data/raw/geo-ri-covid-19.csv'
raw_facility = './data/raw/facility-covid-19.csv'
raw_zip = './data/raw/zip-codes-covid-19.csv'
raw_dem = './data/raw/demographics-covid-19.csv'

main_sheet = '1n-zMS9Al94CPj_Tc3K7Adin-tN9x1RSjjx2UzJ4SV7Q/export?format=csv&gid='
facility_sheet = '2PACX-1vQUem_oGj3-KdLreZ3swTBx6q264zWqJUWc39nWSgE-KSYoqDRmlFyksSIP7H_lLNTVtr5lHbudeDz0'

if __name__ == "__main__":
    # scrape, clean & tweet out general information
    scraper.scrape_sheet(main_sheet, raw_general, raw_geo, raw_dem)
    cleaner.clean_general(raw_general)
    cleaner.clean_geographic(raw_geo)
    tweeter.send_tweet()

    # scrape, clean infrequently updated data
    scraper.scrape_nursing_homes(facility_sheet, raw_facility)
    scraper.scrape_zip_codes(main_sheet, raw_zip)
    cleaner.clean_zip_codes(raw_zip)
    cleaner.clean_facilities(raw_facility)