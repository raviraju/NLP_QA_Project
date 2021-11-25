import io
import json
import argparse

def evaluate(predictionsFile):
    with io.open(predictionsFile) as dataFile:
        noOfCorrectPredictions = 0
        noOfInCorrectPredictions = 0
        noOfSupportingFactsMismatch = 0
        noOfAnswersMismatch = 0
        for predictionDict in map(json.loads, dataFile):
            if predictionDict['act_answer'] == predictionDict['pred_answer']:
                if predictionDict['act_supportingFacts'] == predictionDict['pred_supportingFacts']:
                    noOfCorrectPredictions += 1
                else:
                    noOfInCorrectPredictions += 1
                    noOfSupportingFactsMismatch += 1
                    print(predictionDict)
                    input()
            else:
                noOfInCorrectPredictions += 1
                noOfAnswersMismatch += 1
                print(predictionDict)
                input()

        print("Results : ")
        print("noOfCorrectPredictions : ", noOfCorrectPredictions)
        print("noOfInCorrectPredictions : ", noOfInCorrectPredictions)
        print("\tnoOfAnswersMismatch : ", noOfAnswersMismatch)
        print("\tnoOfSupportingFactsMismatch : ", noOfSupportingFactsMismatch)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Evaluate Predictions')
    parser.add_argument('predictionsFile', help='Path to predictions of babi task file')
    args = parser.parse_args()

    evaluate(args.predictionsFile)