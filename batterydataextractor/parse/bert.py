# -*- coding: utf-8 -*-
"""
batterydataextractor.parse.bert

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Bert parsers.
author:
"""
import logging
from .base import BaseSentenceParser
from transformers.pipelines import pipeline

log = logging.getLogger(__name__)


class BertParser(BaseSentenceParser):
    """Bert Parser."""

    @staticmethod
    def qa_model(model_name_or_path="batterydata/test1"):
        return pipeline('question-answering', model=model_name_or_path, tokenizer=model_name_or_path)

    def interpret(self, tokens):
        bert_model = self.qa_model()
        context = " ".join([token[0] for token in tokens])
        for specifier in self.model.defined_names:
            if specifier in context:
                question = "What is the value of {}?".format(specifier)
                qa_input = {'question': question, 'context': context}
                res = bert_model(qa_input, top_k=1)
                if res['score'] > 0:
                    c = self.model(value=res['answer'],
                                   specifier=specifier
                                   )
                    yield c
