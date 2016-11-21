#ravirajukrishna@ubuntu:/media/ravirajukrishna/Windows/Users/Ravi/Desktop/USC/Courses_Sem3/NLP/project/NLP_QA_Project$ python34 classifyVerbLemma.py input/qa6_yes-no-questions_train_POS_Lemma.jl clusters/qa6_yes-no-questions_train_factsOnly_cluster.json 
#Reading Clusters...
#{'0': ['hallway', 'bedroom', 'office', 'kitchen', 'garden', 'bathroom'],
 #'1': ['left',
       #'dropped',
       #'got',
       #'picked',
       #'discarded',
       #'down',
       #'took',
       #'up',
       #'put',
       #'grabbed'],
 #'2': ['journeyed', 'to', 'travelled', 'went', 'back', 'moved'],
 #'3': ['apple', 'football', 'milk', 'there'],
 #'4': ['Daniel', 'the', 'John', 'Sandra', 'Mary']}
#Cluster Mapping Relation
#{'1': {'4:3'}, '2': {'4:0'}}

#{'verb_1': {'data': ['left',
                     #'dropped',
                     #'got',
                     #'picked',
                     #'discarded',
                     #'down',
                     #'took',
                     #'up',
                     #'put',
                     #'grabbed'],
            #'lemma_data': ['leave',
                           #'drop',
                           #'get',
                           #'pick',
                           #'discard',
                           #'take',
                           #'put',
                           #'grab'],
            #'set_A': ['Daniel', 'the', 'John', 'Sandra', 'Mary'],
            #'set_B': ['apple', 'football', 'milk', 'there']},
 #'verb_2': {'data': ['journeyed', 'to', 'travelled', 'went', 'back', 'moved'],
            #'lemma_data': ['journey', 'travel', 'go', 'move'],
            #'set_A': ['Daniel', 'the', 'John', 'Sandra', 'Mary'],
            #'set_B': ['hallway',
                      #'bedroom',
                      #'office',
                      #'kitchen',
                      #'garden',
                      #'bathroom']}}
#Results found in verbMapping/qa6_yes-no-questions_train_factsOnly_cluster_classifyVerb.json
#Provide a className for following set of verbs
#Provide a className (o : objectVerbs, l : locationVerbs, anyOtheName) for set of verbs : ['journey', 'travel', 'go', 'move']
#l
#Provide a className for following set of verbs
#Provide a className (o : objectVerbs, l : locationVerbs, anyOtheName) for set of verbs : ['leave', 'drop', 'get', 'pick', 'discard', 'take', 'put', 'grab']
#o
#{'locationVerbs': ['journey', 'travel', 'go', 'move'],
 #'objectVerbs': ['leave',
                 #'drop',
                 #'get',
                 #'pick',
                 #'discard',
                 #'take',
                 #'put',
                 #'grab']}
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

def annotateVerbs(resultDict, annotatedVerbFileName):
    annotatedVerbDict = {}
    for verb in resultDict:
        print("Provide a className for following set of verbs")
        className = input("Provide a className (o : objectVerbs, l : locationVerbs, anyOtheName) for set of verbs : {}\n".format(resultDict[verb]["lemma_data"]))
        if className == "o":
            annotatedVerbDict["objectVerbs"] = resultDict[verb]["lemma_data"]
        elif className == "l":
            annotatedVerbDict["locationVerbs"] = resultDict[verb]["lemma_data"]
        else:
            annotatedVerbDict[className] = resultDict[verb]["lemma_data"]
    pprint(annotatedVerbDict)
    annotatedVerbFilePath = "annotatedVerbs/" + annotatedVerbFileName
    with open(annotatedVerbFilePath, 'w') as outFile:
        json.dump(annotatedVerbDict, outFile, indent=4)


def identifyClasses(pos_lemmaTagged_factFile, clusters_factFile):
    classifyVerbFileName = getFileNamePart(clusters_factFile, '.json') + "_classifyVerb.json"
    annotatedVerbFileName = getFileNamePart(clusters_factFile, '.json') + "_annotatedVerb.json"
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
    
    annotateVerbs(resultDict, annotatedVerbFileName)

def main():
    parser = argparse.ArgumentParser(description="classify lemma verb actions into categories based on entities they connect")
    parser.add_argument("pos_lemmaTagged_factFile", help="path to jsonLines file with POS and Lemma Annotations")
    parser.add_argument("clusters_factFile", help="path to json file having clusters identified based on word embedding")
    args = parser.parse_args()
    pos_lemmaTagged_factFile = args.pos_lemmaTagged_factFile
    clusters_factFile = args.clusters_factFile
    identifyClasses(pos_lemmaTagged_factFile, clusters_factFile)

if __name__ == "__main__" : main()
