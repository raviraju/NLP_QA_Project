import networkx as nx
import collections
import json
import io
import matplotlib.pyplot as plt
from pycorenlp import StanfordCoreNLP
from networkx.classes.function import neighbors

class babiGraph():
    def __init__(self):
        self.edgeList=[]
        self.nodeList=[]
        self.timeStampLemmaDict = dict()
        self.G=nx.Graph()
        self.corenlp = StanfordCoreNLP("http://localhost:9000")
    def subStoryCheck(self,fact):
        if(fact is 1):
            print("SUBSTORY BLOCK")
            print("New Story Detected")
            print("The Following graph is for this substory and it will be cleared. ")
           # self.displayGraph()
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
        #print(WHQ + " " + node + " " + verb + " " + lemma)
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
        with open("/home/aditya/newJavaSpace/babI/Tests/outputResults/outPutResults.jl", "a+") as textFile:
            json.dump(QJSON,textFile)
            textFile.write("\n")
        pass
    def traverseGraph(self,node,QJsonObj):
        QEdgeAttribute = dict()
        sampleDict=dict()
        neigh = self.G.neighbors(node)
        lemmaDict = {}
        locationSet = set(["go","travel","journey","move"])
        locationDict = {}
        objectSet = set(["football","apple","milk","move"])
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
        print(lemmaDict)
        #differenciate bw lemmas
        for lemma in lemmaDict:
            finalResultDict=dict()
            if lemma in locationSet:
                tsKeys = lemmaDict[lemma].keys()
                #print(tsKeys, type(tsKeys))
                for ts in tsKeys:
                    #print(ts)
                    location = lemmaDict[lemma][ts]
                    locationDict[ts] = location
                    finalResultDict=locationDict
            if lemma in objectSet:
                tsKeys = lemmaDict[lemma].keys()
                #print(tsKeys, type(tsKeys))
                for ts in tsKeys:
                    #print(ts)
                    object = lemmaDict[lemma][ts]
                    objectDict[ts] = location
                    finalResultDict=objectDict
        timeStamps = finalResultDict.keys()
        latestTimeStamp = max(timeStamps, key=int)
        answer = finalResultDict[latestTimeStamp]
        #print(answer,QJsonObj,latestTimeStamp)
        if(QJsonObj['Sentence']=="Where is John? "):
            #self.displayGraph()
            pass
        self.writeResults(answer, QJsonObj, latestTimeStamp)
        #lemmaChoice = input("Enter lemma type : {}\n".format(lemmaDict))
        #choices = lemmaDict.get(lemmaChoice,None)
        #print(choices)
        #if choices:
        #    timeStamps = choices.keys()
        #    latestTimeStamp = max(timeStamps, key=int)
            #print("Answer is " + choices[latestTimeStamp])
        #    print(question+"\t"+choices[latestTimeStamp]+"\t"+str(latestTimeStamp))
    def processQuestion(self,output):
        originalText = ""
        resultDict = dict()
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

if __name__ == "__main__":
    babiGraphObj = babiGraph()
    with io.open("/home/aditya/newJavaSpace/babI/babiLemma/NER_TEXT.jl") as data_file:   
        for line in data_file:
            jsonObj = json.loads(line)
            fact=jsonObj["SNO"]
            #fact=fact[0]
            babiGraphObj.subStoryCheck(fact)
            #print(jsonObj["isFact"],type(jsonObj["isFact"]))
            if(jsonObj["isFact"] is False):
                #print(jsonObj["Sentence"])
                #question=babiGraphObj.question(subStory)
                #print(subStory)
                question = jsonObj["Sentence"]
                print(question)
                annotedQuestion=babiGraphObj.annotateQuestion(question)
                QDict=babiGraphObj.processQuestion(annotedQuestion)
                QNode=babiGraphObj.analyzeQuestion(QDict)
                babiGraphObj.traverseGraph(QNode,jsonObj)
            else:
                sentence = jsonObj["Sentence"]
                node1=jsonObj["POS_NN"]
                node2=jsonObj["POS_NNP"]
                lemma=str(jsonObj["Lemma_Verb"])
                edgeAttribute=dict()
                edgeAttribute[fact]=lemma
                edge=(node1,node2,edgeAttribute)
                babiGraphObj.G.add_node(node1)
                babiGraphObj.G.add_node(node2)
                babiGraphObj.G.add_edge(node1,node2,edgeAttribute)
