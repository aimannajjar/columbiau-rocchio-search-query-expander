# Rochhio Query Expansion Implementation
* COMS E6111 Advanced Database Systems (Fall 2012)
* Columbia University
* Done by:
	* Aiman Najjar (an2434)
	* John Terzis (jt2514)




1 . Installation & Usage:
--------------------------
Unpack archive and from the command line in a Linux machine run using Python 2.7.3+

	python main.py <precision> <query>

For example, suppose we want results relevant only to Bill Gates when we run the query 'gates' with target precision of 0.9:

	python main.py .90 'gates'
	
![screenshot query expansion example] (https://s3.amazonaws.com/aimannajjar.com/assets/images/portfolio/rocchio.png)

Initially, the web search will return various results, some of them are related to Bill Gates while others are related to the actual word "gate" (door). You will be prompted to indicate which results are relevant to your search. Go ahead and mark results related to Bill Gates as relevant, and everything else as irrelevant. The tool will perform another search but will augment your query with keywords it learned from the results you marked as relevant, by adding this keywords the next results will have higher precision. This will continue to iterate until the target precision has been achieved.


Various settings can be easily changed to experiment with results in __constants.py__



2 . Package Contents:
--------------------------
- \_\_init\_\_.py
- common.py
- constants.py
- indexer.py
- bingclient.py
- main.py
- parser.py
- PorterStemmer.py
- rocchio.py
- transcript.txt (Sample Output)

3. Disclosures:
--------------------------
- As explained in the respective files, we have used an existing Python implementation of PorterStemmer here:
http://www.tartarus.org/~martin/PorterStemmer
We do not use this stemmer in default settings (see constants.py)

- We have also used a code snippet from StackOverflow that parses HTML tags of an HTML document, but we've highly modified the snippet to suit our needs (see common.py)



4. Basic Algorithm and Data Structures
---------------------------------------

##	Algorithm: ##


	* Initialization (bing client, ...etc) //Initialize singletons here
	* For each round:
		1. Prompt user for input
		1. Use Bing API to retrieve top-10
		2. Present results to user and compute P = Precision @ 10
		3. While P < TARGET_VALUE:
				( More details of following steps can be found in the heading comments section of indexer.py file)
			* Crawl in each individual URL
			* We index the contents of all documents (Create the Inverted File)
				- Preprocessing:  Tokenize and eliminate useless terms (numbers and tokens of length 1)
				- Insert into invertedFile
				- Increment term frequency of this term in this document's vector representation
				( More details of following steps can be found in the heading comments section of rocchio.py file)
			* Build query vector (INITIALLY: 1 - if a term exists in query, 0 - otherwise)
			* Expand Query: Take 2 highest weighted non-stop word terms that are not part of current query using ROCCHIO ALGORITHM.



## Data Structures ##



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



# DocumentsList Structure

	[
		{   "ID" : 0,
			"Title": " from BING ",
			"Description" : ".... from BING ... "
		    "Body": "...",
		    "URL":"http://...."
		    "IsRelevant: True/False,
		    "tfVector": { "term1": term1_frequency, .... other terms }
		 },


		.
		.
		.
		other documents
	]

5. Algorithm & Design Explanation
---------------------------------------
Our design is structurally implemented using an object oriented model and separate components for the preprocessing stage, the index construction, and the query re-weighting. The code is setup as a python package as characterized by the __init__.py file in the source
folder. main.py parses the arguments to main and starts a main loop which retrieves a query from the Bing API via the bingClient object
, parses the returned JSON, and builds the invertedFile data structure for each query through worker threads created by Indexer which
wait for a shared queue resource of Documents (see above Document List data structure outline) to become populated, then grab a mutex to
dequeue the Document queue and index the document. During this indexing phase, the Porter Stemmer algorithm is optionally applied and the token is
inserted into the invertedFile, which is structured as a dictionary (outline above). In our design, we went the extra step and crawled into
the URL's indicated by each result from Bing's API, stripped html tags using common.py, and indexed the body of the html pages pointed to by
the URL's as well in order to obtain a more robust signal from each result than was presented by the Title/Summary alone. After the indexing phase completes per round, we apply the Rocchio algorithm using proprietary weights found in constants.py for alpha,beta,gamma optimized by
user tests to move the query vector towards the centroid of the desired result vector in the most expedient manner.

You'll notice that we are placing higher prioity for efficient and quick processing rather than efficient memory usage, our argument is that given the interactive nature of this application, quicker indexing (e.g. background concurrent threads) and quick access to terms weights (using hash maps with keys rather than arrays with common ordering of terms) is more important than efficient memory usage, furthermore, since the collection of documents (10) is small and the vocabulary for the collection is relatively small, this should not result in exteremly high usage of memory, that being said however, the application may not scale very well when attempting to work with much larger collections


Query-Modification method:
Our application is basically a straightforward implementation of Rocchio algorithm, we build a new invertedFile for each round. We do however perform some post-processing on the modified query vector returned by the algorithm. We have created a dictionary of common English stop words in constants.py, this dictionary, QUERY_SKIP_TERMS, represented the set of terms we would skip regardless of their weight from successive applications of the Rocchio algorithm each round. We found that at each round,
taking the 2 highest terms that did not intersect with QUERY_SKIP_TERMS would provide the best augmented query given beta,gamma all
equal to 1.0 and alpha given 0. Our reasoning for setting alpha to 0 is that we would like to eliminate existing query terms before deciding what next (augmentation) will be. By weighing Beta and Gamma such high values, we were placing more importance on the user feedback and increasing the velocity
at which 'relevant' terms distinguish from 'non-relevant' terms as evidenced by the absolute value of their difference in weights. To the
extent that the user feedback accurately reflects the intended results of the query, we move the query vector more rapidly towards the
centroid of relevant results.

