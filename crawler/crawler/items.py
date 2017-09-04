# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class Book(scrapy.Item):
	id = scrapy.Field()
	title = scrapy.Field()
	author = scrapy.Field()
	text = scrapy.Field()
	last_updated = scrapy.Field(serializer=str)
	
	
