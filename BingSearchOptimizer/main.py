'''
Created on Sep 21, 2012

@author: johnterzis

arguments: <bing account key> <precision> <query>
'''

import json
import sys
import bingclient
import constants
import parser
import indexer
import rocchio




#were using pybing wrapper for bing search api
#from pybing import Bing



#only if run as standalone script (not imported module) does, __name__  attribute defaults to __main__
#assume first arg is <bing acct key> second is <precision> third is <query>
if __name__ == '__main__':

#create all singleton objects
    arglist = sys.argv 
    if len(arglist) < 4:
        print "Missing Arguments!"
        sys.exit(1) #exit interpreter
    
    print 'desired precision@10: {}'.format(arglist[2])
    precisionTenTarg = float(arglist[2])   #must convert string to float
    #'eECeOiLBFOie0G3C03YjoHSqb1aMhEfqk8qe7Xi2YMs='
    #connect to client with key arg[1] and post a query with arg[3], query
    bingClient = bingclient.BingClient(arglist[1])
    indexerWorker = indexer.Indexer()
    queryOptimizer = rocchio.RocchioOptimizeQuery(arglist[3])
    
    firstPass = 1
    precisionAtK = 0.00
    expandedQuery = '' 
    queryWeights = {} 
    
    #while precision at 10 is less than desired amt issue a query, obtain new precision metric, expand query, repeat
    while (precisionAtK < precisionTenTarg):
        relDocCount = 0
        precisionAtK = 0.00 #reset precision each round
        #PROCESS A QUERY
        if firstPass == 1:
            result = bingClient.webQuery(arglist[3])
        else:
            result = bingClient.webQuery(expandedQuery)
            
        jsonResult = json.loads(result)  #convert string to json
        print 'found query'
        #put result into a list of documents
        parsedResult = parser.Parser(jsonResult['d']['results'])
        parsedResult.parser()
        DocumentList = parsedResult.getDocList()
        print DocumentList
                
        
        #to calc precision@10 display documents to user and ask them to categorize as Relevant or Non-Relevant
        print 'Please rank the following 10 documents returned based on the binary classification: R for Relevent, NR for Nonrelevant'
        for i in range(len(DocumentList)):
            print DocumentList[i]

            
            print ''
            print 'Relevant or NonRelevant: '
            value = raw_input("Prompt:")
            if value == 'R':
                DocumentList[i]['IsRelevant'] = 1   #1 is true , 0 is false
                precisionAtK = precisionAtK + 1
                relDocCount = relDocCount + 1   
                
                #index only each Relevant document in document list
                indexerWorker.indexDocument(DocumentList[i])
            elif value == 'NR':
                DocumentList[i]['IsRelevant'] = 0   #1 is true , 0 is false
            else:
                print 'Invalid value entered!'
        

        
        precisionAtK = float(precisionAtK) / 10  #final precision@10 per round
        
        print ''
        print 'Precision@10 is: {}'.format(float(precisionAtK))
        print ''
        if indexerWorker.indexerIdle:
            print indexerWorker.invertedFile
        print ''
        print 'Inverted Index Printed'
        
        #expand query here by indexing and weighting current document list
        if (precisionAtK < precisionTenTarg):
            queryWeights = queryOptimizer.Rocchio(indexerWorker.invertedFile, relDocCount)   #optimize new query here 
        print ''
        print 'printings new query weights: {}'.format(queryWeights)   

            
    
    #precision@10 is > desired , return query and results to user 
    print DocumentList
            
        
        
    
  
    
    