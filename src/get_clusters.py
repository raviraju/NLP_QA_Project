import argparse
import json
import os
import gensim
import logging
import json_lines
import numpy as np
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_samples, silhouette_score
from os.path import basename
from pprint import pprint
from collections import defaultdict
import pandas as pd

class Sentences(object):
    def __init__(self, fileName):
        self.fileName = fileName

    def __iter__(self):
        for item in json_lines.reader(open(self.fileName, 'r')):
            if item['isFact']:
                yield item['sentence'].split()

def getFileNamePart(fileName):
    return basename(fileName).strip('.txt').strip('.jl')

def trainModel(parsedFile, verboseMode):
    if verboseMode:
        logging.basicConfig(
            format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)
    sentences = Sentences(parsedFile)
    # Model HyperParameters
    # 1. Pruning the internal dictionary
    # A reasonable value for min_count is between 0-100, depending on the size of your dataset.
    # model = gensim.models.Word2Vec(sentences, min_count=10)  # default value is 5
    # 2.Size of the NN layers, which correspond to the “degrees” of freedom the training algorithm has:
    # Bigger size values require more training data, but can lead to better (more accurate) models. '
    # Reasonable values are in the tens to hundreds.
    # model = gensim.models.Word2Vec(sentences, vector_size=200)  # default value is 100
    # 3.Training parallelization, to speed up training:
    # model = gensim.models.Word2Vec(sentences, workers=4) # default = 1 worker = no parallelization

    model = gensim.models.Word2Vec(sentences, vector_size=300, workers=4)

    # You can store/load models using the standard gensim methods
    modelFileName = 'models/word2vec_model_' + getFileNamePart(parsedFile)
    model.save(modelFileName)
    print("Word2Vec model is stored in {}".format(modelFileName))

def getClusters(word2vec_dict):
    all_clusters = []
    for n_clusters in range(2, 9):
        clusterer = KMeans(n_clusters=n_clusters)
        X = np.array([value for key, value in word2vec_dict.items()])
        y = [i for i in word2vec_dict.keys()]
        # print(X)
        # print(y)
        cluster_labels = clusterer.fit_predict(X)

        silhouette_avg = silhouette_score(X, cluster_labels)

        cluster_dict = defaultdict(list)
        for word, label in zip(y, cluster_labels):
            cluster_dict[str(label)].append(word)

        all_clusters.append({
            'n_clusters':n_clusters,
            'silhouette_avg':silhouette_avg,
            'cluster_dict': cluster_dict
        })

    df = pd.DataFrame(all_clusters).sort_values('silhouette_avg', ascending=False)
    print(df)
    print(df.iloc[0])
    cluster_dict = df.iloc[0]['cluster_dict']
    return cluster_dict

def clusterWordEmbeddings(genSim_model, verboseMode):
    #genSim_model = gensim.models.Word2Vec.load('models/word2vec_model_' + getFileNamePart(parsedFile))

    # the vector dictionary of the model
    word2vec_dict={}
    # for i in genSim_model.vocab.keys():
    for i in genSim_model.wv.index_to_key:#https://stackoverflow.com/questions/35596031/gensim-word2vec-find-number-of-words-in-vocabulary
        try:
            word2vec_dict[i] = genSim_model.wv[i]
        except:
            pass

    cluster_dict = getClusters(word2vec_dict)
    return cluster_dict

def main():
    parser = argparse.ArgumentParser(
        description="Clustering of facts using word2vec distributed representation")
    parser.add_argument("parsedFile", help="path to parsed json lines file")
    parser.add_argument("-v", "--verbose",
                        help="increase output verbosity", action="store_true")
    args = parser.parse_args()
    parsedFile = args.parsedFile
    verboseMode = args.verbose

    trainModel(parsedFile, verboseMode)

    genSim_model = gensim.models.Word2Vec.load(
        'models/word2vec_model_' + getFileNamePart(parsedFile))

    cluster_dict = clusterWordEmbeddings(genSim_model, verboseMode)

    clusterFileName = "clusters/" + getFileNamePart(parsedFile) + "_cluster.json"
    with open(clusterFileName, 'w') as outfile:
        json.dump(cluster_dict, outfile, indent=4)
    print("Clusters computed are stored in {}".format(clusterFileName))

if __name__ == "__main__":
    main()
