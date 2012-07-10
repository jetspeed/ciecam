#!/usr/bin/env python
# encoding: utf-8
"""
ciecam.py

Created by wangxq on 2012-03-22.
Copyright (c) 2012 __MyCompanyName__. All rights reserved.
"""

import sys
import os
import util
import xlrd

import numpy as np
from math import e, pi, sqrt, atan, cos, log, sin

Mcat02 = np.array([[0.7328,  0.4296, -0.1624],
    [-0.7036, 1.6975, 0.0061],
    [0.0030,  0.0136, 0.9834]])
MHPE   = np.array([[0.38971,  0.68898, -0.07868],
    [-0.22981, 1.18340, 0.04641],
    [0.00000,  0.00000, 1.00000]])

La = 63.66
c, F = 0.69, 1.0

#Xw, Yw, Zw = 0.333, 0.333, 0.333
#X, Y, Z = 4, 5, 5
xb, yb, Yb = 0.316833333,0.3369,24.2883

#xyzb = util.computeXYZ((24.2883, 0.316833333, 0.3369)) 
Nc = 1.0

#XYZ = np.array([X, Y, Z]).reshape(-1, 1)
#XYZw = np.array([Xw, Yw, Zw]).reshape(-1, 1)


data = 'data/ciecam.xls'
columns = 6

class ReadXls:
    def read(self, row):
        out = []
        sheet = xlrd.open_workbook(data).sheet_by_index(0)
        for i in range(columns):
            value = float(sheet.cell_value(row, i))
            out.append(value)
        return out

class CieCam02:
    def __init__(self, xyz, xyzw):
        self.Yw = xyzw[1]
        self.XYZ = self.toXYZ(xyz)
        self.XYZw = self.toXYZ(xyzw)

    def toXYZ(self, arr):
        return np.array(arr).reshape(-1, 1)

    def first(self, xyz):
        """compute LMS and LMSw"""
        LMS = np.dot(Mcat02, xyz)
        #print "LMS: \n", LMS
        return LMS
    def second(self):
        """computing D"""
        D = F * (1 - 1/3.6 * e ** ( -1 * (42 + La) / 92) )
        #print 'D: \n', D
        return D
    def third(self, lms):
        """compute LMSc and LMSwc"""
        D = self.second()
        YwD = self.Yw * D
        LMSw = self.first(self.XYZw)
        LMS = self.first(self.XYZ)

        alpha =  YwD / LMSw + ( 1 - D )
        #print 'in 3, alpha: \n', alpha
        #print 'in 3, LMS: \n', lms
        #print alpha * lms

        LMSc = alpha * lms
        return LMSc
    def fourth(self):
        """计算亮度水平适应因子"""
        k = 1.0 / (5 * La + 1)
        Fl = 0.2 * k ** 4 * (5 * La) + 0.1 * (1 - k ** 4) ** 2 * (5 * La) ** (1.0 / 3)
        n = Yb / self.Yw
        Nbb = Ncb = 0.725 * (1.0 / n) ** 0.2
        z = 1.48 + sqrt(n)
        return {'k':k, 'Fl':Fl, 'n':n, 'Nbb':Nbb, 'Ncb':Ncb, 'z':z}
    def fifth(self, lmsc):
        """变换到HPE空间,LMShpe and LMShpew"""
        LMShpe = np.dot(np.dot(MHPE, np.linalg.inv(Mcat02)) , lmsc)
        return LMShpe
    def sixth(self, lmshpe):
        """应用后适应非线性压缩计算"""
        """if L M S negative, use abs"""
        Fl = self.fourth()['Fl']
        c = (Fl * abs(lmshpe) / 100) ** 0.42
        LMShpea = 400 * c / (27.13 + c) + 0.1
        return LMShpea * (lmshpe/abs(lmshpe))
    def seventh(self):
        """计算笛卡儿坐标a,b和色调h,should use LMShpea in sixth step"""
        # LMShpea = sixth(fifth(third(first(XYZ))))
        LMShpea = self.computeLMShpea(self.XYZ)
        Lhpea, Mhpea, Shpea = LMShpea[0][0], LMShpea[1][0], LMShpea[2][0]
        a = Lhpea - 12.0 * Mhpea / 11 + Shpea / 11
        b = (1.0/9) * (Lhpea + Mhpea - 2 * Shpea)
        h = atan(b * 1.0 / a) * 180 / pi
        return {"a":a, "b":b, "h":h}
    def eighth(self):
        """not same as wikipedia,计算偏心因子e"""
        Ncb = fourth()['Ncb']
        h = seventh()["h"]
        e = (12500.0/13 * Nc * Ncb) * ((cos(h * pi/ 180) + 2) + 3.8)
        return e

    def ninth(self):
        """计算色调H"""
        harray = (20.14, 90.00, 164.25, 237.53, 380.14)
        earray = (0.8, 0.7, 1.0, 1.2, 0.8)
        Harray = (0.0, 100.0, 200.0, 300.0, 400.0)
        h = self.seventh()["h"]
        i = 0
        # find i
        for index, value in enumerate(harray):
            if value <= h:
                i = index
        H = Harray[i] + (100.0 * (h - harray[i]) / earray[i]) / ((h - harray[i])/earray[i] + (harray[i+1] - h)/earray[i+1])
        return H
    def tenth(self, lmshpea):
        """compute A and Aw"""
        # LMShpea = computeLMShpea(XYZ)
        # LMShpeaw = computeLMShpea(XYZw)
        Lhpea, Mhpea, Shpea = self.abstractLMS(lmshpea)
        Nbb = self.fourth()['Nbb']
        A = (2.0 * Lhpea + Mhpea + (1.0/20)* Shpea - 0.305) * Nbb
        return A
    def eleventh(self):
        """明度J"""
        A = self.tenth(self.computeLMShpea(self.XYZ))
        Aw = self.tenth(self.computeLMShpea(self.XYZw))
        z = self.fourth()['z']
        J = 100 * (A * 1.0 / Aw) ** (c * z)
        return J
    def twelfth(self):
        """视明度Q"""
        J = self.eleventh()
        Aw = self.tenth(self.computeLMShpea(self.XYZw))
        Fl = self.fourth()['Fl']
        Q = (4 * 1.0 / c) * sqrt(J / 100.0) * (Aw + 4) * Fl ** 0.25
        return Q
    def thirteenth(self):
        s = self.seventh()
        a, b = s["a"], s["b"]
        Lhpea, Mhpea, Shpea = self.abstractLMS(self.computeLMShpea(self.XYZ))
        t = e * (a ** 2 + b ** 2) ** 0.5 / (Lhpea + Mhpea + (21.0/20)* Shpea)
        return t
    def fourteenth(self):
        """计算彩度C"""
        t = self.thirteenth()
        J = self.eleventh()
        n = self.fourth()["n"]
        C = t ** 0.9 * sqrt(J/100.0) * (1.64 - 0.29 ** n) ** 0.73
        return C
    def fifteenth(self):
        """计算视彩度M"""
        C = self.fourteenth()
        Fl = self.fourth()['Fl']
        M = C * Fl ** 0.25
        return M
    def sixteenth(self):
        """计算饱和度S, the book is wrong"""
        M = self.fifteenth()
        Q = self.twelfth()
        S = 100 * sqrt(M * 1.0 / Q)
        return S
    def computeLMShpea(self, xyz):
        LMShpea = self.sixth(self.fifth(self.third(self.first(xyz))))
        return LMShpea
    def abstractLMS(self, lmshpea):
        return lmshpea[0][0], lmshpea[1][0], lmshpea[2][0]

class DeltaE:
    def __init__(self, Kl, C1, C2, leftJ, rightJ, leftM, rightM, lefth, righth):
        self.Kl = Kl
        self.C1 = C1
        self.C2 = C2
        self.leftJ, self.rightJ, self.leftM, self.rightM, self.lefth, self.righth \
        = leftJ, rightJ, leftM, rightM, lefth, righth

    def deltaJ(self):
        left  = (1 + 100 * self.C1) * self.leftJ / (1 + self.C1 * self.leftJ) 
        right = (1 + 100 * self.C1) * self.rightJ / (1 + self.C1 * self.rightJ)
        return left - right
    def Mp(self, M):
        mp = (1 / self.C2) * log((1 + self.C2 * M), e)
        return mp
    def deltaa(self):
        left = self.Mp(self.leftM) * cos(self.lefth * pi / 180)
        right = self.Mp(self.rightM) * cos(self.righth * pi / 180)
        return left - right
    def deltab(self):
        left = self.Mp(self.leftM) * sin(self.lefth * pi / 180)
        right = self.Mp(self.rightM) * sin(self.righth * pi / 180)
        return left - right
    def deltaE(self):
        a = (self.deltaJ()/ self.Kl) ** 2
        b = self.deltaa() ** 2
        c = self.deltab() ** 2
        out = sqrt(a + b + c)
        return out

def main():
    for i in range(35):
        r = ReadXls()
        left = r.read(i)[0:3]
        right = r.read(i)[3:6]
        xyz_left = util.computeXYZ(left)
        xyz_right = util.computeXYZ(right)

        xyzw = util.computeXYZ((81.9550, 0.311466667, 0.3311))


        Kl, C1, C2 = 0.77, 0.007, 0.0053
        #Kl, C1, C2 = 1.24, 0.007, 0.0363
        #Kl, C1, C2 = 1.00, 0.007, 0.0228

        cleft = CieCam02(xyz_left, xyzw)
        cright = CieCam02(xyz_right, xyzw)

        # # abh
        # print c.seventh()
        # # H
        # print "H is :", c.ninth()
        # # J
        # print "J is :", c.eleventh()
        # # Q
        # print "Q is :", c.twelfth()
        # print "C is :", c.fourteenth()
        # print "M is :", c.fifteenth()
        # print "s is :", c.sixteenth()

        leftJ = cleft.eleventh()
        rightJ = cright.eleventh()
        leftM = cleft.fifteenth()
        rightM = cright.fifteenth()
        lefth = cleft.seventh()['h']
        righth = cright.seventh()['h']

        #print leftJ, rightJ, leftM, rightM, lefth, righth

        deltaE = DeltaE(Kl, C1, C2, leftJ, rightJ, leftM, rightM, lefth, righth)
        print deltaE.deltaE()
            
if __name__ == '__main__':
    main()

