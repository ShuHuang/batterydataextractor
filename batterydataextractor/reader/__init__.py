# -*- coding: utf-8 -*-
"""
batterydataextractor.reader.__init__

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Paper reader
"""
from .elsevier import ElsevierXmlReader
from .markup import HtmlReader, XmlReader
from .plaintext import PlainTextReader
from .rsc import RscHtmlReader
from .springer import SpringerXmlReader


DEFAULT_READERS = [
    RscHtmlReader(),
    ElsevierXmlReader(),
    SpringerXmlReader(),
    XmlReader(),
    HtmlReader(),
    PlainTextReader(),
]
