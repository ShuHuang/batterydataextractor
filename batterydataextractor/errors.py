# -*- coding: utf-8 -*-
"""
batterydataextractor.errors

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Error classes for BatteryDataExtractor.
"""


class BatteryDataExtractorError(Exception):
    """Base ChemDataExtractor exception."""
    pass


class ReaderError(BatteryDataExtractorError):
    """Raised when a reader is unable to read a document."""


class ModelNotFoundError(BatteryDataExtractorError):
    """Raised when a model file could not be found."""
