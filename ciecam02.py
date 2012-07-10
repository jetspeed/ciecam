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
# first(XYZ)
    # second()
    # third()
    data = [(19.148, 0.35108, 0.33822),
            (19.448, 0.3499,  0.3368)]
    left = [(19.148,  0.35108,  0.33822),
            (19.448,  0.3499,   0.33680),
            (20.504,  0.3414,   0.33630),
            (18.808,  0.34874,  0.33734),
            (19.844,  0.34764,  0.33556),
            (18.708,  0.35062,  0.33864),
            (19.53,   0.33864,  0.33640),
            (17.546,  0.35038,  0.33984),
            (18.268,  0.34694,  0.33632),
            (18.79,   0.34884,  0.33758),
            (19.232,  0.34988,  0.33652),
            (19.37,   0.34628,  0.33668),
            (17.182,  0.35112,  0.33994),
            (19.844,  0.34338,  0.33618),
            (19.478,  0.34452,  0.33604),
            (19.376,  0.34074,  0.33606),
            (19.436,  0.3419,   0.33694),
            (19.738,  0.34394,  0.33710),
            (18.812,  0.34684,  0.33602),
            (18.826,  0.34726,  0.33630),
            (18.73,   0.34342,  0.33658),
            (19.274,  0.34252,  0.33634),
            (19.444,  0.34084,  0.33754),
            (18.872,  0.34296,  0.33814),
            (19.056,  0.34136,  0.33852),
            (18.408,  0.34246,  0.33766),
            (18.992,  0.34246,  0.33730),
            (20.142,  0.33774,  0.33796),
            (19.08,   0.34558,  0.33594),
            (18.488,  0.34442,  0.33644),
            (19.152,  0.34112,  0.33698),
            (19.404,  0.341,    0.33774),
            (18.694,  0.34348,  0.33760),
            (18.31,   0.3456,   0.33854),
            (18.578,  0.34088,  0.33824)]

    right = [(19.022,  0.35136, 0.33816),
            (18.962,  0.35222,  0.33872),
            (19.694,  0.3392,   0.34014),
            (17.498,  0.3509,   0.33978),
            (19.502,  0.34908,  0.33688),
            (18.47,   0.3514,   0.33958),
            (19.284,  0.34192,  0.34120),
            (17.75,   0.35534,  0.34014),
            (18.29,   0.35004,  0.33886),
            (18.278,  0.35064,  0.34074),
            (19.14,   0.35294,  0.34070),
            (18.818,  0.34956,  0.33982),
            (17.12,   0.352,    0.34228),
            (19.372,  0.34822,  0.34274),
            (19.07,   0.34838,  0.34032),
            (18.882,  0.3444,   0.34062),
            (19.48,   0.34264,  0.34084),
            (19.088,  0.34812,  0.34354),
            (18.282,  0.34702,  0.34042),
            (18.794,  0.35,     0.33996),
            (18.528,  0.34632,  0.34114),
            (18.856,  0.34708,  0.34158),
            (18.976,  0.34524,  0.34228),
            (18.51,   0.34704,  0.34232),
            (18.816,  0.34626,  0.34368),
            (18.066,  0.34674,  0.34424),
            (18.56,   0.34928,  0.34404),
            (19.594,  0.34134,  0.34186),
            (18.648,  0.34914,  0.34006),
            (18.04,   0.34982,  0.34276),
            (18.84,   0.34546,  0.34268),
            (18.93,   0.34514,  0.34274),
            (18.334,  0.3489,   0.34408),
            (18.124,  0.34998,  0.34554),
            (18.352,  0.34728,  0.34522)]

    for i in range(35):
        xyz_left = util.computeXYZ(left[i])
        xyz_right = util.computeXYZ(right[i])

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

