import networkx as nx
import collections
import json
import io
import os
import sys
import matplotlib.pyplot as plt
from pycorenlp import StanfordCoreNLP
from Globals import Globals
from networkx.classes.function import neighbors


class babiGraph():
    def __init__(self):
        self.edgeList=[]
        self.nodeList=[]
        self.timeStampLemmaDict = dict()
        self.G=nx.Graph()
        self.storyNum=0
        self.corenlp = StanfordCoreNLP(Globals.CORENLP_SERVER)
    def subStoryCheck(self,fact):
        
        if(fact is "1"):
            print("SUBSTORY BLOCK")
            print("New Story Detected")
            print("The Following graph is for this substory and it will be cleared. ")
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
        WHQ=QDict.get("WHQ","NoWHQues")
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
    def traverseGraph(self,node,QJsonObj,YESNO):
        QEdgeAttribute = dict()
        sampleDict=dict()
        YESNO_EXPECTED_ANS=""
        neigh = self.G.neighbors(node)
        lemmaDict = {}
        locationSet = set(["go","travel","journey","move"])
        locationDict = {}
        #"football","apple","milk","box",
        objectSet = set(["pick","leave","grab","take","get","discard","drop","put"])
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
        #return
        #differenciate bw lemmas
        location=""
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
        latestTimeStamp = max(timeStamps, key=int)
        answer = finalResultDict[latestTimeStamp]
        if YESNO:
            ##POSSIBLE CULPRIT##
            YESNO_EXPECTED_ANS=QJsonObj['POS_NN']
            if answer!=YESNO_EXPECTED_ANS:
                answer="no"
            else:
                answer="yes"
            self.writeResults(answer, QJsonObj, latestTimeStamp)
        else:
            self.writeResults(answer, QJsonObj, latestTimeStamp)
    def processQuestion(self,output,que):
        originalText = ""
        resultDict = dict()
        print("Question asked is " +que )
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
            pos=nx.spring_layout(self.G)   
            nx.draw(self.G,pos,with_labels=True)
            nx.draw_networkx_edge_labels(self.G, pos)
            dirName=str(self.storyNum)
            dirName=os.path.join(Globals.IMAGE_DIR, dirName)
            if not os.path.exists(dirName):
                os.makedirs(dirName)
            fName=name    
            plt.savefig(dirName+"/"+fName+".png")
if __name__ == "__main__":
    babiGraphObj = babiGraph()
    YESNO=True
    with io.open(Globals.NERTEXT_FILE) as data_file:   
        for line in data_file:
            jsonObj = json.loads(line)
            fact=jsonObj["SNO"]
            babiGraphObj.subStoryCheck(fact)
            #print(jsonObj["isFact"],type(jsonObj["isFact"]))
            if(jsonObj["isFact"] is False):
                question = jsonObj["Sentence"]
                annotedQuestion=babiGraphObj.annotateQuestion(question)
                QDict=babiGraphObj.processQuestion(annotedQuestion,question)
                QNode=babiGraphObj.analyzeQuestion(QDict)
                babiGraphObj.traverseGraph(QNode,jsonObj,YESNO)
                
            else:
                sentence = jsonObj["Sentence"]
                node1=jsonObj["POS_NN"]
                node2=jsonObj["POS_NNP"]
                lemma=str(jsonObj["Lemma_Verb"])
                edgeAttribute=dict()
                edgeAttribute[fact]=lemma
                edge=(node1,node2,edgeAttribute)
                babiGraphObj.G.add_node(node1)#,color='red',style='filled',fillcolor='blue',shape='square'
                babiGraphObj.G.add_node(node2)
                babiGraphObj.G.add_edge(node1,node2,edgeAttribute)
                babiGraphObj.saveGraph(fact)
                
                sys.exit