'''
Created on Sep 21, 2012

@author: aiman.najjar

'''

import threading
import datetime
import re
import urllib2
import logging
import constants
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

		for i in range(constants.NUM_INDEXER_THREADS):
		    worker = Thread(target=self.index, args=(i, self.documents_queue,))
		    worker.setDaemon(True)
		    worker.start()		


	# Enqueues a task in the indexer queue
	def indexDocument(self,document):
		self.documents_queue.put(document)


	def waitForIndexer(self):
		self.documents_queue.join()

	def index(self, i, q):
		while True:
			logging.info('Indexer-%s: Waiting for next document' % i)
			document = q.get()

			logging.info('Indexer-%s: Indexing document #%s (%s)' % (i, document["ID"], document["Url"]))

			# Create key to hold tf weights
			document["tfVector"] = { }

			# Retrive Entire document
			url=document["Url"]
			req = urllib2.Request(url)
			req.add_header('User-Agent', 'QueryOptimizer') 
			response = urllib2.urlopen(req)
			body = response.read()			
			document["Body"] = body
			# Strip out HTML
			processed_body = strip_tags(document["Body"])
			document["ProcessedBody"] = processed_body

			# Terms List
			terms = []

			# Tokenizer 
			logging.debug('Indexer-%s: Tokenizing document #%s' % (i, document["ID"]))
			tokens = re.compile(constants.DELIMITERS).split(processed_body)
			logging.debug('Indexer-%s: Found %d tokens' % (i, len(tokens)))
			j = 0


			# Process Tokens
			p = PorterStemmer()
			for token in tokens:

				
				logging.debug('Indexer-%s: Stemming token: \'%s\'' % (i, token))

				# Stem Token
				if (constants.STEM_TOKEN):
					token = p.stem(token.lower(), 0,len(token)-1)				
				else:
					token = token.lower()

				# Is token eligible to indexed?
				if (token == '' or len(token) <= 1 or len(token) >= 10 or is_number(token)):
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

					if (token in document["tfVector"]):
						document["tfVector"][token] = document["tfVector"][token] + 1
					else:
						document["tfVector"][token] = 1


				j = j + 1

			logging.info('Indexer-%s: Finished indexing document %s' % (i, document["ID"]))
			q.task_done()

