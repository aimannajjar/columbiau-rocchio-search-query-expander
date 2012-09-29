import threading
import datetime
import settings
import re
import urllib2
import logging
from PorterStemmer import PorterStemmer
from common import *
from Queue import Queue
from tokenize import tokenize
from threading import Thread

class Indexer():


	def __init__(self):
		logging.info("Initializing indexer")
		self.ifile_lock = threading.Lock()
		self.documents_queue = Queue()
		self.invertedFile = dict()

		for i in range(settings.NUM_INDEXER_THREADS):
		    worker = Thread(target=self.index, args=(i, self.documents_queue,))
		    worker.setDaemon(False)
		    worker.start()		


	def indexDocument(self,document):
		self.documents_queue.put(document)


	def indexerIdle(self):
		return self.documents_queue.empty()

	def index(self, i, q):
		while True:
			logging.info('Indexer-%s: Waiting for next document' % i)
			document = q.get()

			logging.info('Indexer-%s: Indexing document #%s' % (i, document["ID"]))

			# Strip out HTML
			processed_body = strip_tags(document["body"])

			# Terms List
			terms = []

			# Tokenizer 
			logging.debug('Indexer-%s: Tokenizing document #%s' % (i, document["ID"]))
			tokens = re.compile(settings.DELIMITERS).split(processed_body)
			logging.debug('Indexer-%s: Found %d tokens' % (i, len(tokens)))
			j = 0


			# Process Tokens
			p = PorterStemmer()
			for token in tokens:

				
				logging.debug('Indexer-%s: Stemming token: \'%s\'' % (i, token))

				# Stem Token
				token = p.stem(token.lower(), 0,len(token)-1)				

				# Is token eligible to indexed?
				if (token == '' or len(token) <= 1 or is_number(token)):
					logging.debug('Indexer-%s: Discarding short or empty token \'%s\'' % (i, token))
					continue

				terms.append(token)

				# Insert into invertedFile
				with self.ifile_lock:
					logging.debug('Indexer-%s: Updating postings for token: %s' % (i, token))
					if not self.invertedFile.has_key(token):
						self.invertedFile[token] = { }

					if not self.invertedFile[token].has_key(document["ID"]):
						self.invertedFile[token][document["ID"]] = { }

					body_postings = []
					if self.invertedFile[token][document["ID"]].has_key("body"):
						body_postings = self.invertedFile[token][document["ID"]]["body"]
						body_postings.append(j)
					else:
						self.invertedFile[token][document["ID"]]["body"] = [j]


				j = j + 1

			logging.info('Indexer-%s: Finished indexing document %s' % (i, document["ID"]))
			q.task_done()



## TESTER ##
logging.basicConfig(level=logging.INFO)
logging.info("Starting Test")
url="http://docs.python.org/library/urllib.html"
req = urllib2.Request(url)
response = urllib2.urlopen(req)
body = response.read()

doc = { "ID": 4343, "body": body }		

indexer = Indexer()

indexer.indexDocument(doc)

