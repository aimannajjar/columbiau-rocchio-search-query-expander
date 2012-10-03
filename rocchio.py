'''
Implement Rocchio algo on a corpus of relevant documents
by weighting based on td-idf to iteratively form a new query vector of weightings
for each unique term across all dictionaries (from invertedFiles) passed into Rocchio
'''
import constants
import math
import sys
import PorterStemmer

class RocchioOptimizeQuery:



    def __init__(self, firstQueryTerm):
        '''
        Constructor
        '''
        self.query = {}
        self.query[firstQueryTerm] = 1
     
        
    def Rocchio(self, invertedFile, documentsList, relevantDocs, nonrelevantDocs):
        '''
        output new query vector'
        
        calculate summation of relevant documents weights 
        'calculate IDF per inverted file'
        

        '''
        p = PorterStemmer.PorterStemmer()

        weights = {}
        for term in invertedFile.iterkeys():
            sterm = term
            if constants.STEM_IN_ROCCHIO:
                sterm = p.stem(term.lower(), 0,len(term)-1)            
            weights[sterm] = 0.0    #initialize weight vector for each key in inverted file
        print ''

        relevantDocsTFWeights = {}
        nonrelevantDocsTFWeights = {} 

        # ------------------------------------- #
        # Compute relevantDocsTFWeights and nonrelevantDocsTFWeights vectors
        for docId in relevantDocs:
            doc = documentsList[docId]
            for term in doc["tfVector"]:
                sterm = term
                if constants.STEM_IN_ROCCHIO:
                    sterm = p.stem(term.lower(), 0,len(term)-1)

                if sterm in relevantDocsTFWeights:
                    relevantDocsTFWeights[sterm] = relevantDocsTFWeights[sterm] + doc["tfVector"][term]
                else:
                    relevantDocsTFWeights[sterm] = doc["tfVector"][term]

        
        for docId in nonrelevantDocs:
            doc = documentsList[docId]
            for term in doc["tfVector"]:
                sterm = term
                if constants.STEM_IN_ROCCHIO:
                    sterm = p.stem(term.lower(), 0,len(term)-1)                

                if sterm in nonrelevantDocsTFWeights:
                    nonrelevantDocsTFWeights[sterm] = nonrelevantDocsTFWeights[sterm] + doc["tfVector"][term]
                else:
                    nonrelevantDocsTFWeights[sterm] = doc["tfVector"][term]


        # ------------------------------------- #
        # Compute Rocchio vector
        for term in invertedFile.iterkeys():
            idf = math.log(float(len(documentsList)) / float(len(invertedFile[term].keys())), 10)


            sterm = term
            if constants.STEM_IN_ROCCHIO:
                sterm = p.stem(term.lower(), 0,len(term)-1)


            # Terms 2 and 3 of Rocchio algorithm
            for docId in invertedFile[term].iterkeys():
                if documentsList[docId]['IsRelevant'] == 1:
                    # Term 2: Relevant documents weights normalized and given BETA weight
                    weights[sterm] = weights[sterm] + constants.BETA * idf * (relevantDocsTFWeights[sterm] / len(relevantDocs))
                else:
                    # Term 3: NonRelevant documents weights normalized and given BETA weight
                    weights[sterm] = weights[sterm] - constants.GAMMA * idf * (nonrelevantDocsTFWeights[sterm]/len(nonrelevantDocs))

            # Term 1 of Rocchio, query terms
            if term in self.query:
                self.query[term] = constants.ALPHA * self.query[term] + weights[sterm]   #build new query vector of weights
            elif weights[sterm] > 0:
                self.query[term] = weights[sterm]

        return self.query
    
            
        
        
    