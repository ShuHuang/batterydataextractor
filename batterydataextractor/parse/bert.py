# -*- coding: utf-8 -*-
"""
batterydataextractor.parse.bert

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Bert parsers.
author:
"""
import logging
from .base import BaseSentenceParser

log = logging.getLogger(__name__)


class BertParser(BaseSentenceParser):
    """Bert Parser."""

    def interpret(self, tokens):
        # For testing
        token = tokens[0][0]
        for i in self.model.defined_names:
            c = self.model(value=token,
                           specifier=i
                           )
            yield c
