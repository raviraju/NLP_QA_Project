import collections
import json
import io
from _collections import defaultdict

if __name__ == "__main__":
    lemmaDict = defaultdict(int)
    with io.open("/home/aditya/newJavaSpace/babI/babiLemma/NER_TEXT.jl") as data_file:   
        for line in data_file:
            jsonObj = json.loads(line)
            lemma=str(jsonObj["Lemma_Verb"])
            lemmaDict[lemma]+=1
    for k,v in lemmaDict.items():
        print(k + " : "+str(v))