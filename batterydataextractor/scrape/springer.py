# -*- coding: utf-8 -*-
"""
batterydataextractor.scrape.springer

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Web-scraping papers from the Springer publisher.
author: Shu Huang (sh2009@cam.ac.uk)
"""
__author__ = "Shu Huang"
__email__ = "sh2009@cam.ac.uk"

import json
import requests
from bs4 import BeautifulSoup
from .base import BaseWebScraper


class SpringerWebScraper(BaseWebScraper):
    def __init__(self, query, api_key):
        """

        :param query_text:
        :param api_key:
        :param start:
        :param year:
        :param max_return:
        """
        self.api_key = api_key
        self.query = query.replace(" ", '%20')

    def get_doi(self, year=2022, start=0, max_return=100):
        """

        :return:
        """
        url = "http://api.springernature.com/meta/v2/json?&q={}%20type:Journal%20year:{}&s={}&p={}&api_key={}".format(
            self.query, year, start, max_return, self.api_key)
        web_content = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}).content
        content = json.loads(web_content.decode('utf-8'))
        dois = [content['records'][i]['doi'] for i in range(max_return)]
        return dois

    def get_xml(self, doi):
        """

        :param dois:
        :return:
        """
        url = "https://api.springernature.com/meta/v2/pam?q=doi:{}&p=2&api_key={}".format(doi, self.api_key)
        return url

    def download_doi(self, doi, file_location):
        """

        :param doi:
        :param file_location:
        :return:
        """
        url = self.get_xml(doi)
        web_content = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}).content
        result = self.get_spr_abstract(web_content)
        doi = result['doi'].replace("/", "_")
        date = result['date']
        name = date + "_" + doi
        with open(file_location + name + '.xml', 'wb') as f:
            f.write(web_content)
            f.close()
        return

    @staticmethod
    def get_spr_abstract(spr_document):
        soup = BeautifulSoup(spr_document, features="html.parser")
        abstract = ''
        for i in soup.find_all("p"):
            if i.parent.name == "abstract":
                abstract = i.text.split("\documentclass")[0]
                abstract = abstract.replace("\n", "")
                abstract = abstract.replace("\t", "")
        date = soup.find_all("prism:publicationdate")[0].get_text()
        doi = soup.find_all("prism:doi")[0].get_text()
        # year = date.find('year').get_text()
        # try:
        #     month = date.find('month').get_text()
        #     if len(month) == 1:
        #         month = '0' + month
        # except AttributeError:
        #     month = '01'
        # try:
        #     day = date.find('day').get_text()
        #     if len(day) == 1:
        #         day = '0' + day
        # except AttributeError:
        #     day = '01'
        # date = year + month + day
        journal = soup.find_all("prism:publicationname")[0].get_text()
        title = soup.find_all("dc:title")[0].get_text()
        return {"title": title, "doi": doi, "date": date, "journal": journal, "abstract": abstract}
