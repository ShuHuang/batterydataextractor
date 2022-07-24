# -*- coding: utf-8 -*-
"""
batterydataextractor.nlp.cem

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Named entity recognition (NER) for Chemical entity mentions (CEM).
"""
from .tag import BertTagger, BaseTagger


class BertCemTagger(BertTagger):
    """"""

    base_tagger = BertTagger()

    def tag(self, tokens):
        tuples = tokens
        cner_tagger = pipeline("token-classification", model="batterydata/bde-cner-batteryonlybert-uncased-base",
                               tokenizer=AutoTokenizer.from_pretrained("batterydata/bde-cner-batteryonlybert-uncased-base",
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
        for tagger in self.taggers:
            tag_gen = tagger.tag(tokens)
            materials = [tag[0][0] for tag in tag_gen]
            tags = [tag[-1] for tag in tag_gen]
        token_tags = list(zip(materials, tags))
        return token_tags
