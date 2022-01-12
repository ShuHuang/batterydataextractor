# -*- coding: utf-8 -*-
"""
batterydataextractor.scrape.__init__

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Web-scrapers from publishers including RSC, Elsevier, and Springer
author: Shu Huang (sh2009@cam.ac.uk)
"""
from .base import BaseWebScraper
from .rsc import RSCWebScraper
from .elsevier import ElsevierWebScraper
from .springer import SpringerMetaWebScraper, SpringerTDMWebScraper
