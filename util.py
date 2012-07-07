#!/usr/bin/env python
# encoding: utf-8

def computeXYZ(Yxy):
    Y,x,y = Yxy[0], Yxy[1], Yxy[2]
    X = Y * x /y
    Z = Y * (1 - x - y) / y
    return [X, Y, Z]