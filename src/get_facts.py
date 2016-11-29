#>>> fact1
#'1 Mary moved to the bathroom.'
#>>> fact1.split(' ')
#['1', 'Mary', 'moved', 'to', 'the', 'bathroom.']
#>>> q1
#'7 Where is the football?\tgarden\t3 6'
#>>> q1.split('\t')
#['7 Where is the football?', 'garden', '3 6']

#NLP_QA_Project/src$ head -10 ../input/qa1_single-supporting-fact_train.txt 
#1 Mary moved to the bathroom.
#2 John went to the hallway.
#3 Where is Mary? 	bathroom	1
#4 Daniel went back to the hallway.
#5 Sandra moved to the garden.
#6 Where is Daniel? 	hallway	4
#7 John moved to the office.
#8 Sandra journeyed to the bathroom.
#9 Where is Daniel? 	hallway	4
#10 Mary moved to the hallway.

#/NLP_QA_Project$ python src/get_facts.py input/qa1_single-supporting-fact_train.txt
				 #Facts written to input/qa1_single-supporting-fact_train_factsOnly.txt
#/NLP_QA_Project$ python src/get_facts.py input/qa2_two-supporting-facts_train.txt 
				 #Facts written to input/qa2_two-supporting-facts_train_factsOnly.txt
#/NLP_QA_Project$ python src/get_facts.py input/qa6_yes-no-questions_train.txt 
				 #Facts written to input/qa6_yes-no-questions_train_factsOnly.txt
#/NLP_QA_Project$

import argparse, os

def extractFact(factLine, outFile):
	#print("fact : ", factLine)
	factList = factLine.split(' ')
	del factList[0]#fact no
	#print(' '.join(factList).replace('.','').lower(), file=outFile, end='')
	print(' '.join(factList).replace('.',''), file=outFile, end='')
	
	
def processData(trainingFilePath):
	with open(trainingFilePath, 'r') as inFile:
		factFileName = os.path.dirname(trainingFilePath) + '/' + os.path.basename(trainingFilePath).strip('.txt') + '_factsOnly.txt'
		with open(factFileName, 'w') as outFile:
			for line in inFile:
				if '\t' in line:
					continue
				else:
					extractFact(line, outFile)
	print("Facts written to {}".format(factFileName))

def main():
	parser = argparse.ArgumentParser(description="process babi-task training dataset to extract facts for buidling word embedding")
	parser.add_argument("path", help="path to training data")
	args = parser.parse_args()
	trainingFilePath = args.path
	processData(trainingFilePath)

if __name__ == "__main__" : main()
