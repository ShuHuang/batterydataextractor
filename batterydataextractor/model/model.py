# -*- coding: utf-8 -*-
"""
batterydataextractor.model.model

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Model classes for physical properties.
author:
"""
import logging

from .base import BaseModel, StringType, ListType, ModelType

from ..parse.cem import CompoundParser
from ..parse.bert import BertParser

log = logging.getLogger(__name__)


class Compound(BaseModel):
    names = ListType(StringType())
    parsers = [CompoundParser()]

    def merge(self, other):
        """Merge data from another Compound into this Compound."""
        log.debug('Merging: %s and %s' % (self.serialize(), other.serialize()))
        for k in self.keys():
            for new_item in other[k]:
                if new_item not in self[k]:
                    self[k].append(new_item)
        log.debug('Result: %s' % self.serialize())
        return self

    @property
    def is_unidentified(self):
        if not self.names:
            return True
        return False

    @property
    def is_id_only(self):
        """Return True if identifier information only."""
        for key, value in self.items():
            if key not in {'names', 'labels', 'roles'} and value:
                return False
        if self.names:
            return True
        return False


class PropertyData(BaseModel):
    value = StringType(contextual=False, required=True)
    # units = StringType(contextual=False)
    specifier = StringType(contextual=False)
    compound = ModelType(Compound, contextual=False)
    parser = BertParser()
    parsers = [parser]
