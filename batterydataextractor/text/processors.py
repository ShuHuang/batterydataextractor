# -*- coding: utf-8 -*-
"""
batterydataextractor.text.processors

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Text processors.
"""
from abc import ABCMeta, abstractmethod
import logging
import six


log = logging.getLogger(__name__)


class BaseProcessor(six.with_metaclass(ABCMeta)):
    """Abstract processor class from which all processors inherit. Subclasses must implement a ``__call__()`` method."""

    @abstractmethod
    def __call__(self, text):
        """Process the text.
        :param string text: The input text.
        :returns: The processed text or None.
        :rtype: string or None
        """
        return text
