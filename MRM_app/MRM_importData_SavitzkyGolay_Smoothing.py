

##% import packages needed
#import os
#import numpy as np
import pandas as pd     
#import matplotlib
from statsmodels.nonparametric.smoothers_lowess import lowess
from scipy.signal import savgol_filter as savgol


# import the function to build files directly in gui main file
#dirOfImportFile='/Users/jennyhallqvist/Documents/Python'
#os.chdir(dirOfImportFile)
from MRM_openTXTfile import MRM_openTXTfile
#
## change directory to where the test files are
#os.chdir("/Users/jennyhallqvist/Documents/Python/Data_for_Python/MRM_files_Trem2_rerun")
#

# Get all the txt files inside the folder
def importData(filesInFolder):

    #filesInFolder = 
    #print('\nThe files to open are:\n')
    #for fileName in os.listdir():
    #    if fileName.endswith(".txt"):
    #        filesInFolder.append(fileName)
    #        print(fileName)
    
    # print('\n')        
    # Run the program to all the files
    # Put the results in list of lists
    contentOfFile_all=[]
#    infoOfFile_all=[]
    
    for fileName in filesInFolder:
        contentOfFile,infoOfFile = MRM_openTXTfile(fileName)
        contentOfFile_all.append(contentOfFile)
#        infoOfFile_all.append(infoOfFile)
    
    transitionsAll = []
    
    # no of transitions (from list within list)
    for transitionNr in range(len(contentOfFile_all[0])):
        transitionTemp = []
    # no of samples (from list)
        for sampleNr in range(len(contentOfFile_all)):
            transitionTemp.append(contentOfFile_all[sampleNr][transitionNr])
    # Savitzky-Golay smooting for all data
            transitionTempSmooth = []
            for item in range(len(transitionTemp)):
                transitionTempSmooth.append(pd.DataFrame(list(zip(transitionTemp[item]['time'], 
                                                         savgol(transitionTemp[item]['intensity'], 5, 3))), # window size 5, polynomial order 3
                                                         columns = ['time','intensity'])) 
                                                                                 
        transitionsAll.append(transitionTempSmooth)  
        
    return contentOfFile_all, infoOfFile, transitionsAll
         
    



    
    
    
    
    
    
    
    