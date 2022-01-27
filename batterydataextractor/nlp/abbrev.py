# -*- coding: utf-8 -*-
"""
batterydataextractor.nlp.abbrev

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Abbreviation detection.
author:
"""
import spacy
import itertools


# Just for demonstration using spacy
# TODO: Change into transformers version
class AbbreviationDetector(object):
    """"""
    def __init__(self, model_name="en_abbreviation_detection_roberta_lar"):
        self.model = spacy.load(model_name)

    def detect_spans(self, tokens):
        doc = self.model(" ".join(tokens))
        entities = doc.ents
        text_label = [(e.text, e.start, e.end, e.label_) for e in entities]
        g_list = [list(g) for k, g in itertools.groupby(text_label, key=lambda x: x[-1])]
        new_tuples = [(" ".join(i), j, h, k[0]) for i, j, h, k in [zip(*i) for i in g_list]]
        pairs = []
        for index, tuples in enumerate(new_tuples):
            if tuples[-1] == "LF":
                lf_tokens = tuples[0].split(" ")
                lf_spans = (tuples[1][0], tuples[2][-1])
                left, right = index, index
                # TODO: Need to optimise this logic
                # TODO: Use the same tokenizer rather than this one?
                while True:
                    if right < len(new_tuples):
                        if new_tuples[right][-1] == "AC":
                            abbrev_spans = (new_tuples[right][1][0], new_tuples[right][2][-1])
                            # abbrev_text = [new_tuples[right][0]]
                            break
                        right += 1
                    else:
                        if new_tuples[left][-1] == "AC" and left >= 1:
                            abbrev_spans = (new_tuples[left][1][0], new_tuples[left][2][-1])
                            # abbrev_text = [new_tuples[left][0]]
                            break
                        left -= 1
                pair = (abbrev_spans, lf_spans)
                pairs.append(pair)
        return pairs

    def detect(self, tokens):
        results = []
        doc = self.model(" ".join(tokens))
        for abbr_span, long_span in self.detect_spans(tokens):
            results.append((doc[abbr_span[0]:abbr_span[1]].text.split(" "), doc[long_span[0]:long_span[1]].text.split(" ")))
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
