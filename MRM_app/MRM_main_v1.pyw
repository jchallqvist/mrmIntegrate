#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Mar 12 16:33:44 2017

@author: Jenny
"""


#self.filesInFolder = r'RTMZ_HPosPhase2.csv'
#df = pd.read_excel(self.filesInFolder)
import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog, QMessageBox
from PyQt5 import uic , QtCore
import pandas as pd
import numpy as np
from MRM_importData import importData
from MRM_trapz import trapezoidalInt

#from openIndividualTextFile1 import openIndividualTextFile1
from matplotlib import rc
rc('font',**{'family':'sans-serif','sans-serif':['Arial'], 'size':8})

# FOR FIGURE
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_qt5agg import (FigureCanvasQTAgg as FigureCanvas, NavigationToolbar2QT as NavigationToolbar)
#from matplotlib import rc
#rc('font',**{'family':'sans-serif','sans-serif':['Corbel']})

# IMPORT FILES FROM UI AND RESOURCES
# http://projects.skylogic.ca/blog/how-to-install-pyqt5-and-build-your-first-gui-in-python-3-4/
#from bookGuiRP6_compiled import Ui_MainWindow
# import resourceFile1_rc # This is already explicit in the .ui compiled file

class MainWindowMRM(QMainWindow):
    def __init__(self):
        super().__init__()
####### INITIALIZATION  #######################################################
        # Load the file from the designer
        uic.loadUi('MRM.ui', self)

# NOTE: to compile the .ui file, open a command window, and in DOS (not in Python) use: 
#compile ui file from Qt Designer
#pyuic5 -o compiled_ui_file.py ui_file.ui
##compile resource file (icons, etc..)
#pyrcc4 -o compiled_resource_file.py resource_file.qrc
# Then, import the file using: import compiled_ui_file
###############################################################################        

        # define the file menu
#        self.action_LoadSamples.triggered.connect(self.f_openFile)
        self.pushButton_2.clicked.connect(self.f_openFile)
        self.flagListPopulated = False
        self.flagAlignmentModeON = False
        self.flagIntegrationModeON = False
        self.alignPoints = []
        self.integratePoints = []

# MAKE FIGURE 0 (TIC)
# NOTE: In QTdesigner create a button on top of the figure widget,
# then apply grid layout on widget, save, and delete button. 
# This will allow the plot to change size. In this program the layout is called mplvl
#create a canvas to put a figure and toolbar, but do not draw anything yet

        self.figX = matplotlib.figure.Figure(figsize=(5,2), dpi=100)
        self.figX.set_tight_layout({"pad": .0})
        self.figX.patch.set_facecolor('white')
        self.canvas = FigureCanvas(self.figX)
        self.toolbar = NavigationToolbar(self.canvas, self.widget_TIC, coordinates=False)
        self.vl_TIC.addWidget(self.toolbar)     
        self.vl_TIC.addWidget(self.canvas)
        self.ax = self.figX.add_subplot(111)
        # plot on figure
        self.PB_plotTrans.clicked.connect(self.addmpl)
        self.PB_align.clicked.connect(self.f_turnAlignmentON)
        self.PB_integrate.clicked.connect(self.f_turnIntegrationON)
#########THESE TWO LINES WERE ADDED FOR MOUSE CLICK
        self.canvas.setFocusPolicy(QtCore.Qt.ClickFocus )
        self.canvas.setFocus()
####################################################################   

        # MAKE FIGURE 1 (histogram)
        self.figX1 = matplotlib.figure.Figure(figsize=(5,2), dpi=100)
        self.figX1.set_tight_layout({"pad": .0})
        self.figX1.patch.set_facecolor('white')
        self.canvas1 = FigureCanvas(self.figX1)
        #self.toolbar1 = NavigationToolbar(self.canvas1, self.widget_histogram, coordinates=False)
        #self.vl_histogram.addWidget(self.toolbar1)     
        self.vl_histogram.addWidget(self.canvas1)
        self.ax1 = self.figX1.add_subplot(111)
        # plot on figure
#        self.PB_plotTrans.clicked.connect(self.addmpl)
#        self.PB_align.clicked.connect(self.f_turnAlignmentON)
#        self.PB_integrate.clicked.connect(self.f_turnIntegrationON)

        # MAKE FIGURE 2 (INTEGRATED AREAS)
        self.figX2 = matplotlib.figure.Figure(figsize=(5,2), dpi=100)
        self.figX2.set_tight_layout({"pad": .0})
        self.figX2.patch.set_facecolor('white')
        self.canvas2 = FigureCanvas(self.figX2)
        #self.toolbar2 = NavigationToolbar(self.canvas2, self.widget_areas, coordinates=False)
        #self.vl_IntAreas.addWidget(self.toolbar2)     
        self.vl_IntAreas.addWidget(self.canvas2)
        self.ax2 = self.figX2.add_subplot(111)   
        
    # INSTANCE METHODS
    # Load data from button or from Menu/Open
    def f_openFile(self):
        try:
            self.filesInFolder = QFileDialog.getOpenFileNames(self, 'Open file', '/Users/jennyhallqvist/Documents/Python/Data_for_Python/MRM_files_Trem2_rerun')
            self.filesInFolder=list(self.filesInFolder)

            self.filesInFolder = self.filesInFolder[0]
            self.fileNameShort=[x.split('/')[-1] for x in self.filesInFolder]
            print(self.fileNameShort)
            print(self.filesInFolder)
            self.contentOfFile_all, self.infoOfFile, self.transitionsAll = importData(self.filesInFolder)
#            df = pd.read_csv(self.filesInFolder[0],header=1)
#            print(type(df))  
            self.MRMtrans = []
            self.infoOfFile = self.infoOfFile[1:]
            print(self.infoOfFile)
            for item in self.infoOfFile:
                self.MRMtrans.append(item[2]+'__'+item[3])
                
            self.listWidget_samples.addItems(self.MRMtrans)
            # choose one item in the list
            self.listWidget_samples.itemClicked.connect(self.f_selectItemFromList)
            self.flagListPopulated = True
            self.integrationsAll = pd.DataFrame(index = self.filesInFolder)

        except:
            QMessageBox.critical(self, "ERROR", "An error occurred. Please try again")
            
    # Choose the items in the list
    def f_selectItemFromList(self,itemX):
            print ('\nRESULTS FROM SINGLE SELECTION\n')
            print('Current index, from list: ' + str(self.listWidget_samples.currentRow()))
            print('Current text, from list: ' + self.listWidget_samples.currentItem().text())
            print('Current Item, from itemX: ' + itemX.text())    
            
    # add matplotlib figure (main integration window)   
    def addmpl(self):
        try:
            if self.flagListPopulated == True:
                # add flag for populated list to avoid crash when clicking button
                self.rmmpl() # needs to delete the actual canvas and toolbar
                self.ax = self.figX.add_subplot(111)
                for sampleMRM in self.transitionsAll[self.listWidget_samples.currentRow()]:
                    self.ax.plot(sampleMRM.ix[:,'time'], sampleMRM.ix[:, 'intensity'])
                self.canvas.draw()# draw now!
                self.figX.canvas.mpl_connect('button_press_event', self.f_mouseclick) 
 
        except:
            QMessageBox.critical(self, "ERROR", "An error occurred. Please try again")

    # support function, to remove old figure before plotting new one
    def rmmpl(self):
        # NOTE: mplvl is the name of the layout of the QWidget mplwindow (defined in Designer)
        self.figX.delaxes(self.ax)

    # add matplotlib figure (histogram)                       
    def addmpl1(self):
        try:
            self.rmmpl1() # needs to delete the actual canvas and toolbar
            self.ax1 = self.figX1.add_subplot(111)
            Xrange = range(len(self.integrationsTemp))
            print(Xrange)
            self.ax1.bar(Xrange,self.integrationsTemp.values,facecolor = '0.75', linewidth = 0.0)
            print(self.integrationsTemp.index)
            sampleNames = [str.split(ttemp,'.')[0] for ttemp in self.integrationsTemp.index]
            print(sampleNames)
            #self.ax1.bar.xticks(Xrange, sampleNames, rotation = 'vertical')
            self.canvas1.draw()# draw now!
 
        except:
            QMessageBox.critical(self, "ERROR", "An error occurred. Please try again")
            
    def rmmpl1(self):
        # NOTE: mplvl is the name of the layout of the QWidget mplwindow (defined in Designer)
        self.figX1.delaxes(self.ax1)
        
        
    # add matplotlib figure (integrated areas)                       
    def addmpl2(self):
        try:
            colorsX = matplotlib.cm.rainbow(np.linspace(0,1,len(self.filesInFolder)))       
            self.rmmpl2() # needs to delete the actual canvas and toolbar
            self.ax2 = self.figX2.add_subplot(111)

            for sampleNr in range(len(self.filesInFolder)):
                self.ax2.fill_between(self.xTempAll[sampleNr], 0, self.yTempAll[sampleNr], facecolor = colorsX[sampleNr], alpha = 0.1)
                self.ax2.plot(self.xTempAll[sampleNr], self.yTempAll[sampleNr], color = colorsX[sampleNr], linewidth = 0.5)
            self.canvas2.draw()# draw now!
 
        except:
            QMessageBox.critical(self, "ERROR", "An error occurred. Please try again")                      
            
    def rmmpl2(self):
        # NOTE: mplvl is the name of the layout of the QWidget mplwindow (defined in Designer)
        self.figX2.delaxes(self.ax2)
        
    def f_turnAlignmentON(self):
        self.flagAlignmentModeON = True
        
    def f_turnIntegrationON(self):
        self.flagIntegrationModeON = True
        
    def f_mouseclick(self, event):
        if self.flagAlignmentModeON == True:
            self.alignPoints.append(event.xdata)
            print(self.alignPoints)

            if len(self.alignPoints) == 2:
                #align here
                self.align()
                self.flagAlignmentModeON = False
                self.alignPoints = []
                
        elif self.flagIntegrationModeON == True:
            self.integratePoints.append(event.xdata)
            print(self.integratePoints)
            
            if len(self.integratePoints) == 2:
                self.integrate()
                self.flagIntegrationModeON = False
                self.integratePoints = []
        else:
            print('button=%d, x=%d, y=%d, xdata=%f, ydata=%f' %(event.button, event.x, event.y, event.xdata, event.ydata))
    #        self.labelCoordinates.setText('x='+str(event.xdata)+'  y='+str(event.ydata))
        
    # alignment
    def align(self):

        xMin = self.alignPoints[0]
        xMax = self.alignPoints[1]
        
        ### GET THE HIGHEST VALUE FOR Y IN X'S RANGE
        yMaxAlign = []
        time_at_yMax = []
        for sampleMRM in self.transitionsAll[self.listWidget_samples.currentRow()]:
            idxValminAlign = abs(sampleMRM['time'] - xMin)
            idxValmaxAlign = abs(sampleMRM['time'] - xMax)
            idxMinAlign = idxValminAlign.argmin()
            idxMaxAlign = idxValmaxAlign.argmin()
            idxTempSample = sampleMRM.ix[idxMinAlign:idxMaxAlign,'intensity'].argmax() # index of max y in alignment window
            time_at_yMax.append(sampleMRM.ix[idxTempSample,'time']) 
            
            yMaxAlign.append(np.amax(sampleMRM.ix[idxMinAlign:idxMaxAlign,'intensity']))
        idx_yHighest = yMaxAlign.index(max(yMaxAlign))
        set_time_at_highestPoint = time_at_yMax[idx_yHighest]
        deltaTime = time_at_yMax - set_time_at_highestPoint
        
        c=0
        for sampleMRM in self.transitionsAll[self.listWidget_samples.currentRow()]:
            sampleMRM['time'] = sampleMRM['time'] - deltaTime[c]
            c+=1
        Xlimits = self.ax.get_xlim()
        self.addmpl()
        self.ax.set_ylim([0, max(yMaxAlign)])
        self.ax.set_xlim(Xlimits)
        self.canvas.draw()

    def integrate(self):

        intStart = self.integratePoints[0]
        intEnd = self.integratePoints[1]

        self.integrationsTemp = pd.DataFrame()
        self.xTempAll = []
        self.yTempAll = []
        counter1 = 0
                
        for sampleMRM in self.transitionsAll[self.listWidget_samples.currentRow()]:
            integralTemp, xTemp, yTemp = trapezoidalInt(sampleMRM.ix[:,'time'], sampleMRM.ix[:, 'intensity'], intStart, intEnd)
            transitionsName = [self.infoOfFile[self.listWidget_samples.currentRow()][2] + '__' +self.infoOfFile[self.listWidget_samples.currentRow()][3]]  
#            print(self.fileNameShort)
            integralTemp2 = pd.DataFrame(integralTemp, index=[self.fileNameShort[counter1]], columns=transitionsName)
            print('integralTemp2 = ')
            print(integralTemp2)
            self.integrationsTemp = self.integrationsTemp.append(integralTemp2)
#            print('integrationsTemp = ')
#            print(self.integrationsTemp)
#            xTempAll.append(xTemp)
#            yTempAll.append(yTemp)
            self.xTempAll.append(xTemp)
            self.yTempAll.append(yTemp)
#            print(counter1)            
            counter1 +=1
        self.integrationsAll = pd.concat([self.integrationsAll, self.integrationsTemp], axis=1)
        # Add histogram
        self.addmpl1()
        self.addmpl2()
        
# START HERE 20170821        
#########################
    def f_saveFile(self):



        
#        for sampleNr in range(len(filesInFolder)):
#            matplotlib.pyplot.fill_between(xTempAll[sampleNr], 0, yTempAll[sampleNr], facecolor = colorsX[sampleNr], alpha = 0.1)
#            matplotlib.pyplot.plot(xTempAll[sampleNr], yTempAll[sampleNr], color = colorsX[sampleNr], linewidth = 0.5)
#        mplib.pyplot.xlabel('Time (min)')
#        mplib.pyplot.ylabel('Intensity')
#        mplib.pyplot.title(transitionsName[0])        
#        mplib.pyplot.show(block = False) # Force plot to be shown
#        
#        mplib.pyplot.figure(3)
#        Xrange = range(len(integrationsTemp))
#        sampleNames = [str.split(ttemp,'.')[0] for ttemp in filesInFolder]
#        mplib.pyplot.bar(Xrange,integrationsTemp.values, facecolor = '0.75', linewidth = 0.0) # Bar plot of integrations
#        mplib.pyplot.xticks(Xrange, sampleNames, rotation = 'vertical')
#        mplib.pyplot.xlabel('Sample')
#        mplib.pyplot.ylabel('Intensity')
#        mplib.pyplot.title(transitionsName[0])        
#        mplib.pyplot.show(block = False) # Force plot to be shown
                
if __name__ == '__main__':

    app = QApplication(sys.argv)
    MainWindowMRM_1 = MainWindowMRM()
    MainWindowMRM_1.show()
    sys.exit(app.exec_())  

    
# USEFUL STUFF FOR PLOTTING    
#    def addmplib1(self):
#        self.rmmplib1() # needs to delete the actual canvas and toolbar
#        self.ax1 = self.fig1.add_subplot(111)
#        self.ax1.grid(True)
#        #self.ax1.plot(self.RT2,self.MZ2,'.',markersize=3,color='y')
#        self.ax1.plot(self.RT1,self.MZ1,'.',markersize=3,color='steelblue')
#        #self.canvas1 = FigureCanvas(self.fig1)
#        #self.fig1_layout.addWidget(self.canvas1)
#        self.canvas1.draw()# draw now!
#        self.label_LastAction.setText(' Reference data imported.') 
#        #self.fig1.canvas1.mpl_connect('button_press_event', self.f_mouseclick) 
#    # support function, to remove old figure before plotting new one
#    def rmmplib1(self):
#        #self.fig1_layout.removeWidget(self.canvas1)
#        #self.canvas1.close()
#        self.fig1.delaxes(self.ax1)