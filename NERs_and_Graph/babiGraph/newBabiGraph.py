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

import espeak
#https://github.com/relsi/python-espeak
male = espeak.ESpeak(amplitude=200, word_gap=-50, pitch=36, speed=200, voice='english-us')
female = espeak.ESpeak(amplitude=200, word_gap=-50, pitch=77, speed=200, voice='english-us')

#male.say("John moved to the office")
#female.say("Sandra journeyed to the bathroom")
#female.say("Mary moved to the hallway")
#male.say("Daniel travelled to the office")
#female.say("John went back to the garden")
#male.say("John moved to the bedroom")

class babiGraph():
    def __init__(self):
        self.edgeList=[]
        self.nodeList=[]
        self.timeStampLemmaDict = dict()
        self.subStoryFacts = dict()
        self.G=nx.Graph()
        self.storyNum=0
        self.corenlp = StanfordCoreNLP(Globals.CORENLP_SERVER)
    def subStoryCheck(self,fact, interactive):
        if(fact == "1"):
            #print("SUBSTORY BLOCK")
            #print("New Story Detected")
            #print("The Following graph is for this substory and it will be cleared. ")
            if interactive:
                print("*************************************************")
                new_story = "All right, Lets start with a new story"
                male.say(new_story)
                print(new_story)
            self.storyNum+=1
            #q = input("\nEnter q to clear graph"+"\n")
            #if(q is "q"):
            #self.displayGraph()
            self.G.clear()
           
    def question(self,subStory):
        print(subStory)
        question = input("\nPlease ask the question based on the above sub-story"+"\n")
        return question       
    def annotateQuestion(self,quest):
        props = { 'annotators': 'tokenize,ssplit,pos,lemma', 'outputFormat': 'json'}
        output = self.corenlp.annotate(quest, properties=props)
        return output
    def analyzeQuestion(self,QDict):
        verb=QDict["POS_Verb"]
        WHQ=QDict["WHQ"]
        actorNode=QDict.get("POS_NNP","actorNode")
        objectLocationNode=QDict.get("POS_NN","objectLocationNode")
        lemma=str(QDict["Lemma_Verb"])
        if(self.G.has_node(actorNode)):
            return actorNode
        else:
            pass
        if(self.G.has_node(objectLocationNode)):
            return objectLocationNode
        else:
            pass
    def writeResults(self,ans,QJSON,TS):
        QJSON['PANS']=ans
        QJSON['PSUPPFACT']=TS
        with open(Globals.OUTPUT_GRAPH_FILE, "a+") as textFile:
            json.dump(QJSON,textFile)
            textFile.write("\n")
        pass
    
    def getTemplateAns(self, subject,answer,ansType):
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

    def traverseGraph(self,node,QJsonObj, interactive, subject):
        QEdgeAttribute = dict()
        sampleDict=dict()
        allNodes = self.G.nodes()
        if node not in allNodes:
            self.writeResults("Dont Know", {}, -1)
            if interactive:
                dont_know = "Sorry, We are not aware of " + subject + ", Hence cant answer the question"
                female.say(dont_know)
                print(dont_know)
            return
        neigh = self.G.neighbors(node)
        lemmaDict = {}
        locationSet = set(["go","travel","journey","move"])
        locationDict = {}
        objectSet = set(["football","apple","milk","box"])
        objectDict = {}
        
        for neighborNode in neigh:
            uvEdge=(neighborNode,node)
            u=uvEdge[0]
            v=uvEdge[1]
            QEdgeAttribute.update(self.G.get_edge_data(u, v))
            sampleDict[neighborNode]=self.G.get_edge_data(u, v)
            attributeDict = self.G.get_edge_data(u, v)
            for TS,Lemma in attributeDict.items():
               if Lemma in lemmaDict:
                   lemmaDict[Lemma][TS] = neighborNode
               else:
                   lemmaDict[Lemma] = {TS : neighborNode}
        #print(lemmaDict)
        #differenciate bw lemmas
        for lemma in lemmaDict:
            finalResultDict=dict()
            if lemma in locationSet:
                tsKeys = lemmaDict[lemma].keys()
                for ts in tsKeys:
                    location = lemmaDict[lemma][ts]
                    locationDict[ts] = location
                    finalResultDict=locationDict
            if lemma in objectSet:
                tsKeys = lemmaDict[lemma].keys()
                for ts in tsKeys:
                    object = lemmaDict[lemma][ts]
                    objectDict[ts] = location
                    finalResultDict=objectDict
        timeStamps = finalResultDict.keys()
        if interactive:
            recollect = "We know that"
            print(recollect)
            female.say(recollect)
            i = 0
            for timeStamp in sorted([int(timeStamp) for timeStamp in timeStamps]):
                if i != 0:
                    print("and then")
                    female.say("and then")
                str_timeStamp = str(timeStamp)
                print(str_timeStamp + " " + self.subStoryFacts[str_timeStamp])
                female.say(self.subStoryFacts[str_timeStamp])
                i += 1
        latestTimeStamp = max(timeStamps, key=int)
        answer = finalResultDict[latestTimeStamp]
        #print(answer,QJsonObj,latestTimeStamp)
        if interactive:
            print("Hence, we can infer that")
            female.say("Hence, we can infer that")
            template_ans = self.getTemplateAns(subject, answer, "location")
            female.say(template_ans)
            print(template_ans)

        self.writeResults(answer, QJsonObj, latestTimeStamp)
        #lemmaChoice = input("Enter lemma type : {}\n".format(lemmaDict))
        #choices = lemmaDict.get(lemmaChoice,None)
        #print(choices)
        #if choices:
        #    timeStamps = choices.keys()
        #    latestTimeStamp = max(timeStamps, key=int)
            #print("Answer is " + choices[latestTimeStamp])
        #    print(question+"\t"+choices[latestTimeStamp]+"\t"+str(latestTimeStamp))
    def processQuestion(self,output,que):
        originalText = ""
        resultDict = dict()
        #print("Question asked is " +que )
        #self.displayGraph()
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
        nx.draw(self.G,with_labels=True)
        plt.show()
    def saveGraph(self,name):
        plt.clf()
        if self.storyNum < 25:
#             self.G.node[qNode]['color']='blue'
#             pos = nx.spring_layout(self.G)
#             nx.draw_networkx_nodes(self.G, pos=pos, nodelist = self.G.nodes())
#             nx.draw_networkx_edges(self.G, pos=pos, edgelist = self.G.edges())
#             nx.draw_networkx_labels(self.G, pos=pos)
            nx.draw(self.G,with_labels=True)
            dirName=str(self.storyNum)
            dirName=os.path.join(Globals.IMAGE_DIR, dirName)
            if not os.path.exists(dirName):
                os.makedirs(dirName)
            fName=name    
            plt.savefig(dirName+"/"+fName+".png")
if __name__ == "__main__":
    #exit()
    parser = argparse.ArgumentParser(description="construct graph from facts of a babi-task and answer questions")
    parser.add_argument("-i", "--interactive",         help="enable interactive user mode", action="store_true")
    args = parser.parse_args()
    interactive = args.interactive
    
    babiGraphObj = babiGraph()
    with io.open(Globals.NERTEXT_FILE) as data_file:   
        for line in data_file:
            jsonObj = json.loads(line)
            fact=jsonObj["SNO"]
            babiGraphObj.subStoryCheck(fact, interactive)
            #print(jsonObj["isFact"],type(jsonObj["isFact"]))
            if(jsonObj["isFact"] is False):
                question = jsonObj["Sentence"]
                if interactive:
                    prompt_msg = "Do you want me to answer the question"
                    female.say(prompt_msg)
                    print(question)
                    female.say(question)
                    choice = input(prompt_msg + " (yes/no)\n")
                    if choice == "no":
                        ask_user_question = "What other question would you like me to answer"
                        female.say(ask_user_question)
                        user_question = input(ask_user_question + "\n")
                        lookup_response = "Let me think"
                        print(lookup_response)
                        female.say(lookup_response)
                        question = user_question
                annotedQuestion=babiGraphObj.annotateQuestion(question)
                QDict=babiGraphObj.processQuestion(annotedQuestion,question)
                subject = QDict["POS_NNP"]
                QNode=babiGraphObj.analyzeQuestion(QDict)
                babiGraphObj.traverseGraph(QNode,jsonObj, interactive, subject)
                if interactive:
                    prompt_msg = "Do you want me to continue with some more facts"
                    male.say(prompt_msg)
                    choice = input(prompt_msg + "? (yes/no)\n")
                    if choice == "no":
                        break
            else:
                if interactive:
                    sentence = jsonObj["Sentence"]
                    print("\t\t" + fact + " " + sentence)
                    male.say(sentence)
                node1=jsonObj["POS_NN"]
                node2=jsonObj["POS_NNP"]
                lemma=str(jsonObj["Lemma_Verb"])
                edgeAttribute=dict()
                edgeAttribute[fact]=lemma
                edge=(node1,node2,edgeAttribute)
                babiGraphObj.subStoryFacts[fact] = jsonObj["Sentence"]
                babiGraphObj.G.add_node(node1)#,color='red',style='filled',fillcolor='blue',shape='square'
                babiGraphObj.G.add_node(node2)
                babiGraphObj.G.add_edge(node1,node2,edgeAttribute)
                babiGraphObj.saveGraph(fact)
                
                sys.exit
