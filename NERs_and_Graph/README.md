# Temporal Graph for Babi QA Tasks

This project aims to solve [Facebook AI Research(FAIR)'s babi QA tasks](https://research.facebook.com/research/babi/) using  temporal graph based approach.

This part of the project has 2 major parts and many sub parts:
1. Construction of Temporal Graphs to representing the activities of actors in the story
 + Parsing the input dataset
 + Normalizing each statement in the story to (timestamp, subject, verb, object) tuple
 + Building the graph and visualizing it
2. Answering questions based on inference on the graph data structure.
 + Parsing the questions
 + Traversing the graph to find the answers

Beside the above core system, this project also has two more supplementary modules:
1. Interactive Shell
2. Evaluator

## Structure of the project
Detailed Explanation of each folders

1. `/babiLemma`  
  - `babiLemma_working.py` is the Python script that takes the input task file, generates the POS using Stanford Core NLP and builds the enriched JSON for future processing.
  - Input file requried is placed in the folder Tests/babiLemmaInputFile/
  - Output file is at the location Tests/outputResultsLemma/ with name NER_TEXT_1_Supp.jl.
  - This NER_TEXT_1_Supp.jl has the enriched JSON which identifies each POS, facts, questions and serial number.

2. `babiGraph`
 + `newBabiGraph.py` is the Python script that reads the output of previous step viz. NER_TEXT_1_Supp.jl and builds the graph for evey story.
 + Whenever a question is asked, the script traverses the graph and gets the correct answer based on the time stamp and classification.
 + Whenver a new story is detected, the previous old story or graph is cleared.
 + Input file is  /babI/Tests/outputResultsLemma/NER_TEXT_1_Supp.jl
 + Output file is generated at /babI/Tests/outputResultsGraph/outPutResults.jl
3. Evaluation
  +  The Python script /babI/babiGraph/evaluate.py evaluates the output of babiGraph step viz outPutResults.jl
  + The number of correct answers as per our prediction and as per the dataset is provided at /babI/Tests/outputResultsGraph/evaluate.txt

## Requirements
+ Stanford Core NLP
+ python-espeak

## Setup
1. Setup Stanford CoreNLP server
  1. Download and extract Core NLP Server
     http://stanfordnlp.github.io/CoreNLP/#download
  2. Start the server on Port 9000  
     `java -mx4g -cp "*" edu.stanford.nlp.pipeline.StanfordCoreNLPServer 9000`
2. Python Espeak https://github.com/relsi/python-espeak


## Instructions
1. Parse the training data  
 ```
 babiparser.py --in Tests/babiLemmaInputFile/qa1_single-supporting-fact_train.txt \
--out output.jl
 ```

## Notes:
1. The paths as per now are hard-coded in the scripts and are realtive to my work environment, feel free to modify them as per your needs. Usually you can find the path in Globals.py.
2. Images folder has the images how exactly the graph is being built for first 24 stories.
