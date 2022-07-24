# -*- coding: utf-8 -*-
"""
batterydataextractor.scrape.elsevier

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Elsevier web-scraper
"""
import six
import json
import requests
import numpy as np
from bs4 import BeautifulSoup
from .base import BaseWebScraper


class ElsevierWebScraper(BaseWebScraper):
    """
    Elsevier web-scraper
    """
    base_url = 'https://api.elsevier.com/content/search/sciencedirect'

    def __init__(self, api_key, query):
        """
        :param api_key: API key from the Elsevier Developer Portal (https://dev.elsevier.com/)
        :param query: query text (e.g. battery materials)
        """
        super().__init__()
        self.api_key = api_key
        self.data = {"qs": query,
                     "date": 2022,
                     # "volume": 0,
                     "display": {"show": 100, "offset": 0}
                     }
        self.headers = {'x-els-apikey': api_key, 'Content-Type': 'application/json', 'Accept': 'application/json'}

    def get_response(self):
        """
        Get the requests response from the url.
        :return: requests response.
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
        Get the list of dois from the query text, year, and volume.
        :param year: the year of published papers
        :param volume: the volume of the journal
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
        Download the xml file from the doi
        :param doi: doi of a paper
        :param file_location: saving location
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
        Get the metadata and abstract from a Elsevier xml file
        :param els_document: Elsevier xml content
        :return: a dictionary of metadata and abstract
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


def fix_elsevier_xml_whitespace(document):
    """ Fix tricky xml tags"""
    # space hsp  and refs correctly
    for el in document.xpath('.//ce:hsp'):
        parent = el.getparent()
        previous = el.getprevious()
        if parent is None:
            continue
        # Append the text to previous tail (or parent text if no previous), ensuring newline if block level
        if el.text and isinstance(el.tag, six.string_types):
            if previous is None:
                if parent.text:
                    if parent.text.endswith(' '):
                        parent.text = (parent.text or '') + '' + el.text
                    else:
                        parent.text = (parent.text or '') + ' ' + el.text
            else:
                if previous.tail:
                    if previous.tail.endswith(' '):
                        previous.tail = (previous.tail or '') + '' + el.text
                    else:
                        previous.tail = (previous.tail or '') + ' ' + el.text
        # Append the tail to last child tail, or previous tail, or parent text, ensuring newline if block level
        if el.tail:
            if len(el):
                last = el[-1]
                last.tail = (last.tail or '') + el.tail
            elif previous is None:
                if el.tail.startswith(' '):
                    parent.text = (parent.text or '') + '' + el.tail
                else:
                    parent.text = (parent.text or '') + ' ' + el.tail
            else:
                if el.tail.startswith(' '):
                    previous.tail = (previous.tail or '') + '' + el.tail
                else:
                    previous.tail = (previous.tail or '') + ' ' + el.tail

        index = parent.index(el)
        parent[index:index + 1] = el[:]
    return document


def els_xml_whitespace(document):
    """ Remove whitespace in xml.text or xml.tails for all elements, if it is only whitespace """
    # selects all tags and checks if the text or tail are spaces
    for el in document.xpath('//*'):
        if str(el.text).isspace():
            el.text = ''
        if str(el.tail).isspace():
            el.tail = ''
        if el.text:
            el.text = el.text.replace('\n', ' ')
    return document


def els_clean_abstract(document):
    """ Remove <ce:section-title> in <ce:abstract>"""
    # selects all tags and checks if the text or tail are spaces
    for el in document.xpath('.//ce:abstract'):
        next_els = el.getchildren()
        for next_el in next_els:
            if next_el.tag == '{http://www.elsevier.com/xml/common/dtd}section-title':
                parent = next_el.getparent()
                if parent is None:
                    continue
                if next_el.tail:
                    previous = next_el.getprevious()
                    if previous is None:
                        parent.text = (parent.text or '') + next_el.tail
                    else:
                        previous.tail = (previous.tail or '') + next_el.tail
                parent.remove(next_el)
    return document
