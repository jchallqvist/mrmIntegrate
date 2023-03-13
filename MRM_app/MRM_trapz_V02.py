#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jan  2 15:47:11 2017

@author: jennyhallqvist
"""
import numpy as np

def trapezoidalInt(x, y, intStart, intEnd):

    # Find the indices nearest x value from intStart and intEnd
    # Start
    resIntStart =  abs(x - intStart)
#    idxIntStart = resIntStart.argmin() # argmin deprecated, change for idxmin
    idxIntStart = resIntStart.idxmin()

    # End
    resIntEnd =  abs(x - intEnd)
#    idxIntEnd = resIntEnd.argmin()  # argmin deprecated, change for idxmin
    idxIntEnd = resIntEnd.idxmin()  
    
    # Copy of array containing only values between the indicies
    xTemp = x.copy()
    xTemp = xTemp[idxIntStart:idxIntEnd+1]
    yTemp = y.copy()
    yTemp = yTemp.loc[idxIntStart:idxIntEnd]

    # Integrate DF
    intRest = np.trapz(yTemp, xTemp, axis = 0)

    return intRest, xTemp, yTemp


