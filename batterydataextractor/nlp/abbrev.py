# -*- coding: utf-8 -*-
"""
batterydataextractor.nlp.abbrev

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Abbreviation detection.
author:
"""
from transformers import pipeline
import itertools


# TODO: Change into transformers version
class AbbreviationDetector(object):
    """"""
    def __init__(self, model_name="batterydata/bde-abbrev-batterybert-base"):
        self.model = pipeline('token-classification', model_name, use_auth_token=True)

    def detect_spans(self, tokens):
        """
        Detects abbreviations in a list of tokens.

        :param tokens:
        :return:
        """
        results = self.model(" ".join(tokens))
        b_short_spans, i_short_spans, b_long_spans, i_long_spans = [], [], [], []
        for result in results:
            if result['index'] == 1:
                b_short_spans.append((result['start'], result['end']))
            elif result['index'] == 2:
                i_short_spans.append((result['start'], result['end']))
            elif result['index'] == 4:
                b_long_spans.append((result['start'], result['end']))
            elif result['index'] == 5:
                i_long_spans.append((result['start'], result['end']))

        # if i_short_spans != []:


        pairs = []
        # pair = (abbrev_spans, lf_spans)
        #             pairs.append(pair)

        # doc = self.model(" ".join(tokens))
        # entities = doc.ents
        # text_label = [(e.text, e.start, e.end, e.label_) for e in entities]
        # g_list = [list(g) for k, g in itertools.groupby(text_label, key=lambda x: x[-1])]
        # new_tuples = [(" ".join(i), j, h, k[0]) for i, j, h, k in [zip(*i) for i in g_list]]


        # for index, tuples in enumerate(new_tuples):
        #     if tuples[-1] == "LF":
        #         lf_spans = (tuples[1][0], tuples[2][-1])
        #         left, right = index, index
        #         # TODO: Need to optimise this logic
        #         # TODO: Use the same tokenizer rather than this one?
        #         abbrev_spans = []
        #         for r in range(right, len(new_tuples)):
        #             if new_tuples[r][-1] == "AC":
        #                 abbrev_spans = (new_tuples[r][1][0], new_tuples[r][2][-1])
        #                 break
        #         if abbrev_spans == []:
        #             for l in range(left, -1, -1):
        #                 if new_tuples[l][-1] == "AC":
        #                     abbrev_spans = (new_tuples[l][1][0], new_tuples[l][2][-1])
        #                     break
        #         if abbrev_spans != []:
        #             pair = (abbrev_spans, lf_spans)
        #             pairs.append(pair)
        return pairs

    def detect(self, tokens):
        results = []
        # doc = self.model(" ".join(tokens))
        # for abbr_span, long_span in self.detect_spans(tokens):
            # results.append((doc[abbr_span[0]:abbr_span[1]].text.split(" "), doc[long_span[0]:long_span[1]].text.split(" ")))
        return results


class ChemAbbreviationDetector(AbbreviationDetector):
    """Chemistry-aware abbreviation detector.
    This abbreviation detector has an additional list of string equivalents (e.g. Silver = Ag) that improve abbreviation
    detection on chemistry texts.
    """
    #: String equivalents to use when detecting abbreviations.
    # TODO: include rule-based abbrev into it?
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
