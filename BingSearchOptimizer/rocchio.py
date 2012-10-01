'''
Implement Rocchio algo on a corpus of relevant documents
by weighting based on td-idf to iteratively form a new query vector of weightings
for each unique term across all dictionaries (from invertedFiles) passed into Rocchio
'''
import constants

class RocchioOptimizeQuery:



    def __init__(self, firstQueryTerm):
        '''
        Constructor
        '''
        self.query = {}
        self.query[firstQueryTerm] = 1
     
        
    def Rocchio(self, invertedFile, numberRelDoc):
        '''
        'output new query vector'
        
        'calculate IDF per inverted file'
        'calculate TF per inverted file'
        
        'generate weight vector for relevant terms'
        '''
        weights = {}
        for key in invertedFile.iterkeys():
            weights[key] = 0    #initialize weight vector for each key in inverted file
        print ''
        print '[Rocchio]: printing weights'
        print weights
        for key in invertedFile.iterkeys():
            for subkey in invertedFile[key].iterkeys():
                #were only looking at terms found in body!
                weights[key] = weights[key] + len(invertedFile[key][subkey]['body'])  #term freq. per document body
            weights[key] = (constants.beta * weights[key]) / (numberRelDoc * len(invertedFile[key])) #divide final weight of term by its current IDF
    
            if key in self.query:
                self.query[key] = constants.alpha * self.query[key] + weights[key]   #build new query vector of weights
            else:
                self.query[key] = weights[key]
                
        return self.query
    
            
        
        
    