# -*- coding: utf-8 -*-
"""
batterydataextractor.model.model

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Model classes for physical properties.
"""
import logging

from .base import BaseModel, StringType, ListType, FloatType

from ..parse.cem import CompoundParser
from ..parse.bert import BertMaterialParser, BertGeneralParser

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
    value = ListType(FloatType(required=True))
    units = StringType(contextual=False)
    raw_value = StringType(contextual=False)
    specifier = StringType(contextual=False)
    material = StringType(contextual=False, required=True)
    confidence_score = FloatType(contextual=False)
    original_text = StringType(contextual=False)
    device = FloatType(contextual=False)
    parsers = [BertMaterialParser()]


class GeneralInfo(BaseModel):
    answer = StringType(contextual=False, required=True)
    specifier = StringType(contextual=False)
    confidence_score = FloatType(contextual=False)
    original_text = StringType(contextual=False)
    device = FloatType(contextual=False)
    parsers = [BertGeneralParser()]
