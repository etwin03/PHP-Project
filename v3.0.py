import requests
import math

def callAPI(call, input1 = None, input2 = None):
    if call is None:
        return []
    elif input2 is not None:
        data = requests.get(f'https://idwebsite.herokuapp.com/{call}/{input1}/{input2}')
    elif input1 is not None:
        data = requests.get(f'https://idwebsite.herokuapp.com/{call}/{input1}')
    else:
        data = requests.get(f'https://idwebsite.herokuapp.com/{call}')
    return data.json()

def processUserData(userData):
    symptoms = userData[0].split(', ')    #split different symptoms
    testResults = userData[1].split(', ')    #split different test results
    riskFactors = userData[2].split(', ')

    for i in range(len(symptoms)):    #format symptoms
        symptom = symptoms[i].split('; ')
        if symptom == []:
            symptom.append(None)
            symptom.append(None)
            break
        if symptom[0] == '':
            symptom[0] = None
        if len(symptom) == 1:
            symptom.append(None)
        for j in range(len(symptom)):    #lowercase symptoms
            if symptom[j] is not None:
                symptom[j] = symptom[j].lower().strip()
        symptoms[i] = symptom

    for i in range(len(testResults)):    #format test results
        testResult = testResults[i].split('; ')
        if testResult == []:
            testResult.append(None)
            testResult.append(None)
            break
        if testResult[0] == '':
            testResult[0] = None
        if len(testResult) == 1:
            testResult.append(None)
        for j in range(len(testResult)):    #lowercase test results
            if testResult[j] is not None:
                testResult[j] = testResult[j].lower().strip()
        testResults[i] = testResult

    for i in range(len(riskFactors)):
        riskFactor = riskFactors[i]
        if riskFactor == '':
            riskFactor = None
        if riskFactor is not None:
            riskFactor = riskFactor.lower().strip()
        riskFactors[i] = riskFactor

    return symptoms, testResults, riskFactors

def createAllMicrobeData():
    allMicrobeIDs = [microbe['subtypeid'] for microbe in callAPI('getAllSubtypes')]    #get all subtype IDs

    microbeSymptoms = {}
    symptomRatios = {}
    for microbeID in allMicrobeIDs:    #get symptoms for each subtype ID and symptom ratios
        microbeSymptoms[microbeID] = []
        for symptom in callAPI('getSymptomsBySubtypeID', microbeID):
            if symptom['name'] == '' or symptom['name'] is None:     #format symptoms for microbes
                microbeSymptoms[microbeID].append([None, None])
            elif symptom['modifier'] == '' or symptom['modifier'] is None:
                microbeSymptoms[microbeID].append([symptom['name'].lower().strip(), None])
            else:
                microbeSymptoms[microbeID].append([symptom['name'].lower().strip(), symptom['modifier'].lower().strip()])

            if symptom['name'] == '' or symptom['name'] is None:     #format symptoms for ratios
                symptom = [None, None]
            elif symptom['modifier'] == '' or symptom['modifier'] is None:
                symptom = [symptom['name'].lower().strip(), None]
            else:
                symptom = [symptom['name'].lower().strip(), symptom['modifier'].lower().strip()]
            if str(symptom) not in symptomRatios:    #get symptom counts
                symptomRatios[str(symptom)] = 1
            else:
                symptomRatios[str(symptom)] += 1
    for symptom in symptomRatios:   #get symptom ratios
        symptomRatios[symptom] /= len(allMicrobeIDs)

    microbeTestResults = {}
    for microbeID in allMicrobeIDs:    #get test results for each subtype ID
        microbeTestResults[microbeID] = []
        for testResult in callAPI('getTestresultsBySubtypeID', microbeID):    #format test results
            if testResult['name'] == '' or testResult['name'] is None:
                microbeTestResults[microbeID].append([None, None])
            elif testResult['positiveresult'] == '' or testResult['positiveresult'] is None:
                microbeTestResults[microbeID].append([testResult['name'].lower().strip(), None])
            else:
                microbeTestResults[microbeID].append([testResult['name'].lower().strip(), testResult['positiveresult'].lower().strip()])

    microbeRiskFactors = {}
    for microbeID in allMicrobeIDs:    #get risk factors for each subtype ID
        microbeRiskFactors[microbeID] = []
        for riskFactor in callAPI('getRiskfactorsBySubtypeID', microbeID):    #format risk factors
            if riskFactor['factor'] == '' or riskFactor['factor'] is None:
                microbeRiskFactors[microbeID].append(None)
            else:
                microbeRiskFactors[microbeID].append(riskFactor['factor'].lower().strip())



    f = open('allMicrobeData', 'w+')    #store somewhere temporarily
    f.write(str([microbeSymptoms, microbeTestResults, microbeRiskFactors, symptomRatios]))
    f.close()

    return

def jaccardSimilarity(microbeList, symptoms, testResults):
    f = open('allMicrobeData', 'r')    #get symptom and test results
    allMicrobeSymptoms, allMicrobeTestResults, allMicrobeRiskFactors, symptomRatios = eval(f.read())
    f.close()

    microbeJaccards = {}

    for microbe in microbeList:
        microbeJaccards[microbe] = 0    #set base intersections to 0
        union = 0    #set base union to 0
        for symptom in allMicrobeSymptoms[microbe]:
            if symptom in symptoms:    #get symptom intersections
                microbeJaccards[microbe] += 1
        union += len(symptoms) + len(allMicrobeSymptoms[microbe])    #add symptom union
        for testResult in allMicrobeTestResults[microbe]:
            if testResult in testResults:     #get test result intersections
                microbeJaccards[microbe] += 1
        union += len(testResults) + len(allMicrobeTestResults[microbe])    #add test result union
        union -= microbeJaccards[microbe]    #get final union

        microbeJaccards[microbe] = microbeJaccards[microbe]/union    #get jaccard similarity

    return microbeJaccards

def cosineSimilarity(microbeList, symptoms):
    f = open('allMicrobeData', 'r')    #get symptom and test results
    allMicrobeSymptoms, allMicrobeTestResults, allMicrobeRiskFactors, symptomRatios = eval(f.read())
    f.close()

    microbeCosines = {}
    microbeSymptomLength = 0
    inputSymptomLength = 0

    for microbe in microbeList:
        microbeCosines[microbe] = 0
        for symptom in allMicrobeSymptoms[microbe]:
            if symptom in symptoms:
                microbeCosines[microbe] += math.pow(1 / symptomRatios[str(symptom)], 2)     #dot product
            microbeSymptomLength += math.pow(1 / symptomRatios[str(symptom)], 2)     #length of microbe symptoms
        for symptom in symptoms:
            inputSymptomLength += math.pow(1 / symptomRatios[str(symptom)], 2)      #length of input symptoms
        microbeCosines[microbe] /= math.sqrt(microbeSymptomLength) * math.sqrt(inputSymptomLength)

    return microbeCosines

def scaleWeight(_dict, _key, weight):
    if _key in _dict:
        _dict[_key] *= weight
    else:
        _dict[_key] = weight

# createAllMicrobeData() #run at start of instance

### user input [symptoms], [test results]
userData=[input("Enter symptoms (a; modifier, b..., c...): "),
          input("Enter test results (a; positiveresult, b..., c...): "),
          input("Enter risk factors (a, b, c): ")]

symptoms, testResults, riskFactors = processUserData(userData)


### find microbes with correct symptoms
microbeWeights = {}
for symptom in symptoms:    #check each inputted symptom
    microbes = callAPI('getSubtypesBySymptom', symptom[0], symptom[1])    #find all microbes with that symptom
    for microbe in microbes:
        scaleWeight(microbeWeights, microbe['subtypeid'], 1)

### find and weight microbes with correct test results
for testResult in testResults:    # check each inputted test result
    if testResults == [[None, None]]:    # ! find a better way to catch this
        break
    microbes = callAPI('getTestresultsByName', testResult[0])    #find all microbes with that test result
    for microbe in microbes:
        if testResult[1] is not None and testResult[0] == microbe['name'].lower().strip():
            if microbe['positiveresult'].lower().strip() == testResult[1]:    #see if positive results match
            # ! not sure how to tell user to format positiveresults since they have different wordings
                scaleWeight(microbeWeights, microbe['subtypeid'], 1)
            else:
                scaleWeight(microbeWeights, microbe['subtypeid'], 0.66)    # microbe doesn't match, pertinent negative weight

### weight microbes by risk factors
for riskFactor in riskFactors:
    if riskFactors == [None]:
        break
    microbes = callAPI('getRiskfactorsByFactor', riskFactor)
    for microbe in microbes:
        if microbe['subtypeid'] in microbeWeights:
            scaleWeight(microbeWeights, microbe['subtypeid'], 1.5)     # increase weight

### weight the microbes based on jaccard similarity
microbeJaccards = jaccardSimilarity(microbeWeights, symptoms, testResults)
microbeCosines = cosineSimilarity(microbeWeights, symptoms)

### scale weights by risk factors and pertinent negatives
for microbe in microbeWeights:
    microbeJaccards[microbe] *= microbeWeights[microbe]
    microbeCosines[microbe] *= microbeWeights[microbe]

### sort microbe IDs
sortedMicrobes1 = dict(sorted(microbeJaccards.items(), key=lambda x: x[1], reverse=True))
sortedMicrobes2 = dict(sorted(microbeCosines.items(), key=lambda x: x[1], reverse=True))

### swap IDs with names
subtypeNames = {}
allSubtypes = callAPI('getAllSubtypes')
for subtype in allSubtypes:
    subtypeNames[subtype['subtypeid']] = f'{subtype["genus"]} {subtype["species"]}'

sortedMicrobeNames1 = {}
for microbe in sortedMicrobes1:
    sortedMicrobeNames1[subtypeNames[microbe]] = sortedMicrobes1[microbe]

sortedMicrobeNames2 = {}
for microbe in sortedMicrobes2:
    sortedMicrobeNames2[subtypeNames[microbe]] = sortedMicrobes2[microbe]

'''count = 1
for microbe in sortedMicrobeNames1:
    print(count, microbe, sortedMicrobeNames1[microbe])
    count += 1'''

count = 1
for microbe in sortedMicrobeNames2:
    print(count, microbe, sortedMicrobeNames2[microbe])
    count += 1


# Comments
# - How did you decide the weights of the different features?
# - Why both Jaccard and Cosine?
# - Formatting postiive results - possible menu option?
# - Why use all microbe data?