import sys
import io
import re
import os
import collections
import json
import argparse
from pycorenlp import StanfordCoreNLP

class BabiParser(object):

    def __init__(self, corenlp_url):
        self.corenlp = StanfordCoreNLP(corenlp_url)
        self.props = {'annotators': 'tokenize,ssplit,pos,lemma',
                      'outputFormat': 'json'}

    def annotate(self, text):
        if type(text) != str:
            text = text.encode('ascii')
        return self.corenlp.annotate(text, properties=self.props)

    def parseQuestion(self, line):
        questionList = line.split('\t')
        sNo_question = questionList[0]
        sNo_questionList = sNo_question.split(' ')
        sNo = sNo_questionList[0]
        del sNo_questionList[0]
        question = ' '.join(sNo_questionList)
        output = self.annotate(question)
        answer = questionList[1]
        suppFactNos = list(map(int, questionList[2].strip().split()))
        return self.parseOutput(sNo, question, output, False, answer, suppFactNos)

    def parseFact(self, line):
        tokens = line.strip().split()
        sNo = tokens[0]
        del tokens[0]
        fact = ' '.join(tokens)
        output = self.annotate(fact)
        return self.parseOutput(sNo, fact, output, True)

    def readInput(self, path):
        print("Files are being read and tokenized ...")
        with io.open(path, "r") as f:
            for line in f:
                if '\t' in line:
                    yield self.parseQuestion(line)
                else:
                    yield self.parseFact(line)

    def parseOutput(self, sNo, textLine, output, isFact, answer=None, supportingFactNos=None):
        resultDict = {'sentence': textLine}
        sentences = output['sentences']
        assert len(sentences) == 1  # one sentence at a time
        sentence = sentences[0]
        tokens = sentence['tokens']
        resultDict['sNo'] = int(sNo)
        resultDict['isFact'] = isFact

        # nouns = list(filter(lambda x: x['pos'].startswith('NN'), tokens))
        # # fact has 2 nouns, question has atleast one noun
        # assert (isFact and len(nouns) == 2) or (
        #     not isFact and 1 <= len(nouns) <= 2)

        # # first one is subject
        # resultDict['_subject'] = nouns[0]['originalText'] #POS_NNP
        # if len(nouns) > 1:  # last one is Object
        #     resultDict['_object'] = nouns[-1]['originalText'] #POS_NN

        # search for verbs
        verbs = list(filter(lambda x: x['pos'].startswith('VB'), tokens))
        assert len(verbs) == 1  # check that one and only one verb exists
        # resultDict['_verb'] = verbs[0]['lemma']

        for tok in sentence['tokens']:
            originalText = tok['originalText']
            if answer:
                resultDict['answer'] = answer
            if supportingFactNos:
                resultDict['supportingFactNos'] = supportingFactNos
            if(tok['pos'].startswith('VB')):
                resultDict['verb'] = originalText
                resultDict['posVerb'] = tok['pos']
                resultDict['lemmaVerb'] = tok['lemma']
            elif(tok['pos'] == 'NNP'):
                resultDict['posNNP'] = originalText
            elif(tok['pos'] == 'NN'):
                resultDict['posNN'] = originalText
            elif(tok['pos'] in ('WRB', 'WP')):
                resultDict['posWHQ'] = originalText

        if not isFact:
            if 'posWHQ' in resultDict:
                resultDict['expectedAnsType'] = "WHERE"  # Where
            else:
                resultDict['expectedAnsType'] = "YESNO"  # Yes No
        return resultDict

def dump_as_jsonlines(records, outpath):
    with open(outpath, 'w') as out:
        for rec in records:
            out.write(json.dumps(rec))
            out.write('\n')

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Babi Tasks Parser')
    parser.add_argument('-c', '--corenlp', help='CoreNLP Server URL',
                        default='http://localhost:9000', required=False)
    parser.add_argument(
        '-o', '--out', help='Path to output file to store JSON Line', required=True)
    parser.add_argument(
        '-i', '--in', help='Input path of babi task file', required=True)
    args = vars(parser.parse_args())

    records = BabiParser(args['corenlp']).readInput(args['in'])
    dump_as_jsonlines(records, args['out'])
    print("Done")
