from main_algorithm import *

f = open('caseStudies.txt', 'r')
caseStudies = eval(f.read())
f.close()

f = open('allMicrobeData.txt', 'r')    #get symptom and test results
allMicrobeSymptoms, allMicrobeTestResults, allMicrobeRiskFactors, symptomRatios, microbeTypes = eval(f.read())
f.close()

ranks = []
averageRank = 0
averageBacteriaRank = 0
averageVirusRank = 0
averageFungiRank = 0
bacteriaCount = 0
virusCount = 0
fungiCount = 0
notFoundCount = 0

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

    try: 
        rank = list(sortedMicrobeNames.keys()).index(caseStudy[0]) + 1
    except:
        rank = -1
    print(rank)
    if rank != -1:
        averageRank += rank
        if caseStudy[2] == 'bacteria':
            averageBacteriaRank += rank
            bacteriaCount += 1
        if caseStudy[2] == 'virus':
            averageVirusRank += rank
            virusCount += 1
        if caseStudy[2] == 'fungi':
            averageFungiRank += rank
            fungiCount += 1
    else:
        notFoundCount += 1
    ranks.append([caseStudy[0], rank])

averageRank /= len(caseStudies) - notFoundCount
averageBacteriaRank /= bacteriaCount
averageVirusRank /= virusCount
averageFungiRank /= fungiCount
print(averageRank)
ranks.append(["Average Rank", averageRank])
ranks.append(["Bacteria Average Rank", averageBacteriaRank])
ranks.append(["Virus Average Rank", averageVirusRank])
ranks.append(["Fungi Average Rank", averageFungiRank])

f = open('ranks.txt', 'a+')
f.write(str(ranks) + '\n')
f.close()