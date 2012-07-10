#!/usr/bin/env python
# encoding: utf-8
"""
cmc.py

Created by wangxq on 2012-03-22.
Copyright (c) 2012 __MyCompanyName__. All rights reserved.
"""


import sys
import os
import xlrd

from math import e, pi, sqrt, atan, cos, log, sin

data = 'data/cmc.xls'
columns = 6

class ReadXls:
	def read(self, row):
		out = []
		sheet = xlrd.open_workbook(data).sheet_by_index(0)
		for i in range(columns):
			value = float(sheet.cell_value(row, i))
			out.append(value)
		return out

class Cmc:
	def __init__(self, data):
		self.leftL, self.lefta, self.leftb, self.rightL, self.righta, self.rightb = data

	def deltaL(self):
		return self.leftL - self.rightL

	def sl(self):
		out = 0.040975 * self.leftL / (1 + 0.01765 * self.leftL)
		return out

	def cab(self, a, b):
		return sqrt(a ** 2 + b ** 2)
	
	def deltaCab(self):
		left = self.cab(self.lefta, self.leftb)
		right = self.cab(self.righta, self.rightb)
		return left - right

	def sc(self):
		cab = self.cab(self.lefta, self.leftb) 
		out = 0.0638 * cab / (1 + 0.0131 * cab) + 0.638
		return out

	def deltaE(self):
		out = sqrt(self.deltaL() ** 2 + (self.lefta - self.righta) ** 2 + (self.leftb - self.rightb) ** 2)
		return out

	def deltaH(self):
		return sqrt(self.deltaE() ** 2 - self.deltaL() ** 2 - self.deltaCab() ** 2)

	def f(self):
		cableft = self.cab(self.lefta, self.leftb)
		return sqrt(cableft / (cableft + 1900))

	def hab(self):
		return 180 / pi * atan(self.leftb * 1.0/ self.lefta)
	def t(self):
		out = 0.56 + abs(0.2 * cos((self.hab() + 168) * pi / 180))
		return out
	def sh(self):
		return self.sc() * (self.f() * self.t() + 1 - self.f())


	def E(self):
		x = (self.deltaL()/ (1.4 * self.sl())) ** 2 
		y = (self.deltaCab() / self.sc()) ** 2
		z = (self.deltaH() / self.sh()) ** 2
		return sqrt(x + y + z)

def main():
	r = ReadXls()
	for i in range(35):
		labs = r.read(i)

		cmc = Cmc(labs)
		print cmc.E()


if __name__ == '__main__':
	main()

