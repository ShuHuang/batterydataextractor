# -*- coding: utf-8 -*-
"""
The example of Elsevier scraper.
"""

__author__ = "Shu Huang"
__email__ = "sh2009@cam.ac.uk"

from batterydataextractor.scrape import ElsevierWebScraper


def main(api_key, query, year, file_location):
    scraper = ElsevierWebScraper(api_key=api_key, query=query)
    dois = scraper.get_doi(year=year)
    for doi in dois:
        scraper.download_doi(doi, file_location)
    return


if __name__ == "__main__":
    api_key = ""
    query = "battery materials"
    location = r"F:\work\to_date_papers\els\new\\"
    year = 2022
    main(api_key=api_key, query=query, year=year, file_location=location)
