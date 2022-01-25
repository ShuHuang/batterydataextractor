# -*- coding: utf-8 -*-
"""
batterydataextractor.nlp.tokenize

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Word and sentence tokenizers.
author:
"""
from abc import ABCMeta, abstractmethod
import logging
import re
import six
import spacy

log = logging.getLogger(__name__)


class BaseTokenizer(six.with_metaclass(ABCMeta)):
    """Abstract base class from which all Tokenizer classes inherit.
    Subclasses must implement a ``span_tokenize(text)`` method that returns a list of integer offset tuples that
    identify tokens in the text.
    """

    def tokenize(self, s):
        """Return a list of token strings from the given sentence.
        :param string s: The sentence string to tokenize.
        :rtype: iter(str)
        """
        return [s[start:end] for start, end in self.span_tokenize(s)]

    @abstractmethod
    def span_tokenize(self, s):
        """Return a list of integer offsets that identify tokens in the given sentence.
        :param string s: The sentence string to tokenize.
        :rtype: iter(tuple(int, int))
        """
        return

    def tokenize_sents(self, strings):
        """Apply the ``tokenize`` method to each sentence in ``strings``.
        :param list(str) strings: A list of sentence strings to tokenize.
        :rtype: iter(iter(str))
        """
        return [self.tokenize(s) for s in strings]

    def span_tokenize_sents(self, strings):
        """Apply the ``span_tokenize`` method to each sentence in ``strings``.
        :param list(str) strings: A list of sentence strings to tokenize.
        :rtype: iter(iter(tuple(int, int)))
        """
        for s in strings:
            yield list(self.span_tokenize(s))


def regex_span_tokenize(s, regex):
    """Return spans that identify tokens in s split using regex."""
    left = 0
    for m in re.finditer(regex, s, re.U):
        right, next = m.span()
        if right != 0:
            yield left, right
        left = next
    yield left, len(s)


class SentenceTokenizer(BaseTokenizer):
    """Sentence tokenizer from Spacy."""

    model = 'en_core_web_md'  # This is available from Spacy

    def __init__(self, model=None):
        self.model = model if model is not None else self.model
        self._tokenizer = None
        log.debug('%s: Initializing with %s' % (self.__class__.__name__, self.model))

    def span_tokenize(self, s):
        """Return a list of integer offsets that identify sentences in the given text.
        :param string s: The text to tokenize into sentences.
        :rtype: iter(tuple(int, int))
        """
        if self._tokenizer is None:
            self._tokenizer = spacy.load(self.model)
        sents = list(self._tokenizer(s).sents)
        spans = [(i.start_char, i.end_char) for i in sents]
        return spans


class ChemSentenceTokenizer(SentenceTokenizer):
    """"""
    model = 'en_core_web_md'  # This is available from Spacy
