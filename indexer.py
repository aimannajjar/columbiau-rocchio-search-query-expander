'''
Created on Sep 21, 2012

@author: aiman.najjar

This class is resposible for indexing the documents and it performs the following steps:
	1. Retrieves the body content of the document, if the HTTP request fails, the body summary returned in Bing API is used
	2. Tokenize the document text based on constants.DELIMITERS regular expression
	3. OPTIONAL: Stem token (default is False, setting can be changed in constants.py)
	4. Throw away out terms that are likely to be useless (e.g. length is 1 or numerical only)
	5. Insert into invertedFile
	6. In the same pass, we compute term frequencies for each term in d and store the weight in document["tfVector"][term], this is useful later for Rocchio

Note that this indexer is setup to work concurrently and dynamically build the index as opposed to index the document collections at once.
To index a document, the document object should be enqueued in documents_queue and one of the worker threads will be pick it up to process it
Therefore, a mutex lock was necessary while accessing invertedFile to ensure dictionary consistency

Here is the invertedFile structure:

	invertedFile =
	{

		"Term 1" : {
			"DocID 1" : 
			{
				"body": [0,3,4,2,1] # List of positions
				.
				.
				other zones (currently only indexing body)
			}
			
			.
			.
			.
			other documents 

		}

		.
		.
		.
		.
		other terms

	}


You will notice our liberal usage of hash maps which are convenient for quick access but consume larger memory, we explain our design choice in the README file


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
		self.termsFrequencies = dict()

		for i in range(constants.NUM_INDEXER_THREADS):
		    worker = Thread(target=self.index, args=(i, self.documents_queue,))
		    worker.setDaemon(True)
		    worker.start()		


	# Enqueues a task in the indexer queue
	def indexDocument(self,document):
		self.documents_queue.put(document)


	def waitForIndexer(self):
		self.documents_queue.join()

	def clearIndex(self):
		with self.ifile_lock:
			self.invertedFile = dict()
			self.termsFrequencies = dict()


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

			try:
				response = urllib2.urlopen(req)
				body = response.read()
				# Strip out HTML
				document["Body"] = strip_tags(body)				
			except Exception, e:
				document["Body"] = document["Description"]


			# Terms List
			terms = []

			# Tokenizer 
			logging.debug('Indexer-%s: Tokenizing document #%s' % (i, document["ID"]))
			tokens = re.compile(constants.DELIMITERS).split(document["Body"])
			logging.debug('Indexer-%s: Found %d tokens' % (i, len(tokens)))
			j = 0


			# Process Tokens
			p = PorterStemmer()
			for token in tokens:

				# Stem Token
				if (constants.STEM_TOKEN):
					logging.debug('Indexer-%s: Stemming token: \'%s\'' % (i, token))
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

					if not token in self.termsFrequencies:
						self.termsFrequencies[token] = 1
					else:
						self.termsFrequencies[token] = self.termsFrequencies[token] + 1

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

