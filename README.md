## Simple search engine with TF-IDF ranking

This project started as a simple search engine following the general idea of this [blog post](http://aakashjapi.com/fuckin-search-engines-how-do-they-work/). A starting point implementation was given in Python and can be found [here](./original-src). The task was to make fitted changes to optimize the given implementation. A walkthrough of all the changes are described in the [report.pdf](./report.pdf), currently in Greek.  

## Search engines

There are 3 major stages in developing a search engine:
1) Finding/Crawling the Data
2) Building the index
3) Using the index to answer queries

> On top of this, we can add result ranking (tf-idf, PageRank, etc), query/document classification and maybe some Machine Learning to keep track of user's past queries and selected results to improve the search engine's performance.

### Indexer

The Indexer was benchmarked using a small random [book](./books) subset from the Project Gutenberg collection. The improvements made to the Indexer are:

1) Static lists to sets conversion, for faster searches. *Speedup:* +5%
2) Precompiled Regex, for faster matches. *Speedup:* +2%
3) Stopword removal using [Modified Penn Treebank Tag-Set2](http://www.infogistics.com/tagset.html) closed class 
categories. *Inverted Index size:* -5%
4) Multi-process parallel Indexer with 2 worker processes. *Speedup:* +50%
5) Serialize inverted index as Pickle file. *Inverted Index size:* -30%
6) Apply D-Gap encoding. *Inverted Index size:* -25%

The overall performance for (P = 2) worker processes, is a 2.68 speedup and a -52% reduction in the Inverted Index file size, compared to the original implementation. To get help on the Indexer sub system’s execution arguments, type the following command in the projects' directory:

```bash
$ python BuildIndex.py --help
```

### Query

The Query sub system, uses the inverted Index, and supports standard and phrase queries, with tf-idf rankings. To get help on the Query sub system's execution arguments, type the following command in the projects' directory:

```bash
$ python QueryIndex.py --help
```

### Recommender

A proof of concept, Recommender sub-system, was created for the Gutenberg collection's books. The first, is independent of this implementation, but can easily be adapted to work with the Query sub-system. The provided recommendations are based on other users' ratings on the books (collaborative filtering). The similarity of the users is calculated using the Pearson correlation coefficient. 

The books' ratings were created randomly and a book index was created by parsing the master_list.csv located in the books directory. The last, contains the title, author, id etc. information for all the downloaded books. To execute the Recommender sub-system type the following command in the projects’ directory:

```bash
$ python Recommender.py
```

### Crawler

The crawler sub-system uses the [Scrapy](https://scrapy.org/) web crawling framework. A custom spider was created, to parse the project Gutenberg's website and download books. A custom Book item was created to represent the new entities and a MySQL pipeline was used to insert the books in a database. The books later, can be inputted to the Indexer with some minor changes.

The database credentials as well as the crawler's configuration are located in the crawler/settings.py configuration file. To run the crawler, execute the following commands in the project's directory:

```bash
$ cd crawler
$ srcapy crawl gutenberg
# Setting crawler's max pages = 3 
$ srcapy crawl gutenberg -a maxpages=3
```


## Useful Links
* Nltk installation and usage:
    - https://www.quora.com/How-do-I-install-NLTK-on-Ubuntu
    - http://stackoverflow.com/questions/26693736/nltk-and-stopwords-fail-lookuperror
    - http://www.nltk.org/howto/wordnet.html
    - https://pythonprogramming.net/wordnet-nltk-tutorial/
* Search Engines General:
    - https://www.reddit.com/r/learnpython/comments/3ikd9f/creating_a_search_engine_in_python/
    - http://infolab.stanford.edu/%7Ebackrub/google.html
    - http://www.zackgrossbart.com/hackito/search-engine-python/
    - https://pythonformachinelearning.wordpress.com/
* Project Gutenberg’s TOP 600 April's 2003 e-books in .txt format:
    - ftp://ftp.ibiblio.org/pub/docs/books/gutenberg/1/1/2/2/11220/	(August 2003 CD)

