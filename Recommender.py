#!/usr/bin/python
# Recomends books on other users prefrences

import os
import csv
import pickle

from math import sqrt

# Some random reviews on the books
reviews = {
	'Alice' : {'00ws110.txt': 5.0, '8ataw11.txt': 4.5 },
	'John'	: {'8ataw11.txt': 2.0, 'idiot10.txt': 3.5 },
	'Bob'	: {'idiot10.txt': 4.0, '8ataw11.txt': 2.0, '1cahe10.txt': 3.0}
}


def load_titles_csv(filename):
	""" Returns a dictionary containing the books titlte 
		and author in our collection """
	results = {}
	with open(filename, 'r') as fp:
		rdr = csv.DictReader(fp, delimiter=',', quotechar='"')
		for row in rdr:
			# Titles containing stopwords like "The", "A" are split and saved in reverse order 
			# (example: "Memoirs of Sherlock Holmes, The"). So in the line bellow we
			# reverse the order again resulting to => "The Memoirs of Sherlock Holmes"
			title = (' '.join(reversed(row['Title'].split(',')))).strip()
			
			# This works cause only one field exists at a time,
			# so the other would be the empty string.
			book_id = row['Text'] + row['HTML']
			
			# Construct authors full name
			author = row['Author-LN'] + ' ' + row['Author-FN']
			
			# add book to dict
			results[book_id] = {'Title' : title, 'Author' : author}
	
	# return the books dictionary
	return results



def save_to_pickle(filename, data):
	""" Saves the book structure to pickle format """
	with open(filename, 'wb') as f:
		pickle.dump(data, f)



def load_from_pickle(filename):
	""" Loads the book structure from the pickle file """
	with open(filename, 'rb') as f:
		results = pickle.load(f)
	return results



def sim_pearson(prefs, p1, p2):
	""" Returns the Pearson correlation coefficient for p1 and p2 """
	#Get the list of mutually rated items
	si = {}
	for item in prefs[p1]:
		if item in prefs[p2]: 
			si[item] = 1
	
	#if they are no rating in common, return 0
	if len(si) == 0:
		return 0

	#sum calculations
	n = len(si)

	#sum of all preferences
	sum1 = sum([prefs[p1][it] for it in si])
	sum2 = sum([prefs[p2][it] for it in si])

	#Sum of the squares
	sum1Sq = sum([pow(prefs[p1][it], 2) for it in si])
	sum2Sq = sum([pow(prefs[p2][it], 2) for it in si])

	#Sum of the products
	pSum = sum([prefs[p1][it] * prefs[p2][it] for it in si])

	#Calculate r (Pearson score)
	num = pSum - (sum1 * sum2 / n)
	den = sqrt((sum1Sq - pow(sum1,2) / n) * (sum2Sq - pow(sum2, 2)/n))
	if den == 0:
		return 0

	r = num / den
	return r


#Gets recommendations for a person by using a weighted average
#of every other user's rankings
def getRecommendations(prefs, person):
	
	totals = {}
	simSums = {}

	for other in prefs:
		#don't compare me to myself
		if other == person:
			continue
		sim = sim_pearson(prefs, person, other)

		#ignore scores of zero or lower
		if sim <= 0: 
			continue
		for item in prefs[other]:
			#only score books i haven't seen yet
			if item not in prefs[person] or prefs[person][item] == 0:
				#Similarity * score
				totals.setdefault(item, 0)
				totals[item] += prefs[other][item] * sim
				#Sum of similarities
				simSums.setdefault(item, 0)
				simSums[item] += sim

	#Create the normalized list
	rankings = [(total/simSums[item], item) for item, total in totals.items()]

	#Return the sorted list
	rankings.sort(reverse=True)
	return rankings



if (__name__ == "__main__"):
	
	books_path = './books.pcl'	
	# Load the book dict, if it exists or else
	# parse the csv file containing the book titles
	# and save it to pickle for another time
	
	if os.path.exists(books_path):
		books = load_from_pickle('books.pcl')
	else:
		books = load_titles_csv('../books/master_list.csv')
		save_to_pickle(books_path, books)
	
	
	r = getRecommendations(reviews, 'John')
	if len(r) == 0:
		print 'No recommendations for you :('
	else:
		print 'These books are highly recommended for you:'
	
	for score, book_id in r:
		if score > 2.5:
			print books[book_id]['Title'] + ', by ' + books[book_id]['Author']
	
	

