from main_algorithm import *

f = open('caseStudies.txt', 'r')
caseStudies = eval(f.read())
f.close()

ranks = []

for caseStudy in caseStudies:
    symptoms, testResults, riskFactors = processUserData(caseStudy[1])

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

    ### swap IDs with names
    subtypeNames = {}
    allSubtypes = callAPI('getAllSubtypes')
    for subtype in allSubtypes:
        subtypeNames[subtype['subtypeid']] = f'{subtype["genus"]} {subtype["species"]}'

    sortedMicrobeNames = {}
    for microbe in sortedMicrobes:
        sortedMicrobeNames[subtypeNames[microbe]] = sortedMicrobes[microbe]

    rank = list(sortedMicrobeNames.keys()).index(caseStudy[0])
    print(rank)
    ranks.append([caseStudy[0], rank])

f = open('ranks.txt', 'w+')
f.write(str(ranks))
f.close()