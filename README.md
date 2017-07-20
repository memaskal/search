* The implementation follows the general idea of the below link:
	> http://aakashjapi.com/fuckin-search-engines-how-do-they-work/

* There are 3 major stages in developing a search engine:
	1) Finding/Crawling the Data
	2) Building the index,
	3) Using the index to answer queries
	- On top of this, we can add result ranking (tf-idf, PageRank, etc), query/document classification and maybe some Machine Learning to keep track of user's past queries and selected results to improve the search engine's  performance. 
	- Download Project Gutenbergs TOP 600 April's 2003 e-books in .txt format from the undermentioned links:
		http://www.gutenberg.org/wiki/Gutenberg:The_CD_and_DVD_Project:			(The CD and DVD Project)
		ftp://ftp.ibiblio.org/pub/docs/books/gutenberg/1/1/2/2/11220/			(August 2003 CD)

* You can run each script with --help
	$ ./Desktop/results/se/BuildIndex.py --help
	usage: BuildIndex.py [-h] [-I INPUT_DIR] [-O OUTPUT_DIR]

	Script's objective is to assembly the inverted index of a given document
	collection.

	optional arguments:
	  -h, --help            show this help message and exit
	  -I INPUT_DIR, --input_dir INPUT_DIR
	                        The directory path of the document collection.
	                        Default:/home/gpispi/Desktop/results/se/books
	  -O OUTPUT_DIR, --output_dir OUTPUT_DIR
	                        The output directory path where the inverted file is
	                        going to be exported in JSON format. Default:
	                        (/home/gpispi/Desktop/results/se

	$ ./QueryIndex.py --help
	usage: QueryIindex.py [-h] [-I INPUT_FILE]

	Script's objective is to query the Inverted File constructed previously after
	executing BuildIndex script.

	optional arguments:
	  -h, --help            show this help message and exit
	  -I INPUT_FILE, --input_file INPUT_FILE
	                        The file path of the Inverted File constructed from
	                        BuildIndex. Default:/home/gpispi/Desktop/results/se/in
	                        verted_file.txt

* Usefull links:
	- Nltk installation and usage:
		> https://www.quora.com/How-do-I-install-NLTK-on-Ubuntu
		> http://stackoverflow.com/questions/26693736/nltk-and-stopwords-fail-lookuperror
		> http://www.nltk.org/howto/wordnet.html
		> https://pythonprogramming.net/wordnet-nltk-tutorial/
	- Search Engines General:
		> https://www.reddit.com/r/learnpython/comments/3ikd9f/creating_a_search_engine_in_python/
		> http://infolab.stanford.edu/%7Ebackrub/google.html
		> http://www.zackgrossbart.com/hackito/search-engine-python/
		> https://pythonformachinelearning.wordpress.com/






