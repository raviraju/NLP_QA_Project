#ravirajukrishna@ubuntu:/media/ravirajukrishna/Windows/Users/Ravi/Desktop/USC/Courses_Sem3/NLP/project/NLP_QA_Project$ python34 classifyVerbLemma.py input/qa1_single-supporting-fact_train_POS_Lemma.jl clusters/qa1_single-supporting-fact_train_factsOnly_cluster.json 
#Reading Clusters...
#{'0': ['Sandra', 'Daniel', 'Mary', 'John'],
 #'1': ['bathroom', 'kitchen', 'bedroom', 'office', 'garden', 'hallway'],
 #'2': ['went', 'travelled', 'moved', 'journeyed'],
 #'3': ['the', 'back'],
 #'4': []}
#Cluster Mapping Relation
#{'2': {'0:1'}}

#{'verb_2': {'data': ['went', 'travelled', 'moved', 'journeyed'],
            #'set_A': ['Sandra', 'Daniel', 'Mary', 'John'],
            #'set_B': ['bathroom',
                      #'kitchen',
                      #'bedroom',
                      #'office',
                      #'garden',
                      #'hallway']}}
#Results found in verbMapping/qa1_single-supporting-fact_train_factsOnly_cluster_classifyVerb.json
#ravirajukrishna@ubuntu:/media/ravirajukrishna/Windows/Users/Ravi/Desktop/USC/Courses_Sem3/NLP/project/NLP_QA_Project$ 


import argparse
import json_lines, json
from pprint import pprint
from os.path import basename

def getFileNamePart(fileName,stripText):
    return basename(fileName).strip(stripText)

def getLemmaVerbData(posLemmaVerbDict, verbData):
    lemmaVerbs = []
    for verb in verbData:
        lemmaVerb = posLemmaVerbDict.get(verb,"")
        if lemmaVerb:
            lemmaVerbs.append(lemmaVerb)
    return lemmaVerbs
    
def identifyClasses(pos_lemmaTagged_factFile, clusters_factFile):
    classifyVerbFileName = getFileNamePart(clusters_factFile, '.json') + "_classifyVerb.json"
    clustersDict = {}
    entityClusterDict = {}
    with open(clusters_factFile, 'r') as clusters_File:
        print("Reading Clusters...")
        clustersDict = json.load(clusters_File)
        pprint(clustersDict)
        for clusterNo in clustersDict:
            cluster_name = 'cluster_' + clusterNo
            for clusterItem in clustersDict[clusterNo]:
                entityClusterDict[clusterItem] = clusterNo#cluster_name
    #pprint(entityClusterDict)
    
    clusterVerbDict = {}
    posLemmaVerbDict = {}
    with open(pos_lemmaTagged_factFile, 'r') as pos_lemmaFile, open(clusters_factFile, 'r') as clusters_File:
        for item in json_lines.reader(pos_lemmaFile):
            itemKeys = item.keys()
            if item['isFact']:
                pos_nn = ""
                if 'POS_NN' in itemKeys:
                    pos_nn = item['POS_NN']
                pos_nnp = ""
                if 'POS_NNP' in itemKeys:
                    pos_nnp = item['POS_NNP']
                lemma_verb = ""
                if 'Lemma_Verb' in itemKeys:
                    lemma_verb = item['Lemma_Verb']
                pos_verb = ""
                if 'POS_Verb' in itemKeys:
                    pos_verb = item['POS_Verb']
                #print(pos_nnp, pos_verb, pos_nn, lemma_verb)
                posLemmaVerbDict[pos_verb] = lemma_verb
                clusterVerb = entityClusterDict.get(pos_verb, None)
                clusterNN  = entityClusterDict.get(pos_nn, None)
                clusterNNP = entityClusterDict.get(pos_nnp, None)
                #print(clusterNNP, clusterVerb, clusterNN)
                relationTuple = clusterNNP + ':' + clusterNN
                if clusterVerb in clusterVerbDict:
                    clusterVerbDict[clusterVerb].add(relationTuple)
                else:
                    clusterVerbDict[clusterVerb] = set([relationTuple])
    print("Cluster Mapping Relation")
    pprint(clusterVerbDict)
    print()
    resultDict = {}
    for clusterVerbId in clusterVerbDict:
        #print(clusterVerbId)
        verbDetails = {}
        verbName = 'verb_' + clusterVerbId
        verbData = clustersDict[clusterVerbId]
        for mapping in clusterVerbDict[clusterVerbId]:
            clustersMapped = mapping.split(':')
            setA = 'set_A'
            setA_Index = clustersMapped[0]
            setA_Data = clustersDict[setA_Index]
            setB = 'set_B'
            setB_Index = clustersMapped[1]
            setB_Data = clustersDict[setB_Index]
            verbDetails['data'] = verbData
            verbDetails['lemma_data'] = getLemmaVerbData(posLemmaVerbDict, verbData)
            verbDetails[setA] = setA_Data
            verbDetails[setB] = setB_Data
            resultDict[verbName] = verbDetails
    pprint(resultDict)
    resultFilePath = "verbMapping/" + classifyVerbFileName
    with open(resultFilePath, 'w') as outFile:
        json.dump(resultDict, outFile, indent=4)
    print("Results found in {}".format(resultFilePath))

def main():
    parser = argparse.ArgumentParser(description="classify lemma verb actions into categories based on entities they connect")
    parser.add_argument("pos_lemmaTagged_factFile", help="path to jsonLines file with POS and Lemma Annotations")
    parser.add_argument("clusters_factFile", help="path to json file having clusters identified based on word embedding")
    args = parser.parse_args()
    pos_lemmaTagged_factFile = args.pos_lemmaTagged_factFile
    clusters_factFile = args.clusters_factFile
    identifyClasses(pos_lemmaTagged_factFile, clusters_factFile)

if __name__ == "__main__" : main()
