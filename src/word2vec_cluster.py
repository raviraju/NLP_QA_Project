#/NLP_QA_Project$ python src/word2vec_cluster.py input/qa1_single-supporting-fact_train_factsOnly.txt
				 #Word2Vec model is stored in models/word2vec_model_qa1_single-supporting-fact_train_factsOnly
				 #Clusters computed are stored in clusters/qa1_single-supporting-fact_train_factsOnly_cluster.json
#/NLP_QA_Project$ python src/word2vec_cluster.py input/qa2_two-supporting-facts_train_factsOnly.txt 
				 #Word2Vec model is stored in models/word2vec_model_qa2_two-supporting-facts_train_factsOnly
				 #Clusters computed are stored in clusters/qa2_two-supporting-facts_train_factsOnly_cluster.json
#/NLP_QA_Project$ python src/word2vec_cluster.py input/qa6_yes-no-questions_train_factsOnly.txt 
				 #Word2Vec model is stored in models/word2vec_model_qa6_yes-no-questions_train_factsOnly
				 #Clusters computed are stored in clusters/qa6_yes-no-questions_train_factsOnly_cluster.json
#/NLP_QA_Project$ 


import argparse, json, os
import gensim, logging
import numpy as np
from sklearn.cluster import MiniBatchKMeans, KMeans
from os.path import basename
from pprint import pprint

class Sentences(object):
    def __init__(self, fileName):
        self.fileName = fileName
 
    def __iter__(self):
        for line in open(self.fileName):
            yield line.split()

def getFileNamePart(fileName):
    return basename(fileName).strip('.txt')

def trainModel(factFile, verboseMode):
    if verboseMode:
        logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)
    sentences = Sentences(factFile)
    # Model HyperParameters
    ## 1. Pruning the internal dictionary
    ##    A reasonable value for min_count is between 0-100, depending on the size of your dataset.
    #model = gensim.models.Word2Vec(sentences, min_count=10)  # default value is 5
    ## 2.Size of the NN layers, which correspond to the “degrees” of freedom the training algorithm has:
    ##   Bigger size values require more training data, but can lead to better (more accurate) models. '
    ##   Reasonable values are in the tens to hundreds.
    #model = gensim.models.Word2Vec(sentences, size=200)  # default value is 100
    ## 3.Training parallelization, to speed up training:
    #model = gensim.models.Word2Vec(sentences, workers=4) # default = 1 worker = no parallelization

    model = gensim.models.Word2Vec(sentences, size=200, workers=4)

    # You can store/load models using the standard gensim methods
    modelFileName = 'models/word2vec_model_' + getFileNamePart(factFile)
    model.save(modelFileName)
    print("Word2Vec model is stored in {}".format(modelFileName))

def clusterWordEmbeddings(genSim_model, verboseMode):
    #genSim_model = gensim.models.Word2Vec.load('models/word2vec_model_' + getFileNamePart(factFile))
        
    #the vector dictionary of the model
    word2vec_dict={}
    for i in genSim_model.vocab.keys():
        try:
            word2vec_dict[i]=genSim_model[i]            
        except:    
            pass

    #clusters = MiniBatchKMeans(n_clusters=5, max_iter=100)
    clusters = KMeans(n_clusters=5, n_jobs=-1)
    X = np.array([value for key,value in word2vec_dict.items()])
    y = [i for i in word2vec_dict.keys()]
    #print(X)
    #print(y)
    clusters.fit(X)
    from collections import defaultdict
    cluster_dict=defaultdict(list)
    for word,label in zip(y,clusters.labels_):
        cluster_dict[label].append(word)

    clustersComputed = {}
    for key,values in cluster_dict.items():
        if verboseMode:
            print("*************************************")
            print("Group {}".format(key))
            print(values)
        outlier = genSim_model.doesnt_match(values)
        non_outlier = values[0]
        #pick a word from values not same as outlier
        for cand in values:
            if cand == outlier:
                continue
            else:
                non_outlier = cand
                break
        if verboseMode:
            print("Outlier : {}".format(outlier))
            print("Values most(>=0.5) similar to non_outlier \'{}\' : ".format(non_outlier))
        similarTuples = genSim_model.most_similar(non_outlier)
        groupMembers = set()
        for label,val in similarTuples:
            if val>=0.5 : 
                if verboseMode:
                    print("\t",label,val)
                groupMembers.add(label)
            else:
                if verboseMode:
                    print("\t <0.5 -------------",label,val)
        initialSet = set(values)
        if outlier not in groupMembers:
            if verboseMode:
                print("After removing outlier : {}".format(outlier))
            initialSet.remove(outlier)
        if verboseMode:
            print(initialSet)
        clustersComputed[str(key)] = list(initialSet)
    return(clustersComputed)

#0 ['picked', 'there', 'discarded', 'grabbed', 'got', 'up', 'dropped', 'put', 'down', 'left', 'took']
#1 ['bedroom', 'hallway', 'kitchen', 'office', 'to', 'bathroom', 'garden']
#2 ['daniel', 'mary', 'the', 'sandra', 'john']
#3 ['travelled', 'back', 'moved', 'journeyed', 'went']
#4 ['football', 'milk', 'apple']

#Action_Handle    Person, Things
#Location
#Person
#Action_Travel    Person, Location
#Things

def findKey(key, groups):
    for groupSet in groups:
        if key in groupSet:
            return True
    return False

def findGrp(key, groups):
    for groupSet in groups:
        if key in groupSet:
            return groupSet
    return None

def postProcessClusters(genSim_model, resolve_objectClusterActions):
    top2ActionDict = {}
    lowConfidentActions = []
    groups = []
    for action in resolve_objectClusterActions:
        #print(action)
        group = []
        all_similar_actions = genSim_model.most_similar(action)
        for similar_action in all_similar_actions:
            sim_action = similar_action [0]
            confidence = similar_action [1]
            if confidence > 0.99:
                group.append(sim_action)
                #print("\t Top_2 : {}\t{}".format(sim_action, confidence))
        #print(group)
        if len(group) > 0:
            top2ActionDict[action] = group
        else:
            lowConfidentActions.append(action)
    #pprint(top2ActionDict)
    #pprint(lowConfidentActions)

    for key,values in top2ActionDict.items():
        #print(key, value)
        if groups:
            if not findKey(key, groups):
                groupSet = set()
                groupSet.add(key)
                for value in values:
                    groupSet.add(value)
                groups.append(groupSet)
        else:
            groupSet = set()
            groupSet.add(key)
            for value in values:
                groupSet.add(value)
            groups.append(groupSet)
    #pprint(groups)
    for action in lowConfidentActions:
        #print(action)
        most_similar_action = ((genSim_model.most_similar(action))[0][0])
        grp = findGrp(most_similar_action, groups)
        if grp:
            grp.add(action)
    return(groups)

def main():
    parser = argparse.ArgumentParser(description="Clustering of facts using word2vec distributed representation")
    parser.add_argument("factFile", help="path to fact file")
    parser.add_argument("-v", "--verbose", help="increase output verbosity", action="store_true")
    args = parser.parse_args()
    factFile = args.factFile
    verboseMode = args.verbose
    
    trainModel(factFile, verboseMode)
    
    genSim_model = gensim.models.Word2Vec.load('models/word2vec_model_' + getFileNamePart(factFile))
    
    clustersComputed = clusterWordEmbeddings(genSim_model, verboseMode)
    
    clustersReComputed = {}
    no_of_clusters = 0
    for cluster in clustersComputed:
        #pprint(clustersComputed[cluster])
        newClusterGrps = (postProcessClusters(genSim_model, clustersComputed[cluster]))
        for clusterGrp in newClusterGrps:
            #print(list(clusterGrp))
            clustersReComputed[no_of_clusters] = list(clusterGrp)
            no_of_clusters += 1
    #pprint(clustersReComputed)
    
    clusterFileName = "clusters/" + getFileNamePart(factFile) + "_cluster.json"
    with open(clusterFileName, 'w') as outfile:
        json.dump(clustersReComputed, outfile, indent=4)
    print("Clusters computed are stored in {}".format(clusterFileName))
    #while True:
        #choice = input("Do you want to recompute clusters (y/n)?")
        #if choice.lower() == "y":
            #clustersComputed = clusterWordEmbeddings(verboseMode)
            #print("Cluster Computed : ")
            #pprint(clustersComputed)
        #else:
            #break

if __name__ == "__main__" : main()
