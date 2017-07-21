#!/usr/bin/python
# BuildIndex: Assembly the Inverted Index. Bear in mind that inverted index is the data structure that maps tokens to the documents they appear in.
# http://aakashjapi.com/fuckin-search-engines-how-do-they-work/

import os
import re
import sys
import json
import time
import argparse

from nltk import pos_tag
from nltk.corpus import stopwords
from nltk.tokenize import WordPunctTokenizer
from nltk.stem.wordnet import WordNetLemmatizer



wp_tokenizer = WordPunctTokenizer()			# Tokenizer instance
wnl_lemmatizer = WordNetLemmatizer()		# Wordnet Lemmatizer instance

# English stop words list to set
stop_words = set(stopwords.words('english'))

inverted_file = {}							# The Inverted File data structure

total_doc_cnt = 0							# Total number of indexed documents
indexed_words = 0							# Total (corpus) number of indexed terms
excluded_words = 0							# Total (corpus) number of exluded terms

# closed tag set http://www.infogistics.com/tagset.html
CLOSED_TAGS = {'CD', 'CC', 'DT', 'EX', 'IN',
			   'LS', 'MD', 'PDT', 'POS', 'PRP',
			   'PRP$', 'RP', 'TO', 'UH', 'WDT',
			   'WP', 'WP$', 'WRB'}

def set_argParser():
	""" The build_index script's arguments presentation method."""
	argParser = argparse.ArgumentParser(description="Script's objective is to assembly the inverted index of a given document collection.")
	argParser.add_argument('-I', '--input_dir', type=str, default=os.path.dirname(os.path.realpath(__file__)) + os.sep + 'books', help='The directory path of the document collection. Default:' + os.path.dirname(os.path.realpath(__file__)) + os.sep + 'books')
	argParser.add_argument('-O', '--output_dir', default=os.path.dirname(os.path.realpath(__file__)), type=str, help='The output directory path where the inverted file is going to be exported in JSON format. Default: (' + os.path.dirname(os.path.realpath(__file__)))

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

	return line_args



def export_output(line_args):
	""" Export the Inverted File structure to a JSON file."""
	# http://stackoverflow.com/questions/12309269/how-do-i-write-json-data-to-a-file-in-python
	json_file = line_args.output_dir + 'inverted_file.txt'
	with open(json_file, 'w') as fh:
		json.dump(inverted_file, fh)



def calculate_tfidf():
	""" Calculate the TF * IDF per lemma."""
	global inverted_file

	for lemma in inverted_file.keys():
		# Inverted document frequency = Total number of documents / Number of documents appeared
		idf = total_doc_cnt / len(inverted_file[lemma]['il'].keys())

		for docid in inverted_file[lemma]['il'].keys():
			# Inverted List subdictionary structure:
			#    <key>    :                              <value>
			# Document id : (Term's frequency, [Term's order of appearance list], Tf * IDf)
			inverted_file[lemma]['il'][docid].append(inverted_file[lemma]['il'][docid][0] * idf)



def update_inverted_index(existing_lemmas):
	""" Update the Inverted File structure.."""
	global inverted_file

	for lemma in existing_lemmas.keys():
		if(lemma not in inverted_file.keys()):
			# The following labels are exported per each term to the JSON file => For compactness, we have to keep them short.
			# tdc: Total document frequency in corpus
			# twc: Total word/term frequency in corpus
			#  il: Word/Term's Inverted List
			inverted_file[lemma] = {}
			inverted_file[lemma]['tdc'] = 1
			inverted_file[lemma]['twc'] = len(existing_lemmas[lemma])
			inverted_file[lemma]['il'] = {}
		else :
			inverted_file[lemma]['tdc'] += 1
			inverted_file[lemma]['twc'] += len(existing_lemmas[lemma])

		# Inverted List subdictionary structure:
		#    <key>    :                              <value>
		# Document id : (Term's frequency in current document, [Term's order of appearance list])
		inverted_file[lemma]['il'][docid] = [len(existing_lemmas[lemma]), existing_lemmas[lemma]]



if (__name__ == "__main__") :
	argParser = set_argParser()				# The argument parser instance
	line_args = check_arguments(argParser)	# Check and redefine, if necessary, the given line arguments 
	
	pattern = re.compile(r'[\W_]+')			#compile pattern once, use it every time (If includes a non-letter character)
	
	# -------------------------------------------------------------------------------
	# Text File Parsing
	# -----------------
	for file in os.listdir(line_args.input_dir):
		if (not(file.endswith(".txt"))):		# Skip anything but .txt files
			continue

		docid = re.sub(r'\.txt$', '', file)		# Document's ID -String-
		existing_lemmas = {}					# Dictionary with the document's lemmas
		total_doc_cnt += 1						# Increment the total number of processed documents

		with open(line_args.input_dir + file, "r") as fh:
			tick = time.time()
			print "Processing: " + line_args.input_dir + file,

			word_cnt = 0 		# Our inverted index would map words to document names but, we also want to support phrase queries: queries for not only words, but words in a specific sequence => We need to know the order of appearance.

			for line in fh:
				for word, pos in pos_tag(wp_tokenizer.tokenize(line.lower().strip())):					
					if (
						pos in CLOSED_TAGS or				# search the closed tag set O(1)
						pattern.search(word) or				# If includes a non-letter character
						word in stop_words					# search for stop words O(1)
					):
						excluded_words += 1
						continue
					
					pos = 'v' if (pos.startswith('VB')) else 'n'	# If current term's appearance is verb related then the POS lemmatizer should be verb ('v'), otherwise ('n')
					lemma = wnl_lemmatizer.lemmatize(word, pos)		# Stemming/Lemmatization

					if (lemma not in existing_lemmas):
						existing_lemmas[lemma] = []

					existing_lemmas[lemma].append(word_cnt)		# Keep lemma's current position
					word_cnt += 1								# Increment the position pointer by 1
					indexed_words += 1							# Increment the total indexeds words count


			# Update the Inverted File structure with current document information
			update_inverted_index(existing_lemmas)

			print "({0:>6.2f} sec)".format(time.time() - tick)
	# -------------------------------------------------------------------------------

	calculate_tfidf()			# Enrich the Inverted File structure with the Tf*IDf information
	export_output(line_args)	# Export the Inverted File structure to a JSON file

	sys.exit(0)