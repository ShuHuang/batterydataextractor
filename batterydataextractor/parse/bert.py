# -*- coding: utf-8 -*-
"""
batterydataextractor.parse.bert

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Bert parsers.
author:
"""
import logging
import re
from .base import BaseSentenceParser
from transformers.pipelines import pipeline

log = logging.getLogger(__name__)


class BertParser(BaseSentenceParser):
    """Bert Parser"""

    @staticmethod
    def qa_model(model_name_or_path="batterydata/test1"):
        return pipeline('question-answering', model=model_name_or_path, tokenizer=model_name_or_path)


class BertMaterialParser(BertParser):
    """Bert Material Parser."""

    confidence_threshold = 0.1

    def interpret(self, tokens):
        bert_model = self.qa_model()
        context = " ".join([token[0] for token in tokens])
        for specifier in self.model.defined_names:
            if specifier in context:
                question = "What is the value of {}?".format(specifier)
                qa_input = {'question': question, 'context': context}
                res = bert_model(qa_input, top_k=1)
                if res['score'] > self.confidence_threshold:
                    question2 = "What material has a {} of {}?".format(specifier, res['answer'])
                    qa_input2 = {'question': question2, 'context': context}
                    res2 = bert_model(qa_input2, top_k=1)
                    value = re.findall(r'(?:\d*\.\d+|\d+)', res['answer'])
                    c = self.model(value=[float(v) for v in value],
                                   units=res['answer'].split(value[-1])[-1].strip(),
                                   specifier=specifier,
                                   material=res2['answer']
                                   )
                    yield c


class BertGeneralParser(BertParser):
    """Bert General Parser."""

    confidence_threshold = 0

    def interpret(self, tokens):
        bert_model = self.qa_model()
        context = " ".join([token[0] for token in tokens])
        for specifier in self.model.defined_names:
            question = "What is the {}?".format(specifier)
            qa_input = {'question': question, 'context': context}
            res = bert_model(qa_input, top_k=1)
            if res['score'] > self.confidence_threshold:
                c = self.model(answer=res['answer'],
                               specifier=specifier
                               )
                yield c
