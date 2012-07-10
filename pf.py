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
class Pf:
	def __init__(self):
		r = ReadXls()

		self.deltaE = r.read(0)
		self.deltaV = r.read(1)

		self.n = len(self.deltaE)

	def f(self):
		x, y = 0, 0
		for i in range(self.n):
			x += self.deltaE[i] * self.deltaV[i]
			y += self.deltaV[i] ** 2
		return x/y

	def F(self):
		x, y = 0, 0
		for i in range(self.n):
			x += self.deltaE[i] / self.deltaV[i]
			y += self.deltaV[i] / self.deltaE[i]
		return sqrt(x/y)

	def CV(self):
		f = self.f()

		x = 0
		for i in range(self.n):
			x += (self.deltaE[i] - f * self.deltaV[i]) ** 2
		frac = sqrt(x * 1.0 / self.n)
		averageX = reduce(lambda x,y:x+y, self.deltaE) / self.n
		return frac / averageX * 100

	def Vab(self):
		x = 0
		F = self.F()
		for i in range(self.n):
			x += (self.deltaE[i] - F * self.deltaV[i]) ** 2 / (self.deltaE[i] * F * self.deltaV[i])
		return sqrt(x / self.n)

	def averageLg(self):
		average = 0
		for i in range(self.n):
			average += log10(self.deltaE[i] * 1.0 / self.deltaV[i])
		return average / self.n

	def gamma(self):
		averageLg = self.averageLg()
		sum = 0
		for i in range(self.n):
			sum += (log10(self.deltaE[i] * 1.0 / self.deltaV[i]) - averageLg) ** 2
		out = sqrt(sum * 1.0 / self.n)
		gamma = pow(10, out)
		return gamma

	def pf(self):
		return 100 * ((self.gamma() - 1) + self.Vab() + self.CV() / 100) * 1.0 / 3

def main():
	pf = Pf()
	print pf.CV()
	print pf.gamma()
	print pf.pf()

if __name__ == '__main__':
	main()
