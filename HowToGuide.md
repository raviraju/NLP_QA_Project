## Project Pipeline

**Start the StanfordCoreNLP server on Port 9000**

```java -mx4g -cp "*" edu.stanford.nlp.pipeline.StanfordCoreNLPServer -port 9000```

Check http://localhost:9000/

**Use StanfordCoreNLP to tokenize, fetch POS and Lemma**

```
(base) $ mkdir parsedInput
(base) $ python src/babiparser.py -i input/qa1_single-supporting-fact_train.txt -o parsedInput/qa1_single-supporting-fact_train.jl
(base) $ python src/babiparser.py -i input/qa2_two-supporting-facts_train.txt -o parsedInput/qa2_two-supporting-facts_train.jl
(base) $ python src/babiparser.py -i input/qa6_yes-no-questions_train.txt -o parsedInput/qa6_yes-no-questions_train.jl


The file format for each task is as follows:
ID text
ID text
ID text
ID question[tab]answer[tab]supporting fact IDS.
...
The IDs for a given “story” start at 1 and increase. When the IDs in a file reset back to 1 we can consider the following sentences as a new “story”. Supporting fact IDs only ever reference the sentences within a “story”.

4 Mary travelled to the hallway.
5 Where is the milk? 	hallway	1 4

{"sentence": "Mary travelled to the hallway.", "sNo": 4, "isFact": true, "posNNP": "Mary", "verb": "travelled", "posVerb": "VBD", "lemmaVerb": "travel", "posNN": "hallway"}
{"sentence": "Where is the milk? ", "sNo": 5, "isFact": false, "answer": "hallway", "supportingFactNos": [1, 4], "posWHQ": "Where", "verb": "is", "posVerb": "VBZ", "lemmaVerb": "be", "posNN": "milk", "expectedAnsType": "WHERE"}

```

**K-Means Clustering of facts using word2vec distributed representation**
```
(base) $ python src/get_clusters.py parsedInput/qa1_single-supporting-fact_train.jl
(base) $ python src/get_clusters.py parsedInput/qa2_two-supporting-facts_train.jl
(base) $ python src/get_clusters.py parsedInput/qa6_yes-no-questions_train.jl
```

**Annotate clusters**
```
(base) $ python src/annotate_clusters.py clusters/qa1_single-supporting-fact_train_cluster.json 

(base) $ python src/annotate_clusters.py clusters/qa2_two-supporting-facts_train_cluster.json 
Provide a className for following set
['the', 'Daniel', 'Sandra', 'John', 'Mary']
Provide a className (a : attach, d : detach, t : transport, anyClass) : person
Provide a className for following set
['to', 'bedroom.', 'bathroom.', 'hallway.', 'garden.', 'office.', 'kitchen.']
Provide a className (a : attach, d : detach, t : transport, anyClass) : location
Provide a className for following set
['went', 'moved', 'journeyed', 'back', 'travelled']
Provide a className (a : attach, d : detach, t : transport, anyClass) : t
Provide a className for following set
['there.']
Provide a className (a : attach, d : detach, t : transport, anyClass) : misc
Provide a className for following set
['milk', 'apple', 'football']
Provide a className (a : attach, d : detach, t : transport, anyClass) : object
Provide a className for following set
['picked', 'up', 'got', 'grabbed', 'took']
Provide a className (a : attach, d : detach, t : transport, anyClass) : a
Provide a className for following set
['milk.', 'apple.', 'football.']
Provide a className (a : attach, d : detach, t : transport, anyClass) : object
Provide a className for following set
['left', 'discarded', 'dropped', 'put', 'down']
Provide a className (a : attach, d : detach, t : transport, anyClass) : d
annotatedClusters results found in annotatedClusters/qa2_two-supporting-facts_train_cluster_annotated.json
(base) $ 

(base) $ python src/annotate_clusters.py clusters/qa6_yes-no-questions_train_cluster.json 

```

**Build and Traverse Graph leveraging semantic heuristic derived from word embedding classes in order to distingish verb actions**
```
(base) $ python src/babigraph.py parsedInput/qa1_single-supporting-fact_train.jl annotatedClusters/qa1_single-supporting-fact_train_cluster_annotated.json -o output/qa1_single-supporting-fact_train.jl
Wrote 10000 records to output/qa1_single-supporting-fact_train.jl
(base) $ python src/babigraph.py parsedInput/qa2_two-supporting-facts_train.jl annotatedClusters/qa2_two-supporting-facts_train_cluster_annotated.json -o output/qa2_two-supporting-facts_train.jl
Wrote 10000 records to output/qa2_two-supporting-facts_train.jl
(base) $ python src/babigraph.py parsedInput/qa6_yes-no-questions_train.jl annotatedClusters/qa6_yes-no-questions_train_cluster_annotated.json -o output/qa6_yes-no-questions_train.jl
Wrote 10000 records to output/qa6_yes-no-questions_train.jl
(base) $ 
```

**Evaluation : Ascertain no of questions correctly answered by the algorithm**
```
(base) $ python src/evaluate.py output/qa1_single-supporting-fact_train.jl Results : 
noOfCorrectPredictions :  20000
noOfInCorrectPredictions :  0
        noOfAnswersMismatch :  0
        noOfSupportingFactsMismatch :  0

(base) $ python src/evaluate.py output/qa2_two-supporting-facts_train.jl 
Results : 
noOfCorrectPredictions :  10000
noOfInCorrectPredictions :  0
        noOfAnswersMismatch :  0
        noOfSupportingFactsMismatch :  0

(base) $ python src/evaluate.py output/qa6_yes-no-questions_train.jl 
Results : 
noOfCorrectPredictions :  10000
noOfInCorrectPredictions :  0
        noOfAnswersMismatch :  0
        noOfSupportingFactsMismatch :  0
(base) $ 
```
