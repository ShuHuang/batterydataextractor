# -*- coding: utf-8 -*-
"""
batterydataextractor.nlp.cem

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Named entity recognition (NER) for Chemical entity mentions (CEM).
author:
"""
from transformers import pipeline, AutoTokenizer
from operator import itemgetter
from itertools import groupby
from .tag import BertTagger, BaseTagger


class BertCemTagger(BertTagger):
    """"""

    base_tagger = BertTagger()

    def tag(self, tokens):
        tuples = tokens
        cner_tagger = pipeline("token-classification", model="batterydata/bde-cner-batteryonlybert-cased-base",
                               tokenizer=AutoTokenizer.from_pretrained("batterydata/bde-cner-batteryonlybert-cased-base",
                                                                       model_max_length=512, use_auth_token=True),
                               aggregation_strategy="simple", use_auth_token=True, device=self.device)
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
        # ner, new_tags = [], []
        for tagger in self.taggers:
            tag_gen = tagger.tag(tokens)
            materials = [tag[0][0] for tag in tag_gen]
            tags = [tag[-1] for tag in tag_gen]
        #     seq = [next(group) for key, group in groupby(enumerate(tags), key=itemgetter(1))]
        #     print('-----')
        #     print(materials)
        #     print(tags)
        #     print(seq)
        #     if seq[0][-1] == "O":
        #         seq = seq[1:]
        #     if len(seq) % 2 == 0:
        #         token_indices = [(seq[i][0], seq[i+1][0]) for i in range(0, len(seq), 2)]
        #     else:
        #         token_indices = [(seq[i][0], seq[i+1][0]) for i in range(0, len(seq)-1, 2)]
        #         token_indices.append((seq[-1][0], len(materials)))
        #     for token_index in token_indices:
        #         ner.append(" ".join(materials[token_index[0]:token_index[1]]))
        #         new_tags.append("MAT")
        # token_tags = list(zip(ner, new_tags))
        token_tags = list(zip(materials, tags))
        return token_tags
