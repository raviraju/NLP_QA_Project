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
import time
# TODO: make this optional
import espeak
#https://github.com/relsi/python-espeak
female = espeak.ESpeak(amplitude=200, word_gap=-50, pitch=36, speed=220, voice='en-us')
male = espeak.ESpeak(amplitude=200, word_gap=-50, pitch=80, speed=220, voice='en-us+f4')

class ActionClassifier(object):

    def __init__(self, input_action, model=None):
        # Label -> set of Actions
        with open(input_action,'r') as annotatedActions:
            actions = json.load(annotatedActions)
            actionsDict = {}
            for actionClass in actions:
                actionsDict[actionClass] = set(actions[actionClass])
            self.model = model if model else actionsDict
            #{
                #'attach': set(['get', 'grab', 'pick', 'take']),
                #'detach': set(['discard', 'drop', 'leave', 'put']),
                #'transport': set(['go', 'journey', 'move', 'travel'])
            #}

    def classify(self, action):
        for label, terms in self.model.items():
            if action in terms:
                return label
        raise Exception("Haven't learnt this action : %s" % action)

    def classes(self):
        return self.model.keys()

class BabiGraph(object):
    def __init__(self, interactive=False,
                save_graph=False,
                int_graph=False,
                interactive_delay = 0,
                corenlp=Globals.CORENLP_SERVER,
                input_action=""):
        self.parser = BabiParser(corenlp)
        self.interactive = interactive
        self.interactive_delay = interactive_delay
        self.int_graph = int_graph
        self.subStoryFacts = {}
        self.G = nx.Graph()
        self.storyNum = 0
        self.action_clsfr = ActionClassifier(input_action)

    def subStoryCheck(self, fact):
        if (fact == 1):
            if self.interactive:
                print("*************************************************")
                new_story = "All right, Lets start with a new story"
                male.say(new_story)
                print(new_story)
            self.storyNum += 1
            self.G.clear()
            self.subStoryFacts = {}

    def question(self, subStory):
        print(subStory)
        question = input("\nPlease ask the question based on the above sub-story"+"\n")
        return question

    def analyzeQuestion(self, QDict):
        actorNode = QDict.get("POS_NNP", "actorNode")
        objectLocationNode = QDict.get("POS_NN", "objectLocationNode")
        if self.G.has_node(actorNode):
            return actorNode, True
        if self.G.has_node(objectLocationNode):
            return objectLocationNode, False
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

    def find_recent_neighbor(self, node):
        # node exists
        if node in self.G:
            neighbors = self.G[node]
            rec_time = -1
            rec_neigh = None
            rec_action = None
            for neigh, edge_data in neighbors.items():
                n_time = max(edge_data.keys()) # keys has timestamp
                if n_time > rec_time:
                    rec_time = n_time
                    rec_neigh = neigh
                    rec_action = edge_data[rec_time]
            assert rec_neigh is not None
            return rec_time, rec_action, rec_neigh
        else:
            raise Exception('%s not known' % str(node))

    def traverseGraph(self, node, QJsonObj, is_actor):
        # print("Args: ", node, QJsonObj, is_actor)
        subject = node
        reasons = {}
        if node not in self.G:
            if self.interactive:
                dont_know = "Sorry, We are not aware of " + node + ", Hence cant answer the question"
                print(dont_know)
                female.say(dont_know)
            return None

        neigh = self.G.neighbors(node)
        oldest_mem_no = float('-inf') # oldest memory for search
        newest_mem_no = float('inf')  # newest memory for search
        if not is_actor:
            # find recent actor and time
            ts, action, node = self.find_recent_neighbor(node)
            # print(">>", ts, action, node)
            a_type = self.action_clsfr.classify(action)
            if a_type == 'attach':
                #oldest_mem_no = ts
                pass
            elif a_type == 'detach':
                newest_mem_no = ts
            else:
                raise Exception("This shouldnt be happening!")
            reasons[ts] = self.subStoryFacts[ts]
            # find recent neighbors of actor
            neigh = self.G.neighbors(node)

        lemmaDict = {}
        for neighborNode in neigh:
            uvEdge = (neighborNode, node)
            u = uvEdge[0]
            v = uvEdge[1]
            attributeDict = self.G.get_edge_data(u, v)
            for TS,Lemma in attributeDict.items():
               if Lemma in lemmaDict:
                   lemmaDict[Lemma][TS] = neighborNode
               else:
                   lemmaDict[Lemma] = {TS : neighborNode}

        # find location connecting edges
        location_edges = list(filter(lambda action: self.action_clsfr.classify(action) == 'transport', lemmaDict.keys()))
        candidates = {}
        for lemma in location_edges:
            edges = lemmaDict[lemma]
            for ts, node in edges.items():
                candidates[ts] = node
        timeStamps = candidates.keys()

        timeStamps = list(filter(lambda x: oldest_mem_no <= x <= newest_mem_no, timeStamps))
        if not timeStamps:
            print("ERROR: Insufficient data or wrong question")
            return None
        if self.interactive:
            for ts in timeStamps:
                reasons[ts] = self.subStoryFacts[ts]
            recollect = "We know that"
            print(recollect)
            female.say(recollect)
            for i, ts in enumerate(sorted(reasons.keys())):
                if i != 0:
                    print("and then")
                    female.say("and then")
                reason = reasons[ts]
                print("%d %s" % (ts, reason))
                female.say(reason)
                i += 1

        # print("Time Stamps :", timeStamps)
        latestTimeStamp = max(timeStamps, key=int)
        answer = candidates[latestTimeStamp]
        concluded_answer = answer
        # convert answer to binary if expectation is yes no type
        if QJsonObj.get('expAnsType', '') == 'YESNO':
            answer = "yes" if answer == QJsonObj['POS_NN'] else "no"
        if self.interactive:
            print("Hence, we can infer that")
            female.say("Hence, we can infer that")
            template_ans = "Dont Know"
            if QJsonObj.get('expAnsType', '') == 'YESNO':
                respond = "Yes" if concluded_answer == QJsonObj['POS_NN'] else "No"
                person = QJsonObj.get('POS_NNP', 'SomeOne')
                location = QJsonObj.get('POS_NN', 'some where')
                if answer == "no":
                    template_ans = respond + ", " + person + " is not in the " + location
                else:
                    template_ans = respond + ", " + person + " is in the " + location
            else:
                subj_type = "location" if node == subject else "object"
                template_ans = self.getTemplateAns(subject, answer, subj_type)
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
        if self.int_graph:
            plt.clf()
            pos = nx.spring_layout(self.G)
            nx.draw(self.G, pos, with_labels=True)
            nx.draw_networkx_edge_labels(self.G, pos)
            plt.show()
            time.sleep(self.interactive_delay)

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
        QNode, is_actor = self.analyzeQuestion(ann_line)
        return self.traverseGraph(QNode, ann_line, is_actor)

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
    parser.add_argument("-ig", "--graph", help="enable interactive Graph", action="store_true")
    parser.add_argument("-in", "--input", help="Input file", default=Globals.NERTEXT_FILE)
    parser.add_argument("-ia", "--input_action", help="Input file action annotated verbs", default=Globals.ANNOTATE_ACTIONS)
    parser.add_argument("-o", "--out", help="Output file", default=Globals.RESULTS_FILE)

    args = parser.parse_args()
    bg = BabiGraph(args.interactive, int_graph=args.graph, input_action=args.input_action)
    results = bg.play(args.input)
    bg.write_results(results, args.out)
