# -*- coding: utf-8 -*-
"""
The example of RSC scraper.
"""

__author__ = "Shu Huang"
__email__ = "sh2009@cam.ac.uk"

from batterydataextractor.scrape import RSCWebScraper


def main(url, query, page, file_location):
    scraper = RSCWebScraper(url=url)
    dois = scraper.get_doi(query=query, page=page)
    for doi in dois:
        try:
            scraper.download_doi(doi, file_location)
        # Some papers don't have html access
        except:
            continue
    return


if __name__ == "__main__":
    # Download papers within a certain date range
    url = "https://pubs.rsc.org/en/results/all?Category=All&AllText=battery%20materials&IncludeReference=false&Select" \
          "Journal=false&DateRange=true&SelectDate=true&DateToYear={}&DateFromYear={}&DateFromMonth={}&DateTo" \
          "Month={}&PriceCode=False&OpenAccess=false".format("2022", "2021", "06", "01")
    query = "battery materials"
    location = r"F:\work\to_date_papers\rsc\\"
    for page in range(1, 120):
        main(url, query, page, location)
