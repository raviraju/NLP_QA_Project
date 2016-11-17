# -*- coding: utf-8 -*-

from nltk.tag import StanfordNERTagger
from nltk.tokenize import word_tokenize

st = StanfordNERTagger('/home/aditya/src/stanfordNER/stanford-NER/classifiers/english.all.3class.distsim.crf.ser.gz',
                       '/home/aditya/src/stanfordNER/stanford-NER/stanford-ner.jar',
                       encoding='utf-8')

#text = 'While in France, Christine Lagarde discussed short-term stimulus efforts in a recent interview with the Wall Street Journal.'
text="Los Angeles John Hallway Kitchen"
tokenized_text = word_tokenize(text)
classified_text = st.tag(tokenized_text)

print(classified_text)
