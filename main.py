from src import scraper
from src import cleaner
from src import tweeter
from src import plots

main_sheet = '1n-zMS9Al94CPj_Tc3K7Adin-tN9x1RSjjx2UzJ4SV7Q/export?format=csv&gid='
facility_sheet = '2PACX-1vQUem_oGj3-KdLreZ3swTBx6q264zWqJUWc39nWSgE-KSYoqDRmlFyksSIP7H_lLNTVtr5lHbudeDz0'

if __name__ == "__main__":
    # scrape, clean & tweet out general information
    scraper.scrape_sheet(main_sheet)
    cleaner.clean_general('ri-covid-19')
    cleaner.clean_geographic('geo-ri-covid-19')
    tweeter.send_tweet()

    # scrape, clean infrequently updated data
    scraper.scrape_nursing_homes(facility_sheet)
    scraper.scrape_zip_codes(main_sheet)
    cleaner.clean_nursing_homes('nurse-homes-covid-19')
    cleaner.clean_zip_codes('zip-codes-covid-19')

    # scrape revised data
    scraper.scrape_revised(main_sheet)
    cleaner.clean_revised('revised-data')

    # make graphs
    plots.testing_plot()
    plots.hospital_plot()
    plots.testing_ma_plot()
    plots.hospital_ma_plot()
    plots.city_rate_plot()
