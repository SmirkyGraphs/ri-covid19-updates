from src import scraper
from src import cleaner
from src import tweeter
from src import plots
from src import reports

main_sheet = '1n-zMS9Al94CPj_Tc3K7Adin-tN9x1RSjjx2UzJ4SV7Q/export?format=csv&gid='

if __name__ == "__main__":
    # scrape, clean & tweet out general information
    scraper.scrape_sheet(main_sheet)
    cleaner.clean_general('ri-covid-19')
    cleaner.clean_geographic('geo-ri-covid-19')
    tweeter.send_tweet()

    # scrape, clean infrequently updated data
    scraper.scrape_nursing_homes(main_sheet)
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
    plots.then_v_now()

    # run reports
    reports.run_reports()