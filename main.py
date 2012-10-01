'''
Created on Sep 21, 2012

@author: johnterzis

arguments: <precision> <query>
'''

import json
import sys
import bingclient
import constants
import parser
import constants
import logging
import indexer
import rocchio
import common


#were using pybing wrapper for bing search api
#from pybing import Bing



#only if run as standalone script (not imported module) does, __name__  attribute defaults to __main__
#assume first arg is <precision> second is <query>
if __name__ == '__main__':

    logging.basicConfig(level=logging.ERROR)

#create all singleton objects
    arglist = sys.argv 
    if len(arglist) < 3:
        print "Usage: <precision> <query>"
        sys.exit(1) #exit interpreter
    
    print 'Desired precision@10: {}'.format(arglist[1])

    precisionTenTarg = float(arglist[1])   #must convert string to float
    #'eECeOiLBFOie0G3C03YjoHSqb1aMhEfqk8qe7Xi2YMs='
    #connect to client with key arg[1] and post a query with arg[3], query

    bingClient = bingclient.BingClient(constants.BING_ACCT_KEY)
    indexerWorker = indexer.Indexer()
    queryOptimizer = rocchio.RocchioOptimizeQuery(arglist[2])
    
    firstPass = 1
    precisionAtK = 0.00
    expandedQuery = '' 
    queryWeights = {} 

    
    #while precision at 10 is less than desired amt issue a query, obtain new precision metric, expand query, repeat
    while (precisionAtK < precisionTenTarg):
        relDocCount = 0
        precisionAtK = 0.00 #reset precision each round
        #PROCESS A QUERY

        print 'Searching...'
        if firstPass == 1:
            result = bingClient.webQuery(arglist[2])
        else:
            result = bingClient.webQuery(expandedQuery)
            
        jsonResult = json.loads(result)  #convert string to json
        #put result into a list of documents
        parsedResult = parser.Parser(jsonResult['d']['results'])
        parsedResult.parser()
        DocumentList = parsedResult.getDocList()
                
        
        #to calc precision@10 display documents to user and ask them to categorize as Relevant or Non-Relevant
        print 'Please rank the following 10 documents returned based on the binary classification: R for Relevent, NR for Nonrelevant'
        print ''
        for i in range(len(DocumentList)):

            DocumentList[i]["ID"] = str(i)
            indexerWorker.indexDocument(DocumentList[i])


            print '------------------------------------'
            print ''

            print'%-15s: %10s' % ("TITLE", DocumentList[i]["Title"])
            print'%-15s: %10s' % ("DESCRIPTION", DocumentList[i]["Description"])
            print'%-15s: %10s' % ("URL", DocumentList[i]["Url"])            

            print ''
            print 'Relevant (R) or Non-Relevant (NR): '
            value = raw_input("Prompt:")
            if value == 'R':
                DocumentList[i]['IsRelevant'] = 1   #1 is true , 0 is false
                precisionAtK = precisionAtK + 1
                relDocCount = relDocCount + 1   
                
            elif value == 'NR':
                DocumentList[i]['IsRelevant'] = 0   #1 is true , 0 is false
            else:
                print 'Invalid value entered!'
        

        
        precisionAtK = float(precisionAtK) / 10  #final precision@10 per round
        
        print ''
        print 'Precision@10 is: {}'.format(float(precisionAtK))
        # print ''
        # if indexerWorker.indexerIdle:
        #     print indexerWorker.invertedFile
        # print ''
        # print 'Inverted Index Printed'

        
        #expand query here by indexing and weighting current document list
        if (precisionAtK < precisionTenTarg):
            queryWeights = queryOptimizer.Rocchio(indexerWorker.invertedFile, relDocCount)   #optimize new query here 
        print ''
        
        common.printWeights(queryWeights)

            
    
    #precision@10 is > desired , return query and results to user 
    print 'Achieved desired precision! Here are the results again:'
    print ''
    for i in range(len(DocumentList)):
        print '------------------------------------'
        print'%-15s: %10s' % ("TITLE", DocumentList[i]["Title"])
        print'%-15s: %10s' % ("DESCRIPTION", DocumentList[i]["Description"])
        print'%-15s: %10s' % ("URL", DocumentList[i]["Url"])            
        relevant = "Relevant"
        if not DocumentList[i]["IsRelevant"]:
            relevant = "Non-Relevant"
        print 'Your marked this as: %s' % relevant
        print ''
            
        
        
    
  
    
    