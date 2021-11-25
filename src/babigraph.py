import networkx as nx
import collections
import json
import io
import os
import sys
import matplotlib.pyplot as plt
import argparse
import random
from pycorenlp import StanfordCoreNLP

from babiparser import BabiParser
import time

# TODO: make this optional
# import espeak
# https://github.com/relsi/python-espeak
# female = espeak.ESpeak(amplitude=200, word_gap=-50, pitch=36, speed=220, voice='en-us')
# male = espeak.ESpeak(amplitude=200, word_gap=-50, pitch=80, speed=220, voice='en-us+f4')

class ActionClassifier(object):

    def __init__(self, annotatedClustersFile, model=None):
        # actionClass -> set of Actions
        with open(annotatedClustersFile, 'r') as annotatedActions:
            actions = json.load(annotatedActions)
            actionsDict = dict()
            for actionClass in actions:
                actionsDict[actionClass] = set(actions[actionClass])
            self.model = model if model else actionsDict
            # {
            # 'attach': set(['get', 'grab', 'pick', 'take']),
            # 'detach': set(['discard', 'drop', 'leave', 'put']),
            # 'transport': set(['go', 'journey', 'move', 'travel'])
            # }

    def classify(self, action):
        for actionClass, actions in self.model.items():
            if action in actions:
                return actionClass
        raise Exception("Haven't learnt this action : %s" % action)

    def classes(self):
        return self.model.keys()

class BabiGraph(object):
    def __init__(self, interactive=False,
                 debug=False,
                 saveGraph=False,
                 interactiveDelay=1,
                 corenlp="http://localhost:9000",
                 annotatedClustersFile=""):
        self.parser = BabiParser(corenlp)
        self.interactive = interactive
        self.debug = debug
        self.interactiveDelay = interactiveDelay
        self.factsDict = dict()
        self.G = nx.Graph()
        self.noOfStories = 0
        self.actionClassifier = ActionClassifier(annotatedClustersFile)

    def newStoryCheck(self, timeStamp):
        if (timeStamp == 1):
            if self.interactive:
                print("*************************************************")
                newStory = "All right, Lets start with a new story"
                # male.say(newStory)
                print(newStory)
            self.noOfStories += 1
            self.G.clear()
            self.factsDict = dict()

    def question(self, subStory):
        print(subStory)
        question = input(
            "\nPlease ask the question based on the above sub-story"+"\n")
        return question

    def analyzeQuestion(self, questionDict):
        isActor = None
        questionNode = None

        actorNode = questionDict.get("posNNP", "actorNode")
        objectLocationNode = questionDict.get("posNN", "objectLocationNode")
        if self.G.has_node(actorNode):
            isActor = True
            questionNode = actorNode
            return questionNode, isActor
        if self.G.has_node(objectLocationNode):
            isActor = False
            questionNode = objectLocationNode
            return questionNode, isActor
        # Not Found
        return questionNode, isActor

    def getTemplateAns(self, subject, answer, ansType):
        if ansType == "location":
            templates = [subject + " is in the " + answer,
                         subject + " is at " + answer]
            index = random.randrange(len(templates))
            return templates[index]
        elif ansType == "object":
            templates = [subject + " is at " + answer,
                         subject + " is present in " + answer]
            index = random.randrange(len(templates))
            return templates[index]
        else:
            return "Something went wrong, I cant answer"

    def findRecentActorNeighbour(self, objectLocationNode):
        neighbours = self.G[objectLocationNode]
        if self.debug:
            print("objectLocationNode : ", objectLocationNode)
            print("neighbours : ", neighbours)
        recentTimeStamp = -1
        recentActorNeighbourNode = None
        recentAction = None
        for neighbour, edgeDict in neighbours.items():
            latestTimeStamp = max(edgeDict.keys())  # keys has timestamp
            if latestTimeStamp > recentTimeStamp:
                recentTimeStamp = latestTimeStamp
                recentActorNeighbourNode = neighbour
                recentAction = edgeDict[recentTimeStamp]
        if self.debug:
            print("findRecentActorNeighbour : ", recentTimeStamp, recentAction, recentActorNeighbourNode)
        return recentTimeStamp, recentAction, recentActorNeighbourNode

    def traverseGraph(self, questionDict):
        questionNode, isActor = self.analyzeQuestion(questionDict)
        if self.debug:
            print("questionDict : ", questionDict)
            print("questionNode : ", questionNode, " isActor : ", isActor)

        subject = questionNode
        reasonsDict = dict()
        supportingTimeStamps = []
        if questionNode not in self.G:
            if self.interactive:
                dont_know = "Sorry, We are not aware of " + questionNode + ", Hence cant answer the question"
                print(dont_know)# female.say(dont_know)
            return None

        oldestLocationTimeStamp = float('-inf')  # oldest memory for search
        newestLocationTimeStamp = float('inf')   # newest memory for search
        if not isActor: #objectLocationNode
            # find recent actor and time
            recentTimeStamp, recentAction, recentNeighbourNode = self.findRecentActorNeighbour(questionNode)
            # print(">>", recentTimeStamp, recentAction, recentNeighbourNode)
            actionClass = self.actionClassifier.classify(recentAction)
            if actionClass == 'attach':
                oldestLocationTimeStamp = recentTimeStamp
            elif actionClass == 'detach':
                newestLocationTimeStamp = recentTimeStamp
            else:
                raise Exception("This shouldnt be happening!")
            reasonsDict[recentTimeStamp] = self.factsDict[recentTimeStamp]
            supportingTimeStamps.append(recentTimeStamp)

            actorNode = recentNeighbourNode
        else:#actorNode
            actorNode = questionNode

        # find neighbours of actor
        neighboursActor = self.G[actorNode]
        if self.debug:
            print("neighbours of actor(" + actorNode +") : ", neighboursActor)

        verbDict = dict()
        for neighbourActor in neighboursActor:
            uvEdge = (neighbourActor, actorNode)
            u = uvEdge[0]
            v = uvEdge[1]
            attributeDict = self.G.get_edge_data(u, v)
            for timeStamp, verb in attributeDict.items():
                if verb in verbDict:
                    verbDict[verb][timeStamp] = neighbourActor
                else:
                    verbDict[verb] = {timeStamp: neighbourActor}
        if self.debug:
            print("verbDict : ", verbDict)

        # find location connecting edges
        locationEdges = list(filter(lambda action: self.actionClassifier.classify(action) == 'transport', verbDict.keys()))
        if self.debug:
            print("locationEdges : ", locationEdges)
        locationNodesDict = dict()
        for verb in locationEdges:
            edges = verbDict[verb]
            for timeStamp, node in edges.items():
                locationNodesDict[timeStamp] = node
        if self.debug:
            print("locationNodesDict : ", locationNodesDict)

        locationTimeStamps = locationNodesDict.keys()
        if self.debug:
            print("locationTimeStamps : ", locationTimeStamps)
            print("oldestLocationTimeStamp : ", oldestLocationTimeStamp, " newestLocationTimeStamp : ", newestLocationTimeStamp)
        filteredLocationTimeStamps = list(filter(lambda x: oldestLocationTimeStamp <= x <= newestLocationTimeStamp, locationTimeStamps))
        if self.debug:
            print("filteredLocationTimeStamps : ", filteredLocationTimeStamps)
        if not filteredLocationTimeStamps:
            print("ERROR: Insufficient data or wrong question")
            return None
        if self.interactive:
            for timeStamp in filteredLocationTimeStamps:
                reasonsDict[timeStamp] = self.factsDict[timeStamp]
            recollect = "We know that"
            print(recollect)# female.say(recollect)
            for i, timeStamp in enumerate(sorted(reasonsDict.keys())):
                if i != 0:
                    print("\t" + "and then")# female.say("and then")
                reason = reasonsDict[timeStamp]
                print("\t" + "%d %s" % (timeStamp, reason))# female.say(reason)
                i += 1

        latestTimeStamp = max(filteredLocationTimeStamps, key=int)
        supportingTimeStamps.append(latestTimeStamp)
        if self.debug:
            print("latestTimeStamp : ", latestTimeStamp)

        answer = locationNodesDict[latestTimeStamp]
        supportingTimeStamps = sorted(supportingTimeStamps)
        if self.debug:
            print("predicted answer : ", answer, "supportingTimeStamps : ", supportingTimeStamps)
            # input()

        if self.interactive:
            print("Hence, we can infer that")# female.say("Hence, we can infer that")
            template_ans = "Dont Know"
            if questionDict.get('expectedAnsType', '') == 'YESNO':
                respond = "Yes" if answer == questionDict['posNN'] else "No"
                person = questionDict.get('posNNP', 'SomeOne')
                location = questionDict.get('posNN', 'some where')
                if respond == "No":
                    template_ans = respond + ", " + person + " is not in the " + location + ". But present in " + answer
                else:
                    template_ans = respond + ", " + person + " is in the " + location
                print("\t" + template_ans) #female.say(template_ans)
            else:
                subj_type = "location" if node == subject else "object"
                template_ans = self.getTemplateAns(subject, answer, subj_type)
                print("\t" + template_ans) #female.say(template_ans)

        if questionDict.get('expectedAnsType', '') == 'YESNO':
            # convert answer to binary if expectation is yes no type
            answer = "yes" if answer == questionDict['posNN'] else "no"

        return {
            "story_no" : self.noOfStories,
            "pred_answer" : answer,
            "pred_supportingFacts" : supportingTimeStamps,
            "act_answer" : questionDict['answer'] if 'answer' in questionDict else 'unknown',
            "act_supportingFacts" : sorted(questionDict['supportingFactNos']) if 'supportingFactNos' in questionDict else []
        }

    def processQuestion(self, question):
        annotated = self.parser.annotate(question)
        questionDict = {'sentence': question}
        for sentence in annotated['sentences']:
            for tok in sentence['tokens']:
                originalText = tok['originalText']
                # if(tok['pos'] == 'VBD' or tok['pos'] == 'VB' or tok['pos'] == 'VBG' or tok['pos'] == 'VBN'or tok['pos'] == 'VBP'or tok['pos'] == 'VBZ'):
                if tok['pos'].startswith('VB'):
                    questionDict['verb'] = originalText
                    questionDict['posVerb'] = tok['pos']
                    questionDict['lemmaVerb'] = tok['lemma']
                elif(tok['pos'] == 'NNP'):
                    questionDict['posNNP'] = originalText
                elif(tok['pos'] == 'NN'):
                    questionDict['posNN'] = originalText
                elif(tok['pos'] in ('WRB', 'WP')):
                    questionDict['posWHQ'] = originalText
                    questionDict['expectedAnsType'] = "WHERE"  # Where
                else:
                    questionDict['expectedAnsType'] = "YESNO"  # Yes No
        return questionDict

    def displayGraph(self, save=False):
        plt.clf()
        # pos = nx.spring_layout(self.G)
        # pos = nx.shell_layout(self.G)
        pos = nx.planar_layout(self.G)
        nx.draw_networkx(self.G, pos, with_labels=True)
        nx.draw_networkx_edge_labels(self.G, pos)
        plt.show(block=False)
        plt.pause(self.interactiveDelay)
        if save:
            plt.savefig('latest.png')
        plt.close()

    def updateStory(self, parsedLinesDict):
        timestamp = parsedLinesDict["sNo"]
        fact = parsedLinesDict["sentence"]
        if self.interactive:
            print("\t" + str(timestamp) + " " + fact)
            # male.say(fact)
        node1 = parsedLinesDict["posNN"]
        node2 = parsedLinesDict["posNNP"]
        verb = parsedLinesDict["verb"]
        edgeAttributeDict = dict()
        edgeAttributeDict[timestamp] = verb
        # edge = (node1, node2, edgeAttributeDict)
        # print(edge)
        self.factsDict[timestamp] = fact
        # ,color='red',style='filled',fillcolor='blue',shape='square'
        self.G.add_node(node1)
        self.G.add_node(node2)
        self.G.add_edge(node1, node2)
        self.G[node1][node2].update(edgeAttributeDict)

    def answerQuestion(self, questionDict):
        # timestamp = questionDict["sNo"]
        question = questionDict["sentence"]
        if self.interactive:
            prompt_msg = "Now the question is"
            print(prompt_msg)# female.say(prompt_msg)
            print("\t" + question)# female.say(question)
            self.displayGraph(save=True)
            choice = input("Do you want me to answer the question (yes/no)\n")
            if choice == "no":
                ask_user_question = "What other question would you like me to answer"
                # print(ask_user_question)# female.say(ask_user_question)
                question = input(ask_user_question + "\n\t")
                lookup_response = "Let me think..."
                print(lookup_response)# female.say(lookup_response)
                questionDict = self.processQuestion(question)

        return self.traverseGraph(questionDict)

    def play(self, parsedFile):
        with io.open(parsedFile) as data_file:
            for parsedLinesDict in map(json.loads, data_file):
                self.newStoryCheck(parsedLinesDict["sNo"])
                if parsedLinesDict["isFact"]:
                    self.updateStory(parsedLinesDict)
                else:
                    yield self.answerQuestion(parsedLinesDict)
                    if self.interactive:
                        prompt_msg = "Do you want me to continue with some more stories"
                        # print(prompt_msg)# male.say(prompt_msg)
                        choice = input(prompt_msg + "? (yes/no)\n")
                        if choice == "no":
                            break
                if self.interactive:
                    self.displayGraph()

    def writeResultsTxt(self, answers, out_file):
        count = 0
        with open(out_file, "a+") as fp:
            for answer, supportingTimeStamps, questionDict, story_num in answers:
                count += 1
                rec = "%d\t%s" % (story_num, answer)
                rec += "\t%s" % ','.join(map(str, supportingTimeStamps))

                if 'answer' in questionDict:
                    rec += "\t%s" % questionDict['answer']
                if 'supportingFactNos' in questionDict:
                    rec += "\t%s" % ','.join(map(str, sorted(questionDict['supportingFactNos'])))
                fp.write(rec)
                fp.write("\n")
        print("Wrote %d records to %s" % (count, out_file))

    def writeResults(self, results, out_file):
        count = 0
        with open(out_file, "a+") as fp:
            for result in results:
                fp.write(json.dumps(result))
                fp.write('\n')
                count += 1
        print("Wrote %d records to %s" % (count, out_file))

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="construct graph from facts of a babi-task and answer questions",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("-i", "--interactive",
                        help="enable interactive user mode", action="store_true")
    parser.add_argument("-d", "--debug",
                        help="enable debug mode", action="store_true")
    parser.add_argument("parsedFile", help="path to parsed json lines file")
    parser.add_argument("annotatedClustersFile", help="path to annotated clusters json file")
    parser.add_argument("-o", "--out", help="Output file")

    args = parser.parse_args()
    bg = BabiGraph(args.interactive,
                   args.debug,
                   annotatedClustersFile=args.annotatedClustersFile)
    results = bg.play(args.parsedFile)
    bg.writeResults(results, args.out)
