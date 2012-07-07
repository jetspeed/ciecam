#!/usr/bin/env python
# encoding: utf-8
"""
cmc.py

Created by wangxq on 2012-03-22.
Copyright (c) 2012 __MyCompanyName__. All rights reserved.
"""


import sys
import os

from math import e, pi, sqrt, atan, cos, log, sin
class De2000:
	def __init__(self, leftlab, rightlab):
		self.leftL = leftlab[0]
		self.rightL = rightlab[0]
		self.lefta = leftlab[1]
		self.righta = rightlab[1]
		self.leftb = leftlab[2]
		self.rightb = rightlab[2]

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
	leftlab = [(50.846,8.838,5.836),
			(51.204,8.962,5.366),
			(52.388,6.836,4.332),
			(50.46,8.378,5.312),
			(51.656,8.73,4.882),
			(50.344,8.518,5.752),
			(51.298,5.806,4.032),
			(49.082,7.946,5.92),
			(49.842,8.096,4.828),
			(50.442,8.334,5.382),
			(50.958,8.948,5.344),
			(51.116,7.964,4.928),
			(48.34,8.034,5.978),
			(51.658,7.334,4.514),
			(51.244,7.636,4.598),
			(51.122,6.552,4.14),
			(51.19,6.64,4.482),
			(51.546,7.208,4.794),
			(50.484,8.23,4.8),
			(50.486,8.276,4.908),
			(50.348,7.204,4.524),
			(51.006,6.986,4.406),
			(51.202,6.132,4.512),
			(50.514,6.516,4.828),
			(50.752,6.034,4.764),
			(49.834,6.442,4.626),
			(50.678,6.64,4.596),
			(51.718,5.182,4.28),
			(50.78,7.99,4.688),
			(50.088,7.366,4.594),
			(50.864,6.354,4.386),
			(51.156,6.136,4.558),
			(50.326,6.81,4.752),
			(49.868,7.078,5.176),
			(50.19,5.864,4.592)]
	rightlab = [(50.728,8.918,5.84),
			(50.65,8.978,6.05),
			(51.488,6.68,5.614),
			(48.808,8.084,5.96),
			(51.266,8.714,5.316),
			(50.064,8.43,6.084),
			(51.018,5.384,5.434),
			(49.188,9.232,6.58),
			(49.844,8.142,5.752),
			(49.828,7.882,6.232),
			(50.85,8.64,6.594),
			(50.474,7.998,6.012),
			(48.292,7.648,6.574),
			(51.118,6.75,6.512),
			(50.77,7.552,6.006),
			(50.536,6.214,5.554),
			(51.258,5.706,5.464),
			(50.788,7.024,6.908),
			(49.83,8.052,6.212),
			(50.439,7.974,6.052),
			(50.13,6.572,5.852),
			(50.518,6.686,6.072),
			(50.656,5.768,5.932),
			(44.108,6.442,6.194),
			(50.474,5.87,6.432),
			(49.574,5.762,6.532),
			(50.172,6.576,6.838),
			(51.372,5.17,5.542),
			(50.272,7.68,5.95),
			(49.54,7.016,6.556),
			(50.496,5.914,6.128),
			(50.606,5.822,6.104),
			(49.898,6.436,6.774),
			(49.648,6.3,7.2),
			(49.92,5.666,6.836)]
	for i in range(35):
		de2000 = De2000(leftlab[i], rightlab[i])
		print de2000.deltaE()

if __name__ == '__main__':
	main()
