import operator
from HTMLParser import HTMLParser

class MLStripper(HTMLParser):
    def __init__(self):
        self.reset()
        self.fed = []
    def handle_data(self, d):
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

def printWeights(weightsMap,topX=10):
    i = 0
    for term in sorted(weightsMap, key=weightsMap.get, reverse=True):        
        print "%-10s: %10f" % (term, weightsMap[term])
        i = i + 1
        if (topX != 'ALL' and i >= topX):
            break;
