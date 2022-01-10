# -*- coding: utf-8 -*-
"""
The example of Springer scraper.
"""

__author__ = "Shu Huang"
__email__ = "sh2009@cam.ac.uk"

from batterydataextractor.scrape import SpringerWebScraper


def main(api_key, query, year, file_location, start=0):
    scraper = SpringerWebScraper(api_key=api_key, query=query)
    dois = scraper.get_doi(year=year, start=start)
    for doi in dois:
        scraper.download_doi(doi, file_location)
    return


if __name__ == "__main__":
    api_key = ""
    query = "battery materials"
    location = r"F:\work\to_date_papers\spr\abstracts_only\\"
    year = 2021
    for start in range(0, 10000, 100):
        main(api_key=api_key, query=query, year=year, file_location=location, start=start)
