# -*- coding: utf-8 -*-
"""
batterydataextractor.parse.cem

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Chemical entity mention parser elements.
"""
import logging
from .base import BaseSentenceParser
from ..nlp import CemTagger

log = logging.getLogger(__name__)


class CompoundParser(BaseSentenceParser):
    """Chemical name possibly with an associated label."""

    ct = CemTagger()

    def interpret(self, tokens):
        cems = self.ct.tag(tokens)
        for cem in cems:
            if cem[-1] == 'MAT':
                c = self.model(names=[cem[0]])
                yield c
