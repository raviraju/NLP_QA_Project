#>>> fact1
#'1 Mary moved to the bathroom.'
#>>> fact1.split(' ')
#['1', 'Mary', 'moved', 'to', 'the', 'bathroom.']
#>>> q1
#'7 Where is the football?\tgarden\t3 6'
#>>> q1.split('\t')
#['7 Where is the football?', 'garden', '3 6']
#>>>
import argparse

def extractFact(factLine, outFile):
	#print("fact : ", factLine)
	factList = factLine.split(' ')
	#del factList[0]#fact no
	#print(' '.join(factList).replace('.','').lower(), file=outFile, end='')
	print(' '.join(factList).replace('.',''), file=outFile, end='')
	
	
def processData(trainingFilePath):
	QAString=""
	with open(trainingFilePath, 'r') as inFile:
		factFileName = trainingFilePath.strip('.txt') + '_SingleFactsOnly.txt'
		with open(factFileName, 'w') as outFile:
			for line in inFile:
				if '\t' in line:
					#print(line[:line.index("?")+1])
					normalLine=line[:line.index("?")+1] +"\n"
					QAline=line[line.index(" "):len(line)]
					extractFact(normalLine, outFile)
					QAString+=QAline
					#continue
				else:
					extractFact(line, outFile)
	writeToQuestionFile(QAString,trainingFilePath)
	print("Facts written to {}".format(factFileName))
def writeToQuestionFile(QAline,trainingFilePath):
	QAFileName = trainingFilePath.strip('.txt') + '_WhereActorOnly.txt'
	with open(QAFileName, 'w') as outFile:
		outFile.write(QAline)
def main():
	parser = argparse.ArgumentParser(description="process babi-task training dataset for buidling word embedding")
	parser.add_argument("path", help="path to training data")
	args = parser.parse_args()
	trainingFilePath = args.path
	processData(trainingFilePath)

if __name__ == "__main__" : main()
