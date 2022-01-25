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
        # tuples = self.base_tagger.tag(tokens)
        tuples = tokens
        cner_tagger = pipeline("token-classification", model="alvaroalon2/biobert_chemical_ner")
        result = cner_tagger([token[0] for token in tuples])
        labels = ['O' if token == [] else 'B-CM' for token in result]
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
                if newtag == 'I-CM' and not (i == 0 or tag_gen[i - 1][1] not in {'B-CM', 'I-CM'}):
                    tags[i] = 'I-CM'  # Always overwrite I-CM
                elif newtag == 'B-CM' and tags[i] is None:
                    tags[i] = 'B-CM'  # Only overwrite B-CM over None
        token_tags = list(six.moves.zip(tokens, tags))
        return token_tags
