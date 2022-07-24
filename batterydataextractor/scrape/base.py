# -*- coding: utf-8 -*-
"""
batterydataextractor.scrape.base

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Base web-scraper
"""
from transformers import BertTokenizer, BertForSequenceClassification


class BaseWebScraper:
    """
    Base web-scraper.
    """
    def __init__(self, model_name_or_path="batterydata/batteryscibert-uncased-abstract"):
        """
        :param model_name_or_path: the BERT model to classify battery paper abstract. (Not required)
        """
        self.model_name_or_path = model_name_or_path
        self.tokenizer = BertTokenizer.from_pretrained(self.model_name_or_path)
        self.model = BertForSequenceClassification.from_pretrained(self.model_name_or_path)

    def classify_paper(self, abstract):
        """
        Battery or non-battery paper classifier
        :param abstract: abstract text from a scientific paper
        :return: predicted label. (0: non-battery paper; 1: battery paper)
        """
        inputs = self.tokenizer(abstract,  padding=True, truncation=True, max_length=512, return_tensors="pt")
        outputs = self.model(**inputs)
        probs = outputs[0].softmax(1)
        label = probs.argmax().item()
        return label
