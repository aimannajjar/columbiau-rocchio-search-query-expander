'''
Created on Sep 21, 2012

@author: johnterzis

BingClient takes in an Account Key to its ctor and exposes web search query
method to client that is a wrapper of Bing Search API 1.0

Parameters are standardized based on assignment requirements and query returns
top 10 results only, in JSON format
'''

import json
import urllib
import urllib2
import constants
import base64
import logging

class BingClient:
    '''
    classdocs
    '''
    def __init__(self, AccountKey=None):
        '''
        Constructor
        '''
       
        #enfore pseudo privacy of account key member with __ prefix
        self.__i_accountKey = AccountKey
        
        if self.__i_accountKey == None:
            logging.error('Account Key is NULL!!!')
     
    #send a web query to Bing Search API returning top 10 results as json   
    def webQuery(self, query):
        #format query based on OData protocol and desired JSON format of results
        url_query = 'Query=' + '%27' + query.replace(' ', '+') + '%27' + '&$top=10&$format=JSON'
        #encode account key
        logging.debug('Account Key: ' + self.__i_accountKey)
        
        accountKeyEnc = base64.b64encode(self.__i_accountKey + ':' + self.__i_accountKey)
        headers = {'Authorization': 'Basic ' + accountKeyEnc}
        full_query = constants.BING_URL + url_query
        logging.debug('Sending following URL query: ' + full_query)

        print '%-20s= %s' % ("URL", full_query)

        req = urllib2.Request(full_query, headers = headers)

        #open url and store response in json file
        response = urllib2.urlopen(req)
        content = response.read()
        logging.debug("Bing Retured: %s" % content)
        #return json response from Bing. 
      
        return content
        
        
        
        
           
        
    
        