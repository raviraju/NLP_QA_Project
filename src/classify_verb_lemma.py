#/NLP_QA_Project$ python34 src/classify_verb_lemma.py input/qa1_single-supporting-fact_train.jl clusters/qa1_single-supporting-fact_train_factsOnly_cluster.json 
				#Reading Clusters...
				#{'0': ['Mary', 'Sandra'],
				 #'1': ['Daniel', 'John'],
				 #'2': ['bathroom', 'bedroom', 'kitchen', 'hallway', 'office', 'garden'],
				 #'3': ['moved', 'journeyed', 'travelled', 'went']}
				#Cluster Mapping Relation
				#{'3': {'0:2', '1:2'}}

				#{'verb_3': {'data': ['moved', 'journeyed', 'travelled', 'went'],
							#'lemma_data': ['move', 'journey', 'travel', 'go'],
							#'set_A': ['Daniel', 'John'],
							#'set_B': ['bathroom',
									  #'bedroom',
									  #'kitchen',
									  #'hallway',
									  #'office',
									  #'garden']}}
				#verbMapping results found in verbMapping/qa1_single-supporting-fact_train_factsOnly_cluster_classifyVerb.json
				#Provide a className for following set of verbs
				#Provide a className (a : attach, d : detach, t : transport, anyOtheName) for set of verbs : ['move', 'journey', 'travel', 'go']
				#t
				#{'transport': ['move', 'journey', 'travel', 'go']}
				#annotatedVerbs results found in annotatedVerbs/qa1_single-supporting-fact_train_factsOnly_cluster_annotatedVerb.json
#/NLP_QA_Project$ python34 src/classify_verb_lemma.py input/qa2_two-supporting-facts_train.jl clusters/qa2_two-supporting-facts_train_factsOnly_cluster.json 
				#Reading Clusters...
				#{'0': ['hallway', 'kitchen', 'garden', 'bedroom', 'office', 'bathroom'],
				 #'1': ['journeyed', 'travelled', 'moved', 'went'],
				 #'2': ['football', 'milk', 'apple'],
				 #'3': ['got', 'took', 'grabbed', 'picked', 'up'],
				 #'4': ['put', 'dropped', 'discarded', 'down', 'left'],
				 #'5': ['Mary', 'Daniel', 'Sandra', 'John']}
				#Cluster Mapping Relation
				#{'1': {'5:0'}, '3': {'5:2'}, '4': {'5:2'}}

				#{'verb_1': {'data': ['journeyed', 'travelled', 'moved', 'went'],
							#'lemma_data': ['journey', 'travel', 'move', 'go'],
							#'set_A': ['Mary', 'Daniel', 'Sandra', 'John'],
							#'set_B': ['hallway',
									  #'kitchen',
									  #'garden',
									  #'bedroom',
									  #'office',
									  #'bathroom']},
				 #'verb_3': {'data': ['got', 'took', 'grabbed', 'picked', 'up'],
							#'lemma_data': ['get', 'take', 'grab', 'pick'],
							#'set_A': ['Mary', 'Daniel', 'Sandra', 'John'],
							#'set_B': ['football', 'milk', 'apple']},
				 #'verb_4': {'data': ['put', 'dropped', 'discarded', 'down', 'left'],
							#'lemma_data': ['put', 'drop', 'discard', 'leave'],
							#'set_A': ['Mary', 'Daniel', 'Sandra', 'John'],
							#'set_B': ['football', 'milk', 'apple']}}
				#verbMapping results found in verbMapping/qa2_two-supporting-facts_train_factsOnly_cluster_classifyVerb.json
				#Provide a className for following set of verbs
				#Provide a className (a : attach, d : detach, t : transport, anyOtheName) for set of verbs : ['journey', 'travel', 'move', 'go']
				#t
				#Provide a className for following set of verbs
				#Provide a className (a : attach, d : detach, t : transport, anyOtheName) for set of verbs : ['get', 'take', 'grab', 'pick']
				#a
				#Provide a className for following set of verbs
				#Provide a className (a : attach, d : detach, t : transport, anyOtheName) for set of verbs : ['put', 'drop', 'discard', 'leave']
				#d
				#{'attach': ['get', 'take', 'grab', 'pick'],
				 #'detach': ['put', 'drop', 'discard', 'leave'],
				 #'transport': ['journey', 'travel', 'move', 'go']}
				#annotatedVerbs results found in annotatedVerbs/qa2_two-supporting-facts_train_factsOnly_cluster_annotatedVerb.json
#/NLP_QA_Project$ python34 src/classify_verb_lemma.py input/qa6_yes-no-questions_train.jl clusters/qa6_yes-no-questions_train_factsOnly_cluster.json 
				#Reading Clusters...
				#{'0': ['garden', 'kitchen', 'bathroom', 'office', 'hallway', 'bedroom'],
				 #'1': ['grabbed', 'picked', 'up', 'took', 'got'],
				 #'2': ['discarded', 'down', 'left', 'put', 'dropped'],
				 #'3': ['apple', 'football', 'milk'],
				 #'4': ['John', 'Sandra', 'the', 'Mary', 'Daniel'],
				 #'5': ['journeyed', 'travelled', 'went', 'moved']}
				#Cluster Mapping Relation
				#{'1': {'4:3'}, '2': {'4:3'}, '5': {'4:0'}}

				#{'verb_1': {'data': ['grabbed', 'picked', 'up', 'took', 'got'],
							#'lemma_data': ['grab', 'pick', 'take', 'get'],
							#'set_A': ['John', 'Sandra', 'the', 'Mary', 'Daniel'],
							#'set_B': ['apple', 'football', 'milk']},
				 #'verb_2': {'data': ['discarded', 'down', 'left', 'put', 'dropped'],
							#'lemma_data': ['discard', 'leave', 'put', 'drop'],
							#'set_A': ['John', 'Sandra', 'the', 'Mary', 'Daniel'],
							#'set_B': ['apple', 'football', 'milk']},
				 #'verb_5': {'data': ['journeyed', 'travelled', 'went', 'moved'],
							#'lemma_data': ['journey', 'travel', 'go', 'move'],
							#'set_A': ['John', 'Sandra', 'the', 'Mary', 'Daniel'],
							#'set_B': ['garden',
									  #'kitchen',
									  #'bathroom',
									  #'office',
									  #'hallway',
									  #'bedroom']}}
				#verbMapping results found in verbMapping/qa6_yes-no-questions_train_factsOnly_cluster_classifyVerb.json
				#Provide a className for following set of verbs
				#Provide a className (a : attach, d : detach, t : transport, anyOtheName) for set of verbs : ['grab', 'pick', 'take', 'get']
				#a
				#Provide a className for following set of verbs
				#Provide a className (a : attach, d : detach, t : transport, anyOtheName) for set of verbs : ['discard', 'leave', 'put', 'drop']
				#d
				#Provide a className for following set of verbs
				#Provide a className (a : attach, d : detach, t : transport, anyOtheName) for set of verbs : ['journey', 'travel', 'go', 'move']
				#t
				#{'attach': ['grab', 'pick', 'take', 'get'],
				 #'detach': ['discard', 'leave', 'put', 'drop'],
				 #'transport': ['journey', 'travel', 'go', 'move']}
				#annotatedVerbs results found in annotatedVerbs/qa6_yes-no-questions_train_factsOnly_cluster_annotatedVerb.json
#/NLP_QA_Project$ 



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
        className = input("Provide a className (a : attach, d : detach, t : transport, anyOtheName) for set of verbs : {}\n".format(resultDict[verb]["lemma_data"]))
        if className == "a":
            annotatedVerbDict["attach"] = resultDict[verb]["lemma_data"]
        elif className == "d":
            annotatedVerbDict["detach"] = resultDict[verb]["lemma_data"]
        elif className == "t":
            annotatedVerbDict["transport"] = resultDict[verb]["lemma_data"]
        else:
            annotatedVerbDict[className] = resultDict[verb]["lemma_data"]
    pprint(annotatedVerbDict)
    annotatedVerbFilePath = "annotatedVerbs/" + annotatedVerbFileName
    with open(annotatedVerbFilePath, 'w') as outFile:
        json.dump(annotatedVerbDict, outFile, indent=4)
    print("annotatedVerbs results found in {}".format(annotatedVerbFilePath))


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
                if clusterVerb:
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
    print("verbMapping results found in {}".format(resultFilePath))
    
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
