#!/usr/bin/env python
# encoding: utf-8
"""
ciecam.py

Created by wangxq on 2012-03-22.
Copyright (c) 2012 __MyCompanyName__. All rights reserved.
"""

import sys
import os

import numpy as np
from math import e, pi, sqrt, atan, cos

Mcat02 = np.array([[0.7328,  0.4296, -0.1624],
					[-0.7036, 1.6975, 0.0061],
					[0.0030,  0.0136, 0.9834]])
MHPE   = np.array([[0.38971,  0.68898, -0.07868],
					[-0.22981, 1.18340, 0.04641],
					[0.00000,  0.00000, 1.00000]])
					
La = 63.66
c, F = 0.59, 0.9

Xw, Yw, Zw = 1, 2, 3
X, Y, Z = 4, 5, 5
xb, yb, Yb = 4, 5, 6
Nc = 0.95

XYZ = np.array([X, Y, Z]).reshape(-1, 1)
XYZw = np.array([Xw, Yw, Zw]).reshape(-1, 1)

def first(xyz):
	"""compute LMS and LMSw"""
	LMS = np.dot(Mcat02, xyz)
	print "LMS: \n", LMS
	return LMS
def second():
	"""computing D"""
	D = F * (1 - 1/3.6 * e ** ( -1 * (42 + La) / 92) )
	print 'D: \n', D
	return D
def third(lms):
	"""compute LMSc and LMSwc"""
	#LMS = np.array([1,2,3]).reshape(-1, 1)
	#YwD = np.array([2, 4, 5.0]).reshape(-1, 1)
	D = second()
	YwD = Yw * D
	LMSw = first_step(XYZw)
	LMS = first_step(XYZ)
	
	alpha =  YwD / LMSw + ( 1 - D )
	print 'in 3, alpha: \n', alpha 
	print 'in 3, LMS: \n', lms 
	print alpha * lms
	
	LMSc = alpha * lms
	return LMSc
def fourth():
	"""计算亮度水平适应因子"""
	k = 1.0 / (5 * La + 1)
	Fl = 0.2 * k ** 4 * (5 * La) + 0.1 * (1 - k ** 4) ** 2 * (5 * La) ** (1.0 / 3)
	n = Yb / Yw
	Nbb = Ncb = 0.725 * (1.0 / n) ** 0.2
	z = 1.48 + sqrt(n)
	return {'k':k, 'Fl':Fl, 'n':n, 'Nbb':Nbb, 'Ncb':Ncb, 'z':z}
def fifth(lmsc):
	"""变换到HPE空间,LMShpe and LMShpew"""
	LMShpe = np.dot(np.dot(MHPE, np.linalg.inv(Mcat02)) , lmsc)
	return LMShpe
def sixth(lmshpe):
	"""应用后适应非线性压缩计算"""
	"""if L M S negative, use abs"""
	Fl = fourth()['Fl']
	c = (Fl * abs(lmshpe) / 100) ** 0.42 
	LMShpea = 400 * c / (27.13 + c) + 0.1
	return LMShpea * (lmshpe/abs(lmshpe))
def seventh():
	"""计算笛卡儿坐标a,b和色调h,should use LMShpea in sixth step"""
	# LMShpea = sixth(fifth(third(first(XYZ))))
	LMShpea = computeLMShpea(XYZ)
	Lhpea, Mhpea, Shpea = LMShpea[0][0], LMShpea[1][0], LMShpea[2][0]
	a = Lhpea - 12.0 * Mhpea / 11 + Shpea / 11
	b = (1.0/9) * (Lhpea + Mhpea - 2 * Shpea)
	h = atan(b * 1.0 / a) * 180 / pi
	return {"a":a, "b":b, "h":h}
def eighth():
	"""not same as wikipedia,计算偏心因子e"""
	Ncb = fourth()['Ncb']
	h = seventh()["h"]
	e = (12500.0/13 * Nc * Ncb) * ((cos(h * pi/ 180) + 2) + 3.8)
	return e
	
def ninth():
	"""计算色调H"""
	harray = (20.14, 90.00, 164.25, 237.53, 380.14)
	earray = (0.8, 0.7, 1.0, 1.2, 0.8)
	Harray = (0.0, 100.0, 200.0, 300.0, 400.0)
	h = seventh()["h"]
	i = 0
	# find i
	for index, value in enumerate(harray):
		if value <= h:
			i = index
	H = Harray[i] + (100.0 * (h - harray[i]) / earray[i]) / ((h - harray[i])/earray[i] + (harray[i+1] - h)/earray[i+1])
	return H
def tenth(lmshpea):
	"""compute A and Aw"""
	# LMShpea = computeLMShpea(XYZ)
	# LMShpeaw = computeLMShpea(XYZw)
	Lhpea, Mhpea, Shpea = abstractLMS(lmshpea)
	Nbb = fourth()['Nbb']
	A = (2.0 * Lhpea + Mhpea + (1.0/20)* Shpea - 0.305) * Nbb
	return A
def eleventh():
	"""明度J"""
	A = tenth(computeLMShpea(XYZ))
	Aw = tenth(computeLMShpea(XYZw))
	z = fourth()['z']
	J = 100 * (A * 1.0 / Aw) ** (c * z)
	return J
def twelfth():
	"""视明度Q"""
	J = eleventh()
	Aw = tenth(computeLMShpea(XYZw))
	Fl = fourth()['Fl']
	Q = (4 * 1.0 / c) * sqrt(J / 100.0) * (Aw + 4) * Fl ** 0.25
	return Q
def thirteenth():
	s = senventh()
	a, b = s["a"], s["b"]
	Lhpea, Mhpea, Shpea = abstractLMS(computeLMShpea(XYZ))
	t = e * (a ** 2 + b ** 2) ** 0.5 / (Lhpea + Mhpea + (21.0/20)* Shpea)
	return t
def fourteenth():
	"""计算彩度C"""
	t = thirteenth()
	J = eleventh()
	n = fourth()["n"]
	C = t ** 0.9 * sqrt(J/100.0) * (1.64 - 0.29 ** n) ** 0.73
	return C
def fifteenth():
	"""计算视彩度M"""
	C = fourteenth()
	Fl = fourth()['Fl']
	M = C * Fl ** 0.25
	return M
def sixteenth():
	"""计算饱和度S, the book is wrong"""
	M = fifteenth()
	Q = twelfth()
	S = 100 * sqrt(M * 1.0 / Q)
	return S
def computeLMShpea(xyz):
	LMShpea = sixth(fifth(third(first(xyz))))
	return LMShpea
def abstractLMS(lmshpea):
	return lmshpea[0][0], lmshpea[1][0], lmshpea[2][0]	
		
def main():
	first(XYZ)
	second()
	# third()

if __name__ == '__main__':
	main()

