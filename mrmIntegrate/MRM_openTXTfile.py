# -*- coding: utf-8 -*-
"""
@author: Jenny Hallqvist & Rui Pinto
"""

def MRM_openTXTfile(Xfilename):
        
    # import os
    import numpy as np
    import pandas as pd     
    
    f = open(Xfilename)
    counterX = 0
    flag_found_x = 1
    flag_chromatogram = 0
    listOfDataFrames = []
    listOfSpectrumNames = []
    for line_block in f:
        vals = line_block.split()
        if vals[0]=='chromatogram:':
            flag_chromatogram = 1
        if (flag_chromatogram == 1 and vals[0] == 'id:'):
            spectrumName = vals[1:]
            listOfSpectrumNames.append(spectrumName)
        if vals[0] == 'binary:':
           if flag_found_x == 1:
               flag_found_x = 0
               x = np.array(np.double(vals[2:]))
           else:
               y = np.array(np.double(vals[2:]))
               DFxy = pd.DataFrame(data = [x,y])
               DFxy=np.transpose(DFxy)
               DFxy.columns = ['time','intensity']
               listOfDataFrames.append(DFxy)
               flag_found_x = 1
               flag_chromatogram = 0
               counterX +=1
    f.close()
    return listOfDataFrames,listOfSpectrumNames
