# -*- coding: utf-8 -*-
"""
batterydataextractor.doc.head

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
HeadData Document elements
"""
from .element import BaseElement
import logging
log = logging.getLogger(__name__)


class HeadData(BaseElement):

    def __init__(self, data):
        super(HeadData, self).__init__()
        self._data = data
        self._title = None
        self._authors = None
        self._doi = None
        self._date = None
        self._abstract = None
        for key, value in data.items():
            setattr(self, key, value)

    def __repr__(self):
        return {k: v for k, v in self.data.items() if v}.__str__()

    @property
    def records(self):
        return []

    def serialize(self):
        return {k: v for k, v in self.data.items() if v}

    @property
    def title(self):
        """The article title"""

        return self._title

    @property
    def authors(self):
        """The article Authors
        type:: list()
        """
        return self._authors

    @property
    def doi(self):
        """The source DOI"""
        return self._doi

    @property
    def abstract(self):
        """The abstract"""
        return self._abstract

    @property
    def date(self):
        """The source publish date"""
        return self._date

    @property
    def data(self):
        """Returns all data as a dict()"""
        return {k.lstrip('_'): v for k, v in self._data.items()}

