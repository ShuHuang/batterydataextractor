# -*- coding: utf-8 -*-
"""
batterydataextractor.nlp.cem

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Named entity recognition (NER) for Chemical entity mentions (CEM).
author:
"""
import six
from transformers import pipeline
from .tag import BertTagger, BaseTagger


class BertCemTagger(BertTagger):
    """"""
    base_tagger = BertTagger()

    def tag(self, tokens):
        tuples = tokens
        cner_tagger = pipeline("token-classification", model="batterydata/cner-batterybert-cased-base",
                               aggregation_strategy="simple", use_auth_token=True)
        result = cner_tagger([token[0] for token in tuples])
        labels = ['O' if token == [] else 'MAT' for token in result]
        tagged_sent = list(zip(tuples, labels))
        return tagged_sent


class CemTagger(BaseTagger):
    """Return the combined output of a number of chemical entity taggers."""

    taggers = [BertCemTagger()]

    def tag(self, tokens):
        """Run individual chemical entity mention taggers and return union of matches, with some postprocessing."""
        # Combine output from individual taggers
        tags = [None] * len(tokens)
        for tagger in self.taggers:
            tag_gen = tagger.tag(tokens)
            for i, (token, newtag) in enumerate(tag_gen):
                if newtag == 'MAT':
                    tags[i] = 'MAT'
                # if newtag == 'I-MAT' and not (i == 0 or tag_gen[i - 1][1] not in {'B-MAT', 'I-MAT'}):
                #     tags[i] = 'I-MAT'  # Always overwrite I-CM
                # elif newtag == 'B-MAT' and tags[i] is None:
                #     tags[i] = 'B-MAT'  # Only overwrite B-CM over None
        token_tags = list(six.moves.zip(tokens, tags))
        return token_tags
