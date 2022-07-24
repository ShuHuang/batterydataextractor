# -*- coding: utf-8 -*-
"""
batterydataextractor.parse.base

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Base classes for parsing sentences and tables.
"""
from abc import abstractmethod, ABC
import logging

log = logging.getLogger(__name__)


class BaseParser:
    """"""
    model = None

    @abstractmethod
    def interpret(self, tokens):
        pass


class BaseSentenceParser(BaseParser, ABC):
    """
    Base class for parsing sentences. To implement a parser for a new property,
    implement the interpret function.
    """

    def parse_sentence(self, tokens):
        """
        Parse a sentence. This function is primarily called by the
        :attr:`~batterydataextractor.doc.text.Sentence.records` property of
        :class:`~batterydataextractor.doc.text.Sentence`.
        :param list[(token,tag)] tokens: List of tokens for parsing. When this method
            is called by :attr:`batterydataextractor.doc.text.Sentence.records`,
            the tokens passed in are :attr:`batterydataextractor.doc.text.Sentence.tagged_tokens`.
        :returns: All the models found in the sentence.
        :rtype: Iterator[:class:`batterydataextractor.model.base.BaseModel`]
        """
        for model in self.interpret(tokens):
            yield model
