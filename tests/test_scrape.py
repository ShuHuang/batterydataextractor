import unittest
from batterydataextractor.scrape import RSCWebScraper


class TestRSCScraper(unittest.TestCase):

    rsc_scraper = RSCWebScraper()

    def test_get_doi_rsc(self):
        """
        Test if the list of dois can be found with the RSCWebScraper
        """
        dois = self.rsc_scraper.get_doi(query="battery materials", page=3)
        length = len(dois)

        self.assertEqual(length, 25)

    def test_els_scraper(self):
        # As Elsevier web-scraper requires API key, we have no tests here.
        # See `examples/webscrape/elsevier.py` for more details.
        pass

    def test_spr_scraper(self):
        # As Springer web-scraper requires API key, we have no tests here.
        # See `examples/webscrape/spr.py` for more details.
        pass


if __name__ == "__main__":
    unittest.main()
