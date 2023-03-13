# -*- coding: utf-8 -*-
"""
Created on Sat Nov 26 15:30:37 2016

@author: rupi0002
"""
##% import packages needed

def MRM_openTXTfile(Xfilename):
        
    import os
    import numpy as np
    import pandas as pd     
    import matplotlib as mplib 
    
    #f = open('160914_JH_Trem2__Cal_C_06a_2500x_QC.txt')
    f = open(Xfilename)
    counterX=0
    flag_found_x = 1
    flag_chromatogram = 0
    listOfDataFrames=[]
    listOfSpectrumNames=[]
    for line_block in f:
        #print(line_block)
        vals = line_block.split()
        #print(vals)
        if vals[0]=='chromatogram:':
            flag_chromatogram = 1
            
        if (flag_chromatogram == 1 and vals[0]=='id:'):
            spectrumName = vals[1:]
#            print (spectrumName)
            listOfSpectrumNames.append(spectrumName)
            
        if vals[0]=='binary:':
           if flag_found_x == 1:
               flag_found_x = 0
               x=np.array(np.double(vals[2:]))
           else:
               
               nrOfVals_str=vals[1]
               nrOfVals_double=np.double(nrOfVals_str[1:-1])
#               print('SpectrumNr: ',counterX,' NrOfValues: ',nrOfVals_double,'\n')
               y=np.array(np.double(vals[2:]))
               
               DFxy=pd.DataFrame(data=[x,y])
               DFxy=np.transpose(DFxy)
               DFxy.columns=['time','intensity']
               listOfDataFrames.append(DFxy)
               #mplib.pyplot.plot(x,y)
               #mplib.pyplot.show()
               flag_found_x = 1
               flag_chromatogram = 0
               counterX +=1
    f.close()
    
    return listOfDataFrames,listOfSpectrumNames
