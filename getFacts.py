#>>> fact1
#'1 Mary moved to the bathroom.'
#>>> fact1.split(' ')
#['1', 'Mary', 'moved', 'to', 'the', 'bathroom.']
#>>> q1
#'7 Where is the football?\tgarden\t3 6'
#>>> q1.split('\t')
#['7 Where is the football?', 'garden', '3 6']

#>>>ravirajukrishna@ubuntu:/media/ravirajukrishna/Windows/Users/Ravi/Desktop/USC/Courses_Sem3/NLP/project/NLP_QA_Project$ head -10 input/qa1_single-supporting-fact_train.txt 
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
#ravirajukrishna@ubuntu:/media/ravirajukrishna/Windows/Users/Ravi/Desktop/USC/Courses_Sem3/NLP/project/NLP_QA_Project$ ls -ltr input/total 2680
#-rwxrwxrwx 1 ravirajukrishna ravirajukrishna  944248 Nov 14 21:24 qa1_single-supporting-fact_train.txt
#-rwxrwxrwx 1 ravirajukrishna ravirajukrishna 1794716 Nov 14 21:24 qa2_two-supporting-facts_train.txt
#ravirajukrishna@ubuntu:/media/ravirajukrishna/Windows/Users/Ravi/Desktop/USC/Courses_Sem3/NLP/project/NLP_QA_Project$ python getFacts.py input/qa1_single-supporting-fact_train.txt 
#Facts written to input/qa1_single-supporting-fact_train_factsOnly.txt
#ravirajukrishna@ubuntu:/media/ravirajukrishna/Windows/Users/Ravi/Desktop/USC/Courses_Sem3/NLP/project/NLP_QA_Project$ python getFacts.py input/qa2_two-supporting-facts_train.txt 
#Facts written to input/qa2_two-supporting-facts_train_factsOnly.txt
#ravirajukrishna@ubuntu:/media/ravirajukrishna/Windows/Users/Ravi/Desktop/USC/Courses_Sem3/NLP/project/NLP_QA_Project$ ls -ltr input/total 4480
#-rwxrwxrwx 1 ravirajukrishna ravirajukrishna  944248 Nov 14 21:24 qa1_single-supporting-fact_train.txt
#-rwxrwxrwx 1 ravirajukrishna ravirajukrishna 1794716 Nov 14 21:24 qa2_two-supporting-facts_train.txt
#-rwxrwxrwx 1 ravirajukrishna ravirajukrishna  580782 Nov 14 21:27 qa1_single-supporting-fact_train_factsOnly.txt
#-rwxrwxrwx 1 ravirajukrishna ravirajukrishna 1259315 Nov 14 21:27 qa2_two-supporting-facts_train_factsOnly.txt
#ravirajukrishna@ubuntu:/media/ravirajukrishna/Windows/Users/Ravi/Desktop/USC/Courses_Sem3/NLP/project/NLP_QA_Project$
#ravirajukrishna@ubuntu:/media/ravirajukrishna/Windows/Users/Ravi/Desktop/USC/Courses_Sem3/NLP/project/NLP_QA_Project$ head -10 input/qa1_single-supporting-fact_train_factsOnly.txt 
#Mary moved to the bathroom
#John went to the hallway
#Daniel went back to the hallway
#Sandra moved to the garden
#John moved to the office
#Sandra journeyed to the bathroom
#Mary moved to the hallway
#Daniel travelled to the office
#John went back to the garden
#John moved to the bedroom
#ravirajukrishna@ubuntu:/media/ravirajukrishna/Windows/Users/Ravi/Desktop/USC/Courses_Sem3/NLP/project/NLP_QA_Project$ 

import argparse

def extractFact(factLine, outFile):
	#print("fact : ", factLine)
	factList = factLine.split(' ')
	del factList[0]#fact no
	#print(' '.join(factList).replace('.','').lower(), file=outFile, end='')
	print(' '.join(factList).replace('.',''), file=outFile, end='')
	
	
def processData(trainingFilePath):
	with open(trainingFilePath, 'r') as inFile:
		factFileName = trainingFilePath.strip('.txt') + '_factsOnly.txt'
		with open(factFileName, 'w') as outFile:
			for line in inFile:
				if '\t' in line:
					continue
				else:
					extractFact(line, outFile)
	print("Facts written to {}".format(factFileName))

def main():
	parser = argparse.ArgumentParser(description="process babi-task training dataset for buidling word embedding")
	parser.add_argument("path", help="path to training data")
	args = parser.parse_args()
	trainingFilePath = args.path
	processData(trainingFilePath)

if __name__ == "__main__" : main()
