# -*- coding: utf-8 -*-
"""
batterydataextractor.reader.__init__

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Paper reader
author:
"""
from .elsevier import ElsevierXmlReader
from .markup import HtmlReader, XmlReader
from .plaintext import PlainTextReader
from .rsc import RscHtmlReader


DEFAULT_READERS = [
    RscHtmlReader(),
    ElsevierXmlReader(),
    XmlReader(),
    HtmlReader(),
    PlainTextReader(),
]
