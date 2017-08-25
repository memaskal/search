# -*- coding: utf-8 -*-
import scrapy
from crawler.items import Book

class GutenbergSpider(scrapy.Spider):
    
	# a unique spider name
	name = 'gutenberg'
		
	# starting url for spider
	start_url = 'http://www.gutenberg.org/ebooks/search/?sort_order=downloads'
	
	# maxpages
	maxpages = None
	
	def start_requests(self):
		self.maxpages = int(getattr(self, 'maxpages', None))
		if self.maxpages is None:
			self.maxpages = 3
		yield scrapy.Request(self.start_url, self.parse, meta={'page': 1})  
            

	def parse(self, response):
		# The books list
		books = response.css("li.booklink")
		for book in books:
			url = book.css("a::attr(href)").extract_first()	#id
			req = response.follow(url + ".txt.utf-8", callback=self.store_book_item)
			
			# create partially the book object 
			new_book = Book()
			new_book["id"] = int(url.split('/')[-1])								# book id
			new_book["title"] = book.css("span.title::text").extract_first()		# title 
			new_book["author"] = book.css("span.subtitle::text").extract_first()	# author
			
			# store the object in the request as metadata
			req.meta['book'] = new_book
			# initiate request
			yield req
		
		# Get the current page number
		page = response.meta.get('page')
		# The last link is always the next button
		next_page = response.css('span.links a::attr(href)').extract()[-1]
		if next_page is not None and page < self.maxpages:
			yield response.follow(next_page, callback=self.parse, meta={'page': page + 1})
	

	def store_book_item(self, response):
		# retrieve the object
		book = response.meta['book']
		# add the body
		book['text'] = response.body
		# store the object
		yield book
		
	
