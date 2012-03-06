#!/usr/bin/env python
# encoding: utf-8
"""
get_tax_data.py

Created by Thomas Cabrol on 2012-02-15.
Copyright (c) 2012 Is Cool Entertainment. All rights reserved.
"""


import os
import urllib
import sys
from datetime import datetime
from BeautifulSoup import BeautifulSoup

# Set some constants....
RAW_DATA_DIR = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'raw_data')

class Downloader(object):
	''' Pure hack to crawl data.gouv.fr search results
	and download the files of interest. Please do not try to use it as is for anything else 
	than the Tax data where are looking for ! '''
	
	def __init__(self):
		'''
		  Instantiate the object using search URL components
		'''
		self.base_url = "http://www.data.gouv.fr/"
		self.search_url = "content/search/(offset)/"
		self.search_string = "?SearchText=&Type=data&Contexte=q%3Dtype%253Adata%26add_hit_meta%3Dhtml_simple_view%2540html_simple_view%26sort_ascending%3D0%26r%3DTop%252Fprimary_producer%252Fministere%2Bdu%2Bbudget%252C%2Bdes%2Bcomptes%2Bpublics%2Bet%2Bde%2Bla%2Breforme%2Bde%2Bl%2527etat%26r%3DTop%252Fkeywords%252Fimpot%2Bsur%2Ble%2Brevenu%26r%3DTop%252Fyear_interval%252F2009&Facet=Top/year_interval/2009"
		
	def get_files(self, max_offset):
		''' 
		  Returns a list of all Excel files to download 
		'''
		self.files = []
		for offset in xrange(0, max_offset, 10):
			# Fetch raw data from URL
			search_full_url = self.base_url + self.search_url + str(offset) + self.search_string
			html = urllib.urlopen(search_full_url).read()
			# Soup the content
			soup = BeautifulSoup(html)
			# Extract href links from the content
			for data in soup.findAll('p', { 'class' : 'download' }):
				link = data('a')[0]['href']
				# Filter only xls files
				if '.xls' in link:
					if link not in self.files:
						self.files.append(link)
		print >>sys.stdout, "%i files found...\n" % len(self.files)
		return self.files
		
	def download(self):
		''' Actually download the files '''
		# Create the target local directory if not existing
		if not os.path.isdir(RAW_DATA_DIR):
			os.makedir(RAW_DATA_DIR)
		# Loop thru pages 
		for xl_file in self.get_files(200):
			# Get URL, name, and local path for the files
			xl_file_url = self.base_url + xl_file
			xl_file_name = xl_file.split('/')[-1]
			xl_file_local = os.path.join(RAW_DATA_DIR, xl_file_name)
			print >>sys.stdout, "Downloading %s..." % xl_file_url
			# Actually retrieve the files
			urllib.urlretrieve(xl_file_url, xl_file_local)


if __name__ == '__main__':
	print "%s : Process starts..." % datetime.now()
	d = Downloader()
	d.download()
	print "%s : Process ends..." % datetime.now()
