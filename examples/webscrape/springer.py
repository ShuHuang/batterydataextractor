# -*- coding: utf-8 -*-
"""
The example of Springer scraper.
"""

__author__ = "Shu Huang"
__email__ = "sh2009@cam.ac.uk"

from batterydataextractor.scrape import SpringerMetaWebScraper, SpringerTDMWebScraper


def run_meta_scraper(api_key, query, year, file_location, start=0):
    """
    Springer meta web-scraper runner
    :param api_key: Meta API key from the Springer API
    :param query: query text (e.g. battery materials)
    :param year: the year of published papers
    :param file_location: saving location
    :param start: start index
    :return:
    """
    scraper = SpringerMetaWebScraper(api_key=api_key, query=query)
    dois = scraper.get_doi(year=year, start=start)
    for doi in dois:
        scraper.download_doi(doi, file_location)
    return


def run_tdm_scraper(api_key, query, data_from, date_to, file_location, start=0):
    """
    Springer TDM web-scraper runner
    :param api_key: TDM API key from the Springer API
    :param query: query text (e.g. battery materials)
    :param data_from: the starting date for searching papers
    :param date_to: the end date for searching papers
    :param file_location: saving location
    :param start: start index
    :return:
    """
    scraper = SpringerTDMWebScraper(api_key=api_key, query=query)
    dois = scraper.get_doi(date_from=data_from, date_to=date_to, start=start)
    for doi in dois:
        scraper.download_doi(doi, file_location)
    return


if __name__ == "__main__":
    api_key = ""
    query = "battery materials"
    location = r"F:\work\to_date_papers\spr\\"
    # Use different scraper according to the API key.
    scraper = 'TDM'
    if scraper == "Meta":
        year = 2021
        for start in range(0, 1000, 100):
            run_meta_scraper(api_key=api_key, query=query, year=year, file_location=location, start=start)
    if scraper == "TDM":
        date_from = '2021-06-01'
        date_to = '2022-01-11'
        for start in range(0, 1000, 100):
            run_tdm_scraper(api_key=api_key, query=query, data_from=date_from, date_to=date_to, file_location=location,
                            start=start)
