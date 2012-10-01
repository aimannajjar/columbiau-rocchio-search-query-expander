import operator
import constants
import sys
import logging
import re
from HTMLParser import HTMLParser

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

def getTopTerms(weightsMap,topX=2):
    i = 0
    terms = []
    for term in sorted(weightsMap, key=weightsMap.get, reverse=True):
        if term in constants.STOP_WORDS_LIST:
            continue
        terms.append(term)
        i = i + 1
        if (topX != 'ALL' and i >= topX):
            break;

    return terms

def printWeights(weightsMap,topX=10):
    i = 0
    for term in sorted(weightsMap, key=weightsMap.get, reverse=True):
        if term in constants.STOP_WORDS_LIST:
            continue        
        print "%-10s: %10f" % (term, weightsMap[term])
        i = i + 1
        if (topX != 'ALL' and i >= topX):
            break;
