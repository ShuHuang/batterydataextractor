# -*- coding: utf-8 -*-
"""
batterydataextractor.nlp.abbrev

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Abbreviation detection.
author:
"""
from transformers import pipeline, AutoTokenizer


class AbbreviationDetector(object):
    """"""

    # TODO: improve the model
    def __init__(self, model_name="batterydata/bde-abbrev-batteryonlybert-cased-base", device=None):
        self.tokenizer = AutoTokenizer.from_pretrained(model_name, model_max_length=512, use_auth_token=True)
        self.device = device if device else -1
        self.model = pipeline('token-classification', model_name, tokenizer=self.tokenizer,
                              use_auth_token=True, aggregation_strategy='simple', device=self.device)

    def detect_spans(self, tokens):
        """
        Detects abbreviations in a list of tokens.

        :param tokens:
        :return:
        """
        results = self.model(" ".join(tokens))
        long, short, abbrev_spans, long_spans = [], [], [], []
        for result in results:
            if result['entity_group'] == 'long':
                long.append(result)
                abbrev_spans = (result['start'], result['end'])
            elif result['entity_group'] == 'short':
                short.append(result)
                long_spans = (result['start'], result['end'])
        pairs = []
        pair = (abbrev_spans, long_spans)
        pairs.append(pair)
        return pairs

    def detect(self, tokens):
        results = []
        doc = " ".join(tokens)
        for abbr_span, long_span in self.detect_spans(tokens):
            results.append((doc[abbr_span[0]:abbr_span[1]].split(" "), doc[long_span[0]:long_span[1]].split(" ")))
        return results


class ChemAbbreviationDetector(AbbreviationDetector):
    """Chemistry-aware abbreviation detector.
    This abbreviation detector has an additional list of string equivalents (e.g. Silver = Ag) that improve abbreviation
    detection on chemistry texts.
    """
    abbr_equivs = [
        ('silver', 'Ag'),
        ('gold', 'Au'),
        ('mercury', 'Hg'),
        ('lead', 'Pb'),
        ('tin', 'Sn'),
        ('tungsten', 'W'),
        ('iron', 'Fe'),
        ('sodium', 'Na'),
        ('potassium', 'K'),
        ('copper', 'Cu'),
        ('sulfate', 'SO4'),
    ]
