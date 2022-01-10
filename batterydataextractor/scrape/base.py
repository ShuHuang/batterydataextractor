# -*- coding: utf-8 -*-
"""
batterydataextractor.scrape.base

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Base web-scraper
author: Shu Huang (sh2009@cam.ac.uk)
"""
from transformers import BertTokenizer, BertForSequenceClassification


class BaseWebScraper:
    def __init__(self, model_name_or_path="batterydata/test4"):
        self.model_name_or_path = model_name_or_path

    def classify_paper(self, abstract):
        tokenizer = BertTokenizer.from_pretrained(self.model_name_or_path)
        model = BertForSequenceClassification.from_pretrained(self.model_name_or_path)
        inputs = tokenizer(abstract,  padding=True, truncation=True, return_tensors="pt")
        outputs = model(**inputs)
        probs = outputs[0].softmax(1)
        label = probs.argmax().item()
        return label
