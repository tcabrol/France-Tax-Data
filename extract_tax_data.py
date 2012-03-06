#!/usr/bin/env python
# encoding: utf-8
"""
extract_tax_data.py

Created by Thomas Cabrol on 2012-02-15.
Copyright (c) 2012 Is Cool Entertainment. All rights reserved.
"""

import codecs
import os
import xlrd
import re
from datetime import datetime


# Set some constants....
RAW_DATA_DIR = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'raw_data')
DATA_DIR = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'data')


class ExcelExtractor(object):
	''' 
	  Simple class that takes data from the source xls 
	  files and append it into a tsv file 
	'''
	
	def __init__(self):
		''' 
		  Instantiate the object with some values related to
		  the schema of the xls files 
		'''
		if not os.path.isdir(DATA_DIR):
			os.makedir(DATA_DIR)
		self.outFile = os.path.join(DATA_DIR, 'raw_tax_data.tsv')
		self.sheet_index = 0
		# Specifying where the data is located in the sheet
		self.min_row = 27
		self.max_row = 20000
		self.min_col = 1
		self.max_col = 14
		# Define the layout of the file
		self.columns_map = {
		  	0 : {"description" : u"DEP", "name" : u"dep"} ,
		  	1 : {"description" : u"Commune", "name" : u"commune"} ,
			2 : {"description" : u"Libellé de la communes", "name" : u"label_commune"} ,
		  	3 : {"description" : u"Revenu fiscal de référence par tranche (en euros)", "name" : u"segment_fiscal_revenue"} ,
		  	4 : {"description" : u"Nombre de foyers fiscaux", "name" : u"count_fiscal_hh"} ,
		  	5 : {"description" : u"Revenu fiscal de référence des foyers fiscaux", "name" : u"ref_fiscal_rev_fiscal_hh"} ,
		  	6 : {"description" : u"Impôt net (total)", "name" : u"net_tax"} ,
		  	7 : {"description" : u"Nombre de foyers fiscaux imposables", "name" : u"count_fiscal_hh_taxable"} ,
		  	8 : {"description" : u"Revenu fiscal de référence des foyers fiscaux imposables", "name" : u"ref_fiscal_rev_fiscal_hh_taxable"} ,
		  	9 : {"description" : u"Traitements et salaires - Nombre de foyers concernés", "name" : u"salaries_actual_hh_count"} ,
		  	10: {"description" : u"Traitements et salaires - Montant", "name" : u"salaries_amount"} ,
		  	11: {"description" : u"Retraites et pensions - Nombre de foyers concernés", "name" : u"retirement_actual_hh_count"} ,
		  	12: {"description" : u"Retraites et pensions - Montant", "name" : u"retirement_amount"}
		}
		
	def list_xls(self):
		''' 
		  Returns the list of xls files to be parsed 
		  We only look for the "Departements" files, hence
		  the regex condition
		'''
		return [f for f in os.listdir(RAW_DATA_DIR) if re.match('^(\d{3})(.xls)', f)]
		
	def printable(self, item):
		'''
		  Simple trick to make the content
		  printable in the output file
		'''
		if isinstance(item, basestring):				
			return item
		return str(item)
	
	def xls_to_tsv(self):
		'''
		  Actually extract the content of the files and stack it
		  into a TSV file
		'''
		# Let codecs deals with encoding issues 
		t = codecs.open(self.outFile, 'w', 'utf-8')
		# Write headers from the columns map
		t.write('\t'.join(v['description'] for k, v in e.columns_map.items()) + '\n')
		# Loop thru every files and open them
		for infile in self.list_xls():
			try:
				excel = xlrd.open_workbook(os.path.join(RAW_DATA_DIR, infile))
			except:
				print >>sys.stdout, "Failed to open %s..." % infile
			# Move to the right sheet 
			sheet = excel.sheet_by_index(self.sheet_index)
			# Loop thru rows with data and beyond
			for row in xrange(self.min_row, self.max_row):
				try:
					# Read in teh content of the rows
					record = sheet.row_values(row, start_colx =  self.min_col, end_colx = self.max_col)
					if not len(record) == len(self.columns_map):
						print >>sys.stdout, "Line does not match : %s" % record
					# Output it to a TSV file
					t.write('\t'.join(map(self.printable, record)) + '\n')
				except:
					#print >>sys.stdout, sys.exc_info()[1]
					# Silently pass exceptions...
					pass
		t.close()

if __name__ == '__main__':
	print "%s : Process starts..." % datetime.now()
	e = ExcelExtractor()
	e.xls_to_tsv()
	print "%s : Process ends..." % datetime.now()

