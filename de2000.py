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

class De2000:
	def __init__(self, labs):
		self.leftL, self.lefta, self.leftb, self.rightL, self.righta, self.rightb = labs

	def deltaL(self):
		return self.leftL - self.rightL
	def averageL(self):
		return (self.leftL + self.rightL) / 2
	def sl(self):
		x = (self.averageL() - 50) ** 2
		out = 1 + 0.15 * x / sqrt(20 + x)
		return out
	def averageCab(self):
		return sqrt(self.lefta ** 2 + self.leftb ** 2) * sqrt(self.righta ** 2 + self.rightb ** 2)
	def g(self):
		return 0.5 * (1 - sqrt(self.averageCab() ** 7/ (self.averageCab() ** 7 + 25 ** 7)))
	def ap(self, a):
		return a * ( 1 + self.g())
	def bp(self, b):
		return b
	def cp(self, ap, bp):
		return sqrt(ap ** 2 + bp ** 2)
	def adCp(self):
		cpleft = self.cp(self.ap(self.lefta), self.bp(self.leftb))
		cpright = self.cp(self.ap(self.righta), self.bp(self.rightb))
		return {"acp" : (cpleft + cpright ) / 2, "dcp" : cpleft - cpright }
	def sc(self):
		return 1 + 0.045 * self.adCp()["acp"]

	def hp(self, ap, bp):
		return 180 * atan(bp * 1.0 /ap) / pi
	def adHp(self):
		apleft, apright = self.ap(self.lefta), self.ap(self.righta)
		bpleft, bpright = self.bp(self.leftb), self.bp(self.rightb)

		hpleft = self.hp(apleft, bpleft)
		hpright = self.hp(apright, bpright)
		return {"ahp" : (hpleft + hpright) / 2, "dhp" : hpleft - hpright}

	def deltaHp(self):
		cpleft = self.cp(self.ap(self.lefta), self.bp(self.leftb))
		cpright = self.cp(self.ap(self.righta), self.bp(self.rightb))
		return 2 * (cpleft * cpright ) ** 0.5 * sin(self.adHp()["dhp"] / 2 * pi / 180)
	def t(self):
		ahp = self.adHp()["ahp"]
		x = 0.17 * cos((ahp - 30) * pi / 180)
		y = 0.24 * cos(2 * ahp * pi / 180)
		z = 0.32 * cos((3 * ahp + 6) * pi / 180)
		w = 0.20 * cos((4 * ahp - 63) * pi / 180)
		t = 1 - x + y + z - w
		return t
	def sh(self):
		return 1 + 0.015 * self.adCp()["acp"] * self.t()

	def rc(self):
		acp = self.adCp()["acp"]
		return 2 * sqrt(acp ** 7 / (acp ** 7 + 25 ** 7))
	def deltaZ(self):
		ahp = self.adHp()["ahp"]
		x = -1 * ((ahp - 275) * 1.0 / 25) ** 2
		return 30 * pow(e, x)
	def rt(self):
		return -1 * sin(2 * self.deltaZ() * pi / 180) * self.rc()
	def deltaE(self):
		x = (self.deltaL() * 1.0 / self.sl()) ** 2
		y = (self.adCp()["dcp"] * 1.0 / self.sc()) ** 2
		z = (self.deltaHp() * 1.0 / self.sh()) ** 2
		w = self.rt() * (self.adCp()["dcp"] * 1.0 / self.sc()) * (self.deltaHp() * 1.0 / self.sh())
		return sqrt(x + y + z + w)
def main():
	r = ReadXls()
	for i in range(35):
		labs = r.read(i)

		de2000 = De2000(labs)
		print de2000.deltaE()

if __name__ == '__main__':
	main()
