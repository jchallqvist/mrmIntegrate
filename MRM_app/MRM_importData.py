

##% import packages needed
#import os
#import numpy as np
#import pandas as pd     
#import matplotlib

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
        transitionsAll.append(transitionTemp)
        
    return contentOfFile_all, infoOfFile, transitionsAll
         
    



    
    
    
    
    
    
    
    