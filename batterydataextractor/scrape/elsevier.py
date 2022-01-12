# -*- coding: utf-8 -*-
"""
batterydataextractor.scrape.elsevier

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Web-scraping papers from the Elsevier publisher.
author: Shu Huang (sh2009@cam.ac.uk)
"""
import json
import requests
import numpy as np
from bs4 import BeautifulSoup
from .base import BaseWebScraper


class ElsevierWebScraper(BaseWebScraper):

    base_url = 'https://api.elsevier.com/content/search/sciencedirect'

    def __init__(self, api_key, query):
        """

        :param api_key:
        :param query:
        """
        self.api_key = api_key
        self.data = {"qs": query,
                     "date": 2022,
                     # "volume": 0,
                     "display": {"show": 100, "offset": 0}
                     }
        self.headers = {'x-els-apikey': api_key, 'Content-Type': 'application/json', 'Accept': 'application/json'}

    def get_response(self):
        """

        :return:
        """
        response = requests.put(self.base_url, data=json.dumps(self.data), headers=self.headers)
        response = response.text.replace('false', 'False').replace('true', 'True')
        try:
            response = eval(response)
        except BaseException:
            print(response)
        return response

    def get_doi(self, year=2022, volume=None):
        """

        :param volume:
        :param year:
        :return:
        """
        dois = []
        if volume is not None:
            self.data['volume'] = volume
        self.data["date"] = year
        response = self.get_response()
        if 'resultsFound' in response.keys():
            n = int(np.ceil(response['resultsFound'] / 100))
        else:
            n = 60
        for offset in range(1 + n):
            self.data["display"]["offset"] = offset
            response = self.get_response()
            if 'results' in response.keys():
                results = response['results']
                for result in results:
                    if 'doi' in result:
                        dois.append(result['doi'])
        return list(set(dois))

    def download_doi(self, doi, file_location):
        """

        :param doi:
        :param file_location:
        :return:
        """
        request_url = 'https://api.elsevier.com/content/article/doi/{}?apiKey={}&httpAccept=text%2Fxml'.format(
            doi, self.api_key)
        text = requests.get(request_url).text
        result = self.get_els_abstract(text)
        doi = result['doi'].replace("/", "_")
        date = result['date'].replace("-", "")
        name = date + "_" + doi
        with open(file_location + name + '.xml', 'w', encoding='utf-8') as f:
            f.write(text)
        return

    @staticmethod
    def get_els_abstract(els_document):
        """

        :param els_document:
        :return:
        """
        soup = BeautifulSoup(els_document, features="html.parser")
        date = soup.find_all("xocs:available-online-date")[0].get_text()
        title = soup.find_all("dc:title")[0].get_text()
        journal = soup.find_all("prism:publicationname")[0].get_text()
        abstract = soup.find_all("dc:description")[0].get_text()
        abstract = abstract.replace("\n", "")
        abstract = abstract.replace("\t", "")
        doi = soup.find_all("prism:doi")[0].get_text()
        return {"title": title, "doi": doi, "date": date, "journal": journal, "abstract": abstract}
