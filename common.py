'''

@author: aiman.najjar

Functions that are commonly used across the project

'''

import operator
import constants
import sys
import logging
import re
from HTMLParser import HTMLParser
from PorterStemmer import PorterStemmer


'''
MLStripper:
 An implementation of the HTMLParser class that returns only useful terms and discard other markup
 Initial skeleton of this implementation was obtained from the following StackOverflow page but was modified as per our needs:
 http://stackoverflow.com/questions/753052/strip-html-from-strings-in-python
'''

class MLStripper(HTMLParser):
    def __init__(self):
        self.reset()
        self.fed = []
        self.currentTag = ""
        self.currentAttrs = []
    def handle_starttag(self, tag, attrs):
        self.currentTag = tag
        self.currentAttrs = attrs
    def handle_endtag(self, tag):
        self.currentTag = ""
        self.currentAttrs = []
    def handle_data(self, d):

        if not self.currentTag in constants.IGNORE_TAGS:
            res = re.match( r"(.*http.*)", d.lower())
            if not res:
                self.fed.append(d)
        
    def get_data(self):
        return ''.join(self.fed)

# Convinent function to quickly invoke our special HTML parser
def strip_tags(html):
    s = MLStripper()
    try:
        html = html.decode('UTF-8')
    except UnicodeDecodeError, e:
        html = html

    s.feed(html)
    return s.get_data()

def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False



'''
getTopTerms:
    Given the current query and the new query vector, return the highest scoring terms (default 2 terms)
    The current query is used to ensure that returned terms are actually new
'''

def getTopTerms(currentQuery, weightsMap,topX=2):

    p = PorterStemmer()
    current_terms = []
    # for term in currentQuery.split():
    #     term = p.stem(term.lower(), 0,len(term)-1)
    #     current_terms.append(term)
        

    i = 0
    terms = []
    for term in sorted(weightsMap, key=weightsMap.get, reverse=True):
        if term in constants.QUERY_SKIP_TERMS or p.stem(term.lower(), 0,len(term)-1) in current_terms:
            continue
        terms.append(term)
        current_terms.append(p.stem(term.lower(), 0,len(term)-1))
        i = i + 1
        if (topX != 'ALL' and i >= topX):
            break;

    return terms


'''
printWeights:
    Given the new query vector, print out the highest scoring terms (default 10 terms)
    Used for debugging purposes only
'''
def printWeights(weightsMap,topX=10):
    i = 0
    for term in sorted(weightsMap, key=weightsMap.get, reverse=True):
        if term in constants.STOP_WORDS_LIST:
            continue        
        print "%-10s: %10f" % (term, weightsMap[term])
        i = i + 1
        if (topX != 'ALL' and i >= topX):
            break;


