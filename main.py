from src import scraper
from src import cleaner
from src import tweeter
from src import plots
from src import reports

main_sheet = '1c2QrNMz8pIbYEKzMJL7Uh2dtThOJa2j1sSMwiDo5Gz4/export?format=csv&gid='

if __name__ == "__main__":
    # scrape, clean & tweet out general information
    #scraper.scrape_sheet(main_sheet)
    cleaner.clean_general('ri-covid-19')
    cleaner.clean_geographic('geo-ri-covid-19')
    #tweeter.send_tweet()

    # scrape, clean infrequently updated data
    #scraper.scrape_nursing_homes(main_sheet)
    #scraper.scrape_zip_codes(main_sheet)
    cleaner.clean_nursing_homes('nurse-homes-covid-19')
    cleaner.clean_zip_codes('zip-codes-covid-19')

    # scrape revised data
    #scraper.scrape_revised(main_sheet)
    cleaner.clean_revised('revised-data')

    # make graphs
    plots.make_plots()

    # run reports
    reports.run_reports()

    # archieve page
    scraper.archive_page()