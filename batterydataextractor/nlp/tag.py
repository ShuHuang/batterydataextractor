# -*- coding: utf-8 -*-
"""
batterydataextractor.nlp.tag

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Tagger implementations. Used for part-of-speech tagging and named entity recognition.
"""
from abc import ABCMeta, abstractmethod
import six
from transformers import pipeline, AutoTokenizer


class BaseTagger(six.with_metaclass(ABCMeta)):
    """Abstract tagger class from which all taggers inherit.
    Subclasses must implement a ``tag()`` method.
    """

    @abstractmethod
    def tag(self, tokens):
        """Return a list of (token, tag) tuples for the given list of token strings.
        :param list(str) tokens: The list of tokens to tag.
        :rtype: list(tuple(str, str))
        """
        return

    def tag_sents(self, sentences):
        """Apply the ``tag`` method to each sentence in ``sentences``."""
        return [self.tag(s) for s in sentences]

    def evaluate(self, gold):
        """Evaluate the accuracy of this tagger using a gold standard corpus.
        :param list(list(tuple(str, str))) gold: The list of tagged sentences to score the tagger on.
        :returns: Tagger accuracy value.
        :rtype: float
        """
        tagged_sents = self.tag_sents([w for (w, t) in sent] for sent in gold)
        gold_tokens = sum(gold, [])
        test_tokens = sum(tagged_sents, [])
        accuracy = float(sum(x == y for x, y in six.moves.zip(gold_tokens, test_tokens))) / len(test_tokens)
        return accuracy


class NoneTagger(BaseTagger):
    """Tag every token with None."""

    def tag(self, tokens):
        """"""
        return [(token, None) for token in tokens]


class BertTagger(BaseTagger):
    """BERT Tagger"""

    def __init__(self, model=None, device=None):
        """"""
        self.model = model if model is not None else "batterydata/bde-pos-bert-cased-base"
        self.device = device if device is not None else -1
        self.tokenizer = AutoTokenizer.from_pretrained(self.model, model_max_length=512, use_auth_token=True)

    def tag(self, tokens):
        """Return a list of (token, tag) tuples for a given list of (token, tag) tuples.

        :param list(str) tokens: The list of tokens to tag.
        """
        classifier = pipeline("token-classification", model=self.model, tokenizer=self.tokenizer, use_auth_token=True,
                              aggregation_strategy="simple", device=self.device)
        tags = [token[0]['entity_group'] for token in classifier(tokens)]
        tagged_sent = list(zip(tokens, tags))
        return tagged_sent
