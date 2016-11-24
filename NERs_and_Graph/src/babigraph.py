import networkx as nx
import collections
import json
import io
import os
import sys
import matplotlib.pyplot as plt
import argparse, random
from pycorenlp import StanfordCoreNLP
from Globals import Globals
from networkx.classes.function import neighbors
from babiparser import BabiParser

import espeak
#https://github.com/relsi/python-espeak
male = espeak.ESpeak(amplitude=200, word_gap=-50, pitch=36, speed=200, voice='english-us')
female = espeak.ESpeak(amplitude=200, word_gap=-50, pitch=77, speed=200, voice='english-us')

class BabiGraph():

    def __init__(self, interactive=False, save_graph=False, corenlp=Globals.CORENLP_SERVER):
        self.parser = BabiParser(corenlp)
        self.interactive = interactive
        self.save_graph = save_graph
        self.edgeList = []
        self.nodeList = []
        self.timeStampLemmaDict = dict()
        self.subStoryFacts = dict()
        self.G = nx.Graph()
        self.storyNum = 0
        self.corenlp = StanfordCoreNLP(Globals.CORENLP_SERVER)

    def subStoryCheck(self, fact):
        if (fact == 1):
            if self.interactive:
                print("*************************************************")
                new_story = "All right, Lets start with a new story"
                male.say(new_story)
                print(new_story)
            self.storyNum += 1
            self.G.clear()

    def question(self, subStory):
        print(subStory)
        question = input("\nPlease ask the question based on the above sub-story"+"\n")
        return question

    def analyzeQuestion(self, QDict):
        actorNode = QDict.get("POS_NNP", "actorNode")
        objectLocationNode = QDict.get("POS_NN", "objectLocationNode")
        if self.G.has_node(actorNode):
            return actorNode
        if self.G.has_node(objectLocationNode):
            return objectLocationNode
        # Not Found
        return None

    def getTemplateAns(self, subject, answer, ansType):
        if ansType == "location":
            templates = [subject + " is in the " + answer, subject + " is at " + answer ]
            index = random.randrange(len(templates))
            return templates[index]
        elif ansType == "object":
            templates = [subject + " is at " + answer, subject + " is present in " + answer]
            index = random.randrange(len(templates))
            return templates[index]
        else:
            return "Something went wrong, I cant answer"

    def traverseGraph(self, node, QJsonObj, subject):
        print("Args: ", node, QJsonObj, subject)
        QEdgeAttribute = dict()
        sampleDict = dict()
        allNodes = self.G.nodes()
        if node not in allNodes:
            if self.interactive:
                dont_know = "Sorry, We are not aware of " + subject + ", Hence cant answer the question"
                print(dont_know)
                female.say(dont_know)
            return None
        neigh = self.G.neighbors(node)
        print("neighbors: ", neigh)
        lemmaDict = {}
        locationSet = set(["go", "travel", "journey", "move"])
        locationDict = {}
        objectSet = set(["football", "apple", "milk", "box"])
        objectDict = {}

        for neighborNode in neigh:
            uvEdge = (neighborNode, node)
            u = uvEdge[0]
            v = uvEdge[1]
            QEdgeAttribute.update(self.G.get_edge_data(u, v))
            sampleDict[neighborNode]=self.G.get_edge_data(u, v)
            attributeDict = self.G.get_edge_data(u, v)
            for TS, Lemma in attributeDict.items():
               if Lemma in lemmaDict:
                   lemmaDict[Lemma][TS] = neighborNode
               else:
                   lemmaDict[Lemma] = {TS : neighborNode}
        for lemma in lemmaDict:
            finalResultDict = dict()
            if lemma in locationSet:
                tsKeys = lemmaDict[lemma].keys()
                for ts in tsKeys:
                    location = lemmaDict[lemma][ts]
                    locationDict[ts] = location
                    finalResultDict = locationDict
            if lemma in objectSet:
                tsKeys = lemmaDict[lemma].keys()
                for ts in tsKeys:
                    object = lemmaDict[lemma][ts]
                    objectDict[ts] = location
                    finalResultDict = objectDict
        timeStamps = finalResultDict.keys()
        if self.interactive:
            recollect = "We know that"
            print(recollect)
            female.say(recollect)
            i = 0
            for timeStamp in sorted(timeStamps):
                if i != 0:
                    print("and then")
                    female.say("and then")
                print(str(timeStamp) + " " + self.subStoryFacts[timeStamp])
                female.say(self.subStoryFacts[timeStamp])
                i += 1

        latestTimeStamp = max(timeStamps, key=int)
        answer = finalResultDict[latestTimeStamp]
        if self.interactive:
            print("Hence, we can infer that")
            female.say("Hence, we can infer that")
            template_ans = self.getTemplateAns(subject, answer, "location")
            female.say(template_ans)
            print(template_ans)
        return (answer, QJsonObj, self.storyNum)

    def processQuestion(self, output, que):
        resultDict = {'Sentence': que}
        for sentence in output['sentences']:
            for tok in sentence['tokens']:
                originalText = tok['originalText']
                if(tok['pos'] == 'VBD' or tok['pos'] == 'VB' or tok['pos'] == 'VBG' or tok['pos'] == 'VBN'or tok['pos'] == 'VBP'or tok['pos'] == 'VBZ'):
                    resultDict['POS_Verb'] = originalText
                    resultDict['Lemma_Verb'] = tok['lemma']
                elif(tok['pos'] == 'NNP'):
                    resultDict['POS_NNP'] = originalText
                elif(tok['pos'] == 'NN'):
                    resultDict['POS_NN'] = originalText
                elif(tok['pos'] == 'WRB' or tok['pos']=='WP'):
                    resultDict['WHQ'] = originalText
        return resultDict

    def displayGraph(self):
        nx.draw(self.G, with_labels=True)
        plt.show()

    def saveGraph(self, name):
        if not self.save_graph:
            return
        plt.clf()
        if self.storyNum < 25:
            nx.draw(self.G, with_labels=True)
            dirName = str(self.storyNum)
            dirName = os.path.join(Globals.IMAGE_DIR, dirName)
            if not os.path.exists(dirName):
                os.makedirs(dirName)
            fName = name
            plt.savefig(dirName + "/" + fName + ".png")

    def update_story(self, ann_line):
        timestamp = ann_line['SNO']
        sentence = ann_line["Sentence"]
        if self.interactive:
            print("\t\t" + str(timestamp) + " " + sentence)
            male.say(sentence)
        node1 = ann_line["POS_NN"]
        node2 = ann_line["POS_NNP"]
        lemma = ann_line["Lemma_Verb"]
        edgeAttribute = dict()
        edgeAttribute[timestamp] = lemma
        edge = (node1, node2, edgeAttribute)
        self.subStoryFacts[timestamp] = sentence
        self.G.add_node(node1) #,color='red',style='filled',fillcolor='blue',shape='square'
        self.G.add_node(node2)
        self.G.add_edge(node1, node2, edgeAttribute)
        self.saveGraph(str(timestamp))

    def answer_question(self, ann_line):
        timestamp = ann_line["SNO"]
        question = ann_line["Sentence"]
        if self.interactive:
            prompt_msg = "Do you want me to answer the question"
            female.say(prompt_msg)
            print(question)
            female.say(question)
            choice = input(prompt_msg + " (yes/no)\n")
            if choice == "no":
                ask_user_question = "What other question would you like me to answer"
                female.say(ask_user_question)
                question = input(ask_user_question + "\n")
                lookup_response = "Let me think"
                print(lookup_response)
                female.say(lookup_response)
                annotated = self.parser.annotate(question)
                ann_line = self.processQuestion(annotated, question)

        #subject = ann_line["POS_NNP"]
        QNode = self.analyzeQuestion(ann_line)
        return self.traverseGraph(QNode, ann_line, QNode)

    def play(self, in_file, out_file=None):
        with io.open(in_file) as data_file:
            for ann_line in map(json.loads, data_file):
                self.subStoryCheck(ann_line['SNO'])
                if ann_line["isFact"]:
                    self.update_story(ann_line)
                else:
                    yield self.answer_question(ann_line)
                    if self.interactive:
                        prompt_msg = "Do you want me to continue with some more facts"
                        male.say(prompt_msg)
                        choice = input(prompt_msg + "? (yes/no)\n")
                        if choice == "no":
                            break
                if self.interactive:
                    self.displayGraph()

    def write_results(self, answers, out_file):
        count = 0
        with open(out_file, "a+") as fp:
            for ans, quest, story_num in answers:
                count += 1
                rec = "%d\t%s" % (story_num, ans)
                if 'answer' in quest:
                    rec += "\t%s" % quest['answer']
                if 'supportingFactNos' in quest:
                    rec += "\t%s" % ','.join(map(str, quest['supportingFactNos']))
                fp.write(rec)
                fp.write("\n")
        print("Wrote %d records to %s" % (count, out_file))

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
                description="construct graph from facts of a babi-task and answer questions",
                formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("-i", "--interactive", help="enable interactive user mode", action="store_true")
    parser.add_argument("-in", "--input", help="Input file", default=Globals.NERTEXT_FILE)
    parser.add_argument("-im", "--images", help="Input file", default=Globals.IMAGE_DIR)
    parser.add_argument("-o", "--out", help="Output file", default=Globals.RESULTS_FILE)

    args = parser.parse_args()
    bg = BabiGraph(args.interactive)
    results = bg.play(args.input)
    bg.write_results(results, args.out)
