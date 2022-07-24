# -*- coding: utf-8 -*-
"""
batterydataextractor.nlp.abbrev

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Abbreviation detection.
"""
from transformers import pipeline, AutoTokenizer
from abc import ABCMeta
import six


class AbbreviationDetector(six.with_metaclass(ABCMeta)):
    """"""

    def __init__(self, model_name="batterydata/bde-abbrev-batteryonlybert-cased-base", device=None):
        self.tokenizer = AutoTokenizer.from_pretrained(model_name, model_max_length=512, use_auth_token=True)
        self.device = device if device else -1
        self.model = pipeline('token-classification', model_name, tokenizer=self.tokenizer,
                              use_auth_token=True, aggregation_strategy='simple', device=self.device)

    def detect_spans(self, tokens):
        """
        Detects abbreviations in a list of tokens.

        :param tokens: a list of tokens
        :return:
        """
        results = self.model(" ".join(tokens))
        long, short = [], []
        for entity in results:
            if entity['entity_group'] == 'long':
                long.append((entity['start'], entity['end']))
            elif entity['entity_group'] == 'short':
                short.append((entity['start'], entity['end']))
        return short, long

    def detect(self, tokens):
        short_words = []
        long_words = []
        doc = " ".join(tokens)
        abbr_span, long_span = self.detect_spans(tokens)
        for abbr in abbr_span:
            short_words.append(("Abbr: ", doc[abbr[0]: abbr[1]]))
        for long in long_span:
            long_words.append(("LF: ", doc[long[0]: long[1]]))
        return short_words, long_words
