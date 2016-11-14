import networkx as nx
import collections
import json
import io
import matplotlib.pyplot as plt

# myDict = dict()
# myDict[1]='move'
# 
# G=nx.Graph()
# G.add_node("Mary")
# G.add_node("Bedroom")
# G.add_edge("Mary","Bedroom",attr_dict=myDict)
# nx.draw(G)
# 
# 
# 
# print(G.nodes())
# print(G.edges())
# print(G.get_edge_data('Mary','Bedroom'))
# plt.show()

#   General Rep 
#   babiGraphObj.addNode('Actor')
#   babiGraphObj.addNode('Location/Object')
#   babiGraphObj.addToTSLemmaDict(TimeStamp(feature number),'lemma')
#   babiGraphObj.addEdge('Actor', 'Location/Object')


#     G=nx.Graph()
#     G.add_node("Mary")
#     G.add_node("Mary")
#     G.add_node("Sandra")
#     G.add_node("John")
#     G.add_node("Bedroom")
#     G.add_node("Bathroom")
#     G.add_node("Kitchen")
#     G.add_node("Football")
#     G.add_node("Garden")
#     G.add_edge("Mary","Bedroom",{1:'move'})
#     G.add_edge("Mary","Bedroom",{2:'move'})
#     G.add_edge("John","Kitchen",{3:'move'})
#     G.add_edge("Mary","Football",{4:'took'})
#     
#     nx.draw(G,with_labels=True)
#     print(G.get_edge_data('Mary', 'Football'))
#     print(G.get_edge_data('Mary', 'Bedroom'))
#     node = 'Mary'
#     if(G.has_node(node)):
#         print(G.edges(node,data=True))
#         
#     #plt.show()
#     exit (0)
#     #return

class babiGraph():
    def __init__(self):
        self.edgeList=[]
        self.nodeList=[]
        self.timeStampLemmaDict = dict()
        self.G=nx.Graph()
    def addToTSLemmaDict(self,TS,lemma):
        self.timeStampLemmaDict[TS]=lemma
    def addEdge(self,u,v):
        self.edgeList.append((u,v))#add it as tuple
    def addNode(self,node):
        self.nodeList.append(node)
    def createGraph(self):
        self.G.add_nodes_from(self.nodeList)
        self.G.add_edges_from(self.edgeList,self.timeStampLemmaDict)
    def getNodeList(self):
        print("NodeList")
        print(self.nodeList)
        print(len(self.nodeList))
    def getEdgeList(self):
        print("EdgeList")
        print(self.edgeList)
        print(len(self.edgeList))
    def getEdgesofNode(self,node):
        print("Edges of the given node " + node +" are as follows ")
        if(self.G.has_node(node)):
            print(self.G.edges(node))
            for eachEdge in self.G.edges(node,data=True):
                print(eachEdge[0] ,eachEdge[1])
                print(self.G.get_edge_data(eachEdge[0], eachEdge[1]))
                #print(u + " is connected to " + v)
    def getTimeStampLemmaDict(self):
        for timeStamp,Lemma in self.timeStampLemmaDict.items():
            print("For TimeStamp " + str(timeStamp)+ " associated Lemma is "+" : " + Lemma)
    def displayGraph(self):
        nx.draw(self.G,with_labels=True)
        plt.show()
if __name__ == "__main__":
    babiGraphObj = babiGraph()
    
    with io.open("/home/aditya/newJavaSpace/babI/babiLemma/NER_TEXT.jl") as data_file:   
        for line in data_file:
            jsonObj = json.loads(line)
            fact=jsonObj["factNum"]
            fact=int(fact[0])
            node1=jsonObj["POS_NN"]
            node2=jsonObj["POS_NNP"]
            lemma=str(jsonObj["Lemma_Verb"])
            edgeAttribute=dict()
            edgeAttribute[fact]=lemma
            edge=(node1,node2,edgeAttribute)
            babiGraphObj.G.add_node(node1)
            babiGraphObj.G.add_node(node2)
            babiGraphObj.G.add_edge(node1,node2,edgeAttribute)
            
    babiGraphObj.displayGraph()   

#     
#     
#     babiGraphObj.addNode('Mary')
#     babiGraphObj.addNode('bathroom')
#     babiGraphObj.addToTSLemmaDict(1,'move')
#     babiGraphObj.addEdge('Mary', 'bathroom')
#     
#     babiGraphObj.addNode('Sandra')
#     babiGraphObj.addNode('bedroom')
#     babiGraphObj.addToTSLemmaDict(2,'journey')
#     babiGraphObj.addEdge('Sandra', 'bedroom')
#     
#     babiGraphObj.addNode('Mary')
#     babiGraphObj.addNode('football')
#     babiGraphObj.addToTSLemmaDict(3,'get')
#     babiGraphObj.addEdge('Mary', 'football')
#     
#     babiGraphObj.addNode('John')
#     babiGraphObj.addNode('kitchen')
#     babiGraphObj.addToTSLemmaDict(4,'go')
#     babiGraphObj.addEdge('John', 'kitchen')
#     
#     babiGraphObj.addNode('Mary')
#     babiGraphObj.addNode('kitchen')
#     babiGraphObj.addToTSLemmaDict(5,'go')
#     babiGraphObj.addEdge('Mary', 'kitchen')
#     
#     babiGraphObj.addNode('Mary')
#     babiGraphObj.addNode('garden')
#     babiGraphObj.addToTSLemmaDict(6,'go')
#     babiGraphObj.addEdge('Mary', 'garden')
#     
#     
#     
#     babiGraphObj.getEdgeList()
#     babiGraphObj.getNodeList()
#     babiGraphObj.getTimeStampLemmaDict()
#     babiGraphObj.getEdgesofNode('Mary')
#     #babiGraphObj.displayGraph()
    