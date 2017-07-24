#!/usr/bin/python
# BuildIndex: Assembly the Inverted Index. Bear in mind that inverted index is the data structure that maps tokens to the documents they appear in.
# http://aakashjapi.com/fuckin-search-engines-how-do-they-work/

import os
import re
import sys
import pickle
import time
import argparse

from multiprocessing import Pool, Manager				# Multiprocessing

from nltk import pos_tag
from nltk.corpus import stopwords
from nltk.tokenize import WordPunctTokenizer
from nltk.stem.wordnet import WordNetLemmatizer


# English stop words list to set
stop_words = set(stopwords.words('english'))

# shared memory objects
inverted_file = None									# The Inverted File data structure
inv_lock = None											# The data structure lock

wp_tokenizer = WordPunctTokenizer()						# Tokenizer instance
wnl_lemmatizer = WordNetLemmatizer()					# Wordnet Lemmatizer instance

total_doc_cnt = 0										# Total number of indexed documents
indexed_words = 0										# Total (corpus) number of indexed terms
excluded_words = 0										# Total (corpus) number of exluded terms

# closed tag set http://www.infogistics.com/tagset.html
CLOSED_TAGS = {'CD', 'CC', 'DT', 'EX', 'IN', 'LS', 'MD', 'PDT', 'POS', 'PRP', 'PRP$', 'RP', 'TO', 'UH', 'WDT', 'WP', 'WP$', 'WRB'}


def set_argParser():
	""" The build_index script's arguments presentation method."""
	argParser = argparse.ArgumentParser(description="Script's objective is to assembly the inverted index of a given document collection.")
	argParser.add_argument('-I', '--input_dir', type=str, default=os.path.dirname(os.path.realpath(__file__)) + os.sep + 'books', help='The directory path of the document collection. Default:' + os.path.dirname(os.path.realpath(__file__)) + os.sep + 'books')
	argParser.add_argument('-O', '--output_dir', default=os.path.dirname(os.path.realpath(__file__)), type=str, help='The output directory path where the inverted file is going to be exported in JSON format. Default: (' + os.path.dirname(os.path.realpath(__file__)))
	argParser.add_argument('-P', '--process_cnt', default=1, type=int, help='The number of worker processes. Default: 1')
	return argParser



def check_arguments(argParser):
	""" Parse and check the inserted command line args."""
	line_args = argParser.parse_args()

	# 'input_dir' line argument handling
	if (not(os.path.exists(os.path.realpath(line_args.input_dir)))) :
		line_args.input_dir = os.path.dirname(os.path.realpath(__file__)) + os.sep + 'books'
	if (not(line_args.input_dir.endswith(os.sep))):
		line_args.input_dir += os.sep

	# 'output_dir' line argument handling
	if (not(os.path.exists(os.path.realpath(line_args.output_dir)))) :
		line_args.output_dir = os.path.dirname(os.path.realpath(__file__))
	if (not(line_args.output_dir.endswith(os.sep))):
		line_args.output_dir += os.sep
	
	# processes
	line_args.process_cnt = int(line_args.process_cnt)
	if (line_args.process_cnt < 1):
		line_args.process_cnt = 1
	return line_args



def export_output(output_dir):
	""" Export the Inverted File structure to a picle file."""
	global inverted_file
	
	filename = output_dir + 'inverted_file.pickle'
	with open(filename, 'wb') as handle:
		pickle.dump(inverted_file.copy(), handle, protocol=pickle.HIGHEST_PROTOCOL)



def calculate_tfidf():
	""" Calculate the TF * IDF per lemma."""
	global inverted_file
	
	# get local copy of dictionary
	inv_local = inverted_file.copy()	
	for lemma in inv_local:
		# Inverted document frequency = Total number of documents / Number of documents appeared
		idf = total_doc_cnt / len(inv_local[lemma]['il'])

		for docid in inv_local[lemma]['il']:
			# Inverted List subdictionary structure:
			#    <key>    :                              <value>
			# Document id : (Term's frequency, [Term's order of appearance list], Tf * IDf)
			inv_local[lemma]['il'][docid].append(inv_local[lemma]['il'][docid][0] * idf)
	
	#set the new dictionary
	inverted_file = inv_local


def update_inverted_index(existing_lemmas, docid):
	""" Update the Inverted File structure.."""
	global inverted_file, inv_lock
	
	# acquire shared lock
	inv_lock.acquire()
	inv_local = inverted_file.copy()

	for lemma in existing_lemmas:
		if lemma not in inv_local:
			# The following labels are exported per each term to the JSON file => For compactness, we have to keep them short.
			# tdc: Total document frequency in corpus
			# twc: Total word/term frequency in corpus
			#  il: Word/Term's Inverted List
			inv_local[lemma] = {}
			inv_local[lemma]['tdc'] = 1
			inv_local[lemma]['twc'] = len(existing_lemmas[lemma])
			inv_local[lemma]['il'] = {}
		else :
			inv_local[lemma]['tdc'] += 1
			inv_local[lemma]['twc'] += len(existing_lemmas[lemma])

		# Inverted List subdictionary structure:
		#    <key>    :                              <value>
		# Document id : (Term's frequency in current document, [Term's order of appearance list])
		inv_local[lemma]['il'][docid] = [len(existing_lemmas[lemma]), existing_lemmas[lemma]]
	
	inverted_file.update(inv_local)
	# release shared lock
	inv_lock.release()

		

def parse_file(args):
	""" Parse a single file object """
	# unpack arguments
	input_dir, file = args
	
	# local counter copies 
	_idx_words = 0
	_exc_words = 0
	
	pattern = re.compile(r'[\W_]+')								# compile pattern once, use it every time (If includes a non-letter character)
	docid = re.sub(r'\.txt$', '', file)							# Document's ID -String-
	existing_lemmas = {}										# Dictionary with the document's lemmas
	
	with open(input_dir + file, "r") as fh:
		
		tick = time.time()
		print "Pid: " + str(os.getpid()) + " processing: " + input_dir + file,

		word_cnt = 0 		# Our inverted index would map words to document names but, 
							# we also want to support phrase queries: queries for not only words, but words in a specific sequence => 
							# We need to know the order of appearance.

		for line in fh:
			for word, pos in pos_tag(wp_tokenizer.tokenize(line.lower().strip())):					
				if (
					pos in CLOSED_TAGS or						# search the closed tag set O(1)
					pattern.search(word) or						# If includes a non-letter character
					word in stop_words							# search for stop words O(1)
				):
					_exc_words += 1								# Increment the local copy of excluded words
					continue
				
				pos = 'v' if (pos.startswith('VB')) else 'n'	# If current term's appearance is verb related then 
																# the POS lemmatizer should be verb ('v'), otherwise ('n')
				lemma = wnl_lemmatizer.lemmatize(word, pos)		# Stemming/Lemmatization

				if (lemma not in existing_lemmas):
					existing_lemmas[lemma] = []

				existing_lemmas[lemma].append(word_cnt)			# Keep lemma's current position
				
				word_cnt 	+= 1								# Increment the position pointer by 1
				_idx_words 	+= 1								# Increment the local copy of indexed words count


		# Update the Inverted File structure with current document information
		update_inverted_index(existing_lemmas, docid)
		
		print "({0:>6.2f} sec)".format(time.time() - tick)
		return (_idx_words, _exc_words)

		
		
if (__name__ == "__main__") :

	argParser = set_argParser()									# The argument parser instance
	line_args = check_arguments(argParser)						# Check and redefine, if necessary, the given line arguments 
		
	# -------------------------------------------------------------------------------
	# Text File Parsing
	# -----------------	
	
	# skip non txt files
	files = [(line_args.input_dir, file) for file in os.listdir(line_args.input_dir) if file.endswith(".txt")] 

	# Set the number of files
	total_doc_cnt = len(files)															
	
	# create a new manager object for the shared dictionary, lock
	m = Manager()
	inv_lock = m.Lock()
	inverted_file = m.dict()
	
	# Create a pool of processes
	p = Pool(line_args.process_cnt)
	
	# use the async mapping so every process takes of a job and start computing it
	# we don't care about the order which that happens
	r = p.map_async(parse_file, files)
	
	# wait for every child proceess to finish here
	p.close()
	p.join()
	
	# Increment returned statistics
	for p in r.get():			
		indexed_words 	+= p[0]
		excluded_words 	+= p[1]
	
	# -------------------------------------------------------------------------------

	calculate_tfidf()										# Enrich the Inverted File structure with the Tf*IDf information
	export_output(line_args.output_dir)						# Export the Inverted File structure to a picle file

	sys.exit(0)
