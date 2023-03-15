#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: Jenny Hallqvist
"""
import pandas as pd     
from statsmodels.nonparametric.smoothers_lowess import lowess
from MRM_openTXTfile import MRM_openTXTfile

def importData(filesInFolder):
    contentOfFile_all=[]   
    for fileName in filesInFolder:
        contentOfFile,infoOfFile = MRM_openTXTfile(fileName)
        contentOfFile_all.append(contentOfFile)   
    transitionsAll = []    
    for transitionNr in range(len(contentOfFile_all[0])):
        transitionTemp = []
        for sampleNr in range(len(contentOfFile_all)):
            transitionTemp.append(contentOfFile_all[sampleNr][transitionNr])
        transitionTempSmooth = []
        for item in range(len(transitionTemp)):
            frac_n = 5/len(transitionTemp[item]['time']) # Smooth over 5 points
            transitionTempSmooth.append(pd.DataFrame(lowess(transitionTemp[item]['intensity'], 
                                                            transitionTemp[item]['time'], 
                                                            frac=frac_n, it=0, delta=0.0, 
                                                            is_sorted=True, missing='none', 
                                                            return_sorted=True), 
                                                            columns = ['time','intensity']))          
        transitionsAll.append(transitionTempSmooth)
    return contentOfFile_all, infoOfFile, transitionsAll
         
    



    
    
    
    
    
    
    
    