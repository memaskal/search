# -*- coding: utf-8 -*-
from scrapy import log
from twisted.enterprise import adbapi


class MySQLStorePipeline(object):
	def __init__(self, dbpool):
		self.dbpool = dbpool

	@classmethod
	def from_settings(cls, settings):
		dbargs = dict(
			host=settings['MYSQL_HOST'],
			db=settings['MYSQL_DBNAME'],
			user=settings['MYSQL_USER'],
			passwd=settings['MYSQL_PASSWD'],
			charset='utf8',
			use_unicode=True,
		)
		dbpool = adbapi.ConnectionPool('MySQLdb', **dbargs)
		return cls(dbpool)

	def process_item(self, item, spider):
		# run db query in the thread pool
		d = self.dbpool.runInteraction(self._do_upsert, item, spider)
		d.addErrback(self._handle_error, item, spider)
		# at the end return the item in case of success or failure
		# d.addBoth(lambda _: item)
		# return the deferred instead the item. This makes the engine to
		# process next item (according to CONCURRENT_ITEMS setting) after this
		# operation (deferred) has finished.
		return d

	def _do_upsert(self, conn, item, spider):
		"""Perform an insert or update."""
		bid = int(item['id'])
			
		conn.execute("""SELECT EXISTS(
			SELECT 1 FROM books WHERE id=%s
		)""", (bid,))
		ret = conn.fetchone()[0]

		if ret:
			conn.execute("""
				UPDATE books
				SET title=%s, author=%s, text=%s WHERE id=%s
			""", (item['title'], item['author'], item['text'], bid))
		else:
			conn.execute("""
				INSERT INTO books (id, title, author, text)
				VALUES (%s, %s, %s, %s)
			""", (bid, item['title'], item['author'], item['text']))
		return "Item %d updated" % bid 

	def _handle_error(self, failure, item, spider):
		"""Handle occurred on db interaction."""
		# do nothing, just log
		log.err(failure)

