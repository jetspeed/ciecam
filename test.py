#!/usr/bin/python
# encoding: utf-8

import xlrd

data = 'data/PF.xls'
class Test:
	def a(self):
		print "a"
		b()
	def b(self):
		print "b"

class ReadXls:
	def read(self):
		sheet = xlrd.open_workbook(data).sheet_by_index(0)
		for i in range(sheet.nrows):
			print sheet.cell_value(i, 0), sheet.cell_value(i, 1)

def main():
	t = Test()
	r = ReadXls()
	r.read()
	
if __name__ == '__main__':
	main()