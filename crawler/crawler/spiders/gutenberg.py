# -*- coding: utf-8 -*-
import scrapy


class GutenbergSpider(scrapy.Spider):
    name = 'gutenberg'
    allowed_domains = ['http://www.gutenberg.org/']
    start_urls = ['http://http://www.gutenberg.org//']

    def parse(self, response):
        pass
