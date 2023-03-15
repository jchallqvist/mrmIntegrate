#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: Jenny Hallqvist
"""
import numpy as np

def trapezoidalInt(x, y, intStart, intEnd):
    resIntStart =  abs(x - intStart)
    idxIntStart = resIntStart.idxmin()

    resIntEnd =  abs(x - intEnd)
    idxIntEnd = resIntEnd.idxmin()  
    
    xTemp = x.copy()
    xTemp = xTemp[idxIntStart:idxIntEnd+1]
    yTemp = y.copy()
    yTemp = yTemp.loc[idxIntStart:idxIntEnd]

    intRest = np.trapz(yTemp, xTemp, axis = 0)

    return intRest, xTemp, yTemp


