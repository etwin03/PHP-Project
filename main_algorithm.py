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
    symptoms = userData[0].split(',')    #split different symptoms
    testResults = userData[1].split(',')    #split different test results
    riskFactors = userData[2].split(',')

    for i in range(len(symptoms)):    #format symptoms
        symptom = symptoms[i].split(';')
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
        testResult = testResults[i].split(';')
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

    microbeTypes = {}
    microbeTypes['bacteria'] = [subtype['subtypeid'] for subtype in callAPI('getSubtypesByClassification', 'bacteria')]
    microbeTypes['fungi'] = [subtype['subtypeid'] for subtype in callAPI('getSubtypesByClassification', 'fungi')]
    microbeTypes['virus'] = [subtype['subtypeid'] for subtype in callAPI('getSubtypesByClassification', 'virus')]
    microbeTypes['parasite'] = [subtype['subtypeid'] for subtype in callAPI('getSubtypesByClassification', 'parasite')]



    f = open('allMicrobeData.txt', 'w+')    #store somewhere temporarily
    f.write(str([microbeSymptoms, microbeTestResults, microbeRiskFactors, symptomRatios, microbeTypes]))
    f.close()

    return

def cosineSimilarity(microbeList, symptoms):
    f = open('allMicrobeData.txt', 'r')    #get symptom and test results
    allMicrobeSymptoms, allMicrobeTestResults, allMicrobeRiskFactors, symptomRatios, microbeTypes = eval(f.read())
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


PERTINENT_NEGATIVE_WEIGHT = 0.66
RISK_FACTOR_WEIGHT = 1.5
MICROBE_TYPE_CUTOFF = 15
MICROBE_TYPE_WEIGHT = 2

if __name__ == '__main__': 
    
    createAllMicrobeData() #run at start of instance

    f = open('allMicrobeData.txt', 'r')    #get symptom and test results
    allMicrobeSymptoms, allMicrobeTestResults, allMicrobeRiskFactors, symptomRatios, microbeTypes = eval(f.read())
    f.close()

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
                    scaleWeight(microbeWeights, microbe['subtypeid'], PERTINENT_NEGATIVE_WEIGHT)    # microbe doesn't match, pertinent negative weight

    ### weight microbes by risk factors
    for riskFactor in riskFactors:
        if riskFactors == [None]:
            break
        microbes = callAPI('getRiskfactorsByFactor', riskFactor)
        for microbe in microbes:
            if microbe['subtypeid'] in microbeWeights:
                scaleWeight(microbeWeights, microbe['subtypeid'], RISK_FACTOR_WEIGHT)     # increase weight

    ### weight the microbes based on jaccard similarity
    microbeCosines = cosineSimilarity(microbeWeights, symptoms)

    ### scale weights by risk factors and pertinent negatives
    for microbe in microbeWeights:
        microbeCosines[microbe] *= microbeWeights[microbe]

    ### sort microbe IDs
    sortedMicrobes = dict(sorted(microbeCosines.items(), key=lambda x: x[1], reverse=True))

    ### weight microbes by most common type
    cutoff = MICROBE_TYPE_CUTOFF
    types = [0, 0, 0, 0]
    for microbe in sortedMicrobes:
        types[0] += 1 if microbe in microbeTypes['bacteria'] else 0
        types[1] += 1 if microbe in microbeTypes['fungi'] else 0
        types[2] += 1 if microbe in microbeTypes['virus'] else 0
        types[3] += 1 if microbe in microbeTypes['parasite'] else 0
        
        cutoff -= 1
        if cutoff == 0:
            break
    if types[0] == max(types):
        maxType = 'bacteria'
    if types[1] == max(types):
        maxType = 'fungi'
    if types[2] == max(types):
        maxType = 'virus'
    if types[3] == max(types):
        maxType = 'parasite'
    
    for microbe in microbeCosines:
        if microbe in microbeTypes[maxType]:
            microbeCosines[microbe] *= MICROBE_TYPE_WEIGHT

    sortedMicrobes = dict(sorted(microbeCosines.items(), key=lambda x: x[1], reverse=True))

    ### swap IDs with names
    subtypeNames = {}
    allSubtypes = callAPI('getAllSubtypes')
    for subtype in allSubtypes:
        subtypeNames[subtype['subtypeid']] = f'{subtype["genus"]} {subtype["species"]}'

    sortedMicrobeNames = {}
    for microbe in sortedMicrobes:
        sortedMicrobeNames[subtypeNames[microbe]] = sortedMicrobes[microbe]



