import argparse
import json
from os.path import basename
from collections import defaultdict

def annotate(clustersFile):
    annotatedDict = defaultdict(list)
    with open(clustersFile, 'r') as fp:
        clustersDict = json.load(fp)
        # print(clustersDict)
        for _, values in clustersDict.items():
            print("Provide a className for following set")
            print(values)
            className = input("Provide a className (a : attach, d : detach, t : transport, anyClass) : ")
            if className == "a":
                annotatedDict["attach"].extend(values)
            elif className == "d":
                annotatedDict["detach"].extend(values)
            elif className == "t":
                annotatedDict["transport"].extend(values)
            else:
                annotatedDict[className].extend(values)
    return annotatedDict


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="annotate clusters")
    parser.add_argument("clustersFile",
                        help="path to json file having clusters identified based on word embedding")
    args = parser.parse_args()
    annotatedDict = annotate(args.clustersFile)

    annotatedVerbFileName = basename(args.clustersFile).strip('.json') + "_annotated.json"
    annotatedVerbFilePath = "annotatedClusters/" + annotatedVerbFileName
    with open(annotatedVerbFilePath, 'w') as outFile:
        json.dump(annotatedDict, outFile, indent=4)
    print("annotatedClusters results found in {}".format(annotatedVerbFilePath))