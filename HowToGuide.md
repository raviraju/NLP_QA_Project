## Project Pipeline 
**Use StanfordCoreNLP to fetch POS and Lemma**
```
> python src/babiparser.py -i input/qa2_two-supporting-facts_train.txt -o input/qa2_two-supporting-facts_train.jl
Files are being read and tokenized ...
Done
```

**Extract fact sentences(except questions) from all stories of a task**
```
> python src/get_facts.py input/qa2_two-supporting-facts_train.txt 
Facts written to input/qa2_two-supporting-facts_train_factsOnly.txt
```

**Clustering of facts using word2vec distributed representation**
```
> python src/word2vec_cluster.py input/qa2_two-supporting-facts_train_factsOnly.txt 
Word2Vec model is stored in models/word2vec_model_qa2_two-supporting-facts_train_factsOnly
Clusters computed are stored in clusters/qa2_two-supporting-facts_train_factsOnly_cluster.json
```

**Classify lemma verb actions into categories based on entities they connect**
```
>python34 src/classify_verb_lemma.py input/qa2_two-supporting-facts_train.jl clusters/qa2_two-supporting-facts_train_factsOnly_cluster.json 
Reading Clusters...
{'0': ['hallway', 'kitchen', 'garden', 'bedroom', 'office', 'bathroom'],
'1': ['journeyed', 'travelled', 'moved', 'went'],
'2': ['football', 'milk', 'apple'],
'3': ['got', 'took', 'grabbed', 'picked', 'up'],
'4': ['put', 'dropped', 'discarded', 'down', 'left'],
'5': ['Mary', 'Daniel', 'Sandra', 'John']}
Cluster Mapping Relation
{'1': {'5:0'}, '3': {'5:2'}, '4': {'5:2'}}

{'verb_1': {'data': ['journeyed', 'travelled', 'moved', 'went'],
		'lemma_data': ['journey', 'travel', 'move', 'go'],
		'set_A': ['Mary', 'Daniel', 'Sandra', 'John'],
		'set_B': ['hallway',
					'kitchen',
					'garden',
					'bedroom',
					'office',
					'bathroom']},
'verb_3': {'data': ['got', 'took', 'grabbed', 'picked', 'up'],
		'lemma_data': ['get', 'take', 'grab', 'pick'],
		'set_A': ['Mary', 'Daniel', 'Sandra', 'John'],
		'set_B': ['football', 'milk', 'apple']},
'verb_4': {'data': ['put', 'dropped', 'discarded', 'down', 'left'],
		'lemma_data': ['put', 'drop', 'discard', 'leave'],
		'set_A': ['Mary', 'Daniel', 'Sandra', 'John'],
		'set_B': ['football', 'milk', 'apple']}}
verbMapping results found in verbMapping/qa2_two-supporting-facts_train_factsOnly_cluster_classifyVerb.json
Provide a className for following set of verbs
Provide a className (a : attach, d : detach, t : transport, anyOtheName) for set of verbs : ['journey', 'travel', 'move', 'go']
t
Provide a className for following set of verbs
Provide a className (a : attach, d : detach, t : transport, anyOtheName) for set of verbs : ['get', 'take', 'grab', 'pick']
a
Provide a className for following set of verbs
Provide a className (a : attach, d : detach, t : transport, anyOtheName) for set of verbs : ['put', 'drop', 'discard', 'leave']
d
{'attach': ['get', 'take', 'grab', 'pick'],
'detach': ['put', 'drop', 'discard', 'leave'],
'transport': ['journey', 'travel', 'move', 'go']}
annotatedVerbs results found in annotatedVerbs/qa2_two-supporting-facts_train_factsOnly_cluster_annotatedVerb.json
```

**Build and Traverse Graph leveraging semantic heuristic derived from word embedding classes in order to distingish verb actions**
```
> python3 src/babigraph.py -in input/qa2_two-supporting-facts_train.jl -ia annotatedVerbs/qa2_two-supporting-facts_train_factsOnly_cluster_annotatedVerb.json -o output/qa2_two-supporting-facts_train.tsv
Wrote 10000 records to output/qa2_two-supporting-facts_train.tsv
```

**Evaluation : Ascertain no of questions correctly answered by the algorithm**
```
> src/eval.sh output/qa2_two-supporting-facts_train.tsv 
Total no of outputs to evaluate:
10000 output/qa2_two-supporting-facts_train.tsv
No of Correct(1)/InCorrect(0) Matches:
	10000 1
```
