#!/usr/bin/env python
# encoding: utf-8
"""
geocoder.py

Created by Thomas Cabrol on 2012-02-08.
"""

import codecs
import simplejson
import urllib
import datetime
from threading import Lock
from os.path import join, dirname, realpath
from multiprocessing.dummy import Pool


DATA_DIR = join(dirname(realpath(__file__)), 'data')


class YahooGeocoder():

	def __init__(self, inFile, outFile):
		self.inputFile = inFile
		self.outFile = outFile
		# Specify file delimiter and fields to be used for geocoding
		self.delimiter = '\t'
		self.geocoding_fields = [6, 4, 2]
		# Your own api key for Yahoo
		self.app_id = 'xxxxxxxx'
		self.api_url = 'http://where.yahooapis.com/geocode?'
		self.lock = Lock()
		
	def load_data(self):
		# Skip header line 
		#next(self.inputFile)
		
		# Sends each row of the input file to the geocoder
		for i, line in enumerate(self.inputFile):
			# Write columns names
			if i == 0:
				print >> self.outFile, "%s%s%s%s%s%s%s" % (
					line.strip(), 
					self.delimiter, 
					'Latitude',
					self.delimiter,
					'Longitude',
					self.delimiter, 
					'Quality'
			   )
			# Returns a generator
			else :
				yield line.strip().split(self.delimiter)
			
	def geocode(self, record):
		'''
		Takes an address record from the input file, query Yahoo geocoding api,
		and returns geographic coordinates
		'''
		# Build a dict with the parameters for the query
		args = {}
		args['app_id'] = self.app_id
		# Pass a free-form address plus the country (hard coded == bad)
		args['q'] = ', '.join(record[i].encode('utf-8') for i in self.geocoding_fields) + ', France'
		# Send back json
		args['flags'] = 'J'
		args['locale'] = 'fr_FR'
		# Build the complete URL
		geocoding_url = self.api_url + urllib.urlencode(args)
		try:
			# Fetch the results
			data = simplejson.loads(urllib.urlopen(geocoding_url).read())
		except:
			data = {}
			data['ResultSet'] = {}
		# Take care of multi-threading			
		with self.lock:
			result = []
			# Write thecomplete input line to the output
			result.append(self.delimiter.join(record))
			try:
				# Append geo results
				result.append(str(data['ResultSet']['Results'][0]['latitude']))
				result.append(str(data['ResultSet']['Results'][0]['longitude']))
				result.append(str(data['ResultSet']['Quality']))
				print >> self.outFile, self.delimiter.join(result)
			except:
				print >> self.outFile, self.delimiter.join(result) 
		
		
	def run(self):
		# Run a parallel job by applying the geocoding function
		# on each input record 
		p = Pool(4)
		p.map(self.geocode, self.load_data())
			
		
	
if __name__ == '__main__':	
	i = join(DATA_DIR, 'Clean-Tax-Data.tsv')
	o = join(DATA_DIR, 'Clean-Tax-Data-Geocoded.tsv')	
	print "%s : Geocoding starts..." % (datetime.datetime.now())
	with codecs.open(i, 'r', 'utf-8') as _in:
		with codecs.open(o, 'w', 'utf-8') as _out:
			g = YahooGeocoder(_in, _out)
			g.run()
	print "%s : Geocoding ends..." % (datetime.datetime.now())
	# 2012-02-20 22:06:18.946470 : Geocoding starts...
	# 2012-02-20 23:06:30.969529 : Geocoding ends...

