#!/usr/bin/python
# encoding: utf-8

import xlrd, sys, os
from math import sqrt, log10, pow

data = 'data/PF.xls'

class ReadXls:
	def read(self, column):
		out = []
		sheet = xlrd.open_workbook(data).sheet_by_index(0)
		for i in range(sheet.nrows):
			value = float(sheet.cell_value(i, column))
			out.append(value)
		return out
class Stress:
	def __init__(self):
		r = ReadXls()

		self.deltaE = r.read(0)
		self.deltaV = r.read(1)

		self.n = len(self.deltaE)

	def F1(self):
		x, y = 0, 0
		for i in range(self.n):
			x += self.deltaE[i] ** 2
			y += self.deltaV[i] ** self.deltaE[i]
		return x / y
	def stress(self):
		x, y = 0, 0
		F1 = self.F1()
		for i in range(self.n):
			x += (self.deltaE[i] - F1 * self.deltaV[i]) ** 2
			y += (F1 ** 2) * (self.deltaV[i] ** 2)

		return sqrt(x/y)
		
def main():
	s = Stress()
	print s.stress()

if __name__ == '__main__':
	main()