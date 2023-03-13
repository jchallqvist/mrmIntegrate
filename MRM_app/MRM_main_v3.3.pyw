#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Mar 12 16:33:44 2017

@author: Jenny
"""


#self.filesInFolder = r'RTMZ_HPosPhase2.csv'
#df = pd.read_excel(self.filesInFolder)
import sys
import os
import webbrowser
try:
    from urllib import pathname2url
except:
    from urllib.request import pathname2url
#import codecs
from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog, QMessageBox
from PyQt5 import uic , QtCore
import pandas as pd
import numpy as np
import copy
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

class MainWindowMRM(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('MRM.ui', self)

        # define the file menu      
        menubar = self.menuBar()
        menubar.setNativeMenuBar(False)
        
        self.action_LoadSamples.triggered.connect(self.f_openFile)
        self.actionSave.triggered.connect(self.f_saveFile)
        self.actionSave_As.triggered.connect(self.f_saveFile)
        self.actionQuit.triggered.connect(self.f_quit)   
        '''browser'''
        self.actionHelp.triggered.connect(self.f_help)           
        self.flagListPopulated = False
        self.flagAlignmentModeON = False
        self.flagIntegrationModeON = False
        self.flagReloadDataModeON = False
        self.flagWipePlots = False
        self.alignPoints = []
        self.integratePoints = []

# MAKE FIGURE 0 (TIC)
# NOTE: In QTdesigner create a button on top of the figure widget,
# then apply grid layout on widget, save, and delete button. 
# This will allow the plot to change size. In this program the layout is called mplvl
# create a canvas to put a figure and toolbar, but do not draw anything yet

        self.figX = matplotlib.figure.Figure(figsize=(5,2), dpi=100)
        self.figX.set_tight_layout({"pad": .0})
        self.figX.patch.set_facecolor('white')
        self.canvas = FigureCanvas(self.figX)
        self.toolbar = NavigationToolbar(self.canvas, self.widget_TIC, coordinates=False)
        self.vl_TIC.addWidget(self.toolbar)     
        self.vl_TIC.addWidget(self.canvas)
        self.ax = self.figX.add_subplot(111)
        self.PB_plotTrans.clicked.connect(self.f_plotTransClicked)
        self.PB_align.clicked.connect(self.f_turnAlignmentON)
        self.PB_integrate.clicked.connect(self.f_turnIntegrationON)
        self.PB_reload.clicked.connect(self.f_turnReloadDataON)
#########THESE TWO LINES WERE ADDED FOR MOUSE CLICK
        self.canvas.setFocusPolicy(QtCore.Qt.ClickFocus )
        self.canvas.setFocus()
####################################################################   

        # MAKE FIGURE 1 (histogram)
        self.figX1 = matplotlib.figure.Figure(figsize=(5,2), dpi=100)
        self.figX1.set_tight_layout({"pad": .0})
        self.figX1.patch.set_facecolor('white')
        self.canvas1 = FigureCanvas(self.figX1)    
        self.vl_histogram.addWidget(self.canvas1)
        self.ax1 = self.figX1.add_subplot(111)


        # MAKE FIGURE 2 (INTEGRATED AREAS)
        self.figX2 = matplotlib.figure.Figure(figsize=(5,2), dpi=100)
        self.figX2.set_tight_layout({"pad": .0})
        self.figX2.patch.set_facecolor('white')
        self.canvas2 = FigureCanvas(self.figX2)  
        self.vl_IntAreas.addWidget(self.canvas2)
        self.ax2 = self.figX2.add_subplot(111)   
        
        
    def f_help(self):
        htmlURL = 'MRM_Help_v1_1.html'
        url = 'file:{}'.format(pathname2url(os.path.abspath(htmlURL)))
#        path = os.path.abspath(htmlURL)
#        url = 'file://' + path
#        
#        with open(path, 'w') as f:
#            f.write(htmlURL)
        webbrowser.open(url)
        
        
    # INSTANCE METHODS
    # Load data from button or from Menu/Open
    def f_reloadData(self):
        try:
            self.transitionsAllCopy = copy.deepcopy(self.transitionsAll)  
        except:
            QMessageBox.critical(self, "ERROR","An error occurred. Please try again")   
                
    def f_openFile(self):
        try:    
            self.filesInFolder = QFileDialog.getOpenFileNames(self, 'Open file')
            self.filesInFolder=list(self.filesInFolder)

            self.filesInFolder = self.filesInFolder[0]
            self.fileNameShort=[x.split('/')[-1] for x in self.filesInFolder]
            self.contentOfFile_all, self.infoOfFile, self.transitionsAll = importData(self.filesInFolder)
            self.MRMtrans = []
            self.infoOfFile = self.infoOfFile[1:]
            self.transitionsAll=self.transitionsAll[1:]
            for item in self.infoOfFile:
#                self.MRMtrans.append(item[3]+'__'+item[4])  
                self.MRMtrans.append(item[2]+'__'+item[3])  
  
            self.listWidget_samples.addItems(self.MRMtrans)
            # choose one item in the list
            self.listWidget_samples.itemClicked.connect(self.f_selectItemFromList)
            self.flagListPopulated = True
            self.integrationsAll = pd.DataFrame()
            self.f_reloadData()
        except:
            pass

    def f_plotTransClicked(self):
        try:
            self.addmpl()
            if self.flagWipePlots == True:
                self.ax1.clear() 
                self.canvas1.draw()
                self.ax2.clear()
                self.canvas2.draw()
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
                    self.ax.plot(sampleMRM.loc[:,'time'], sampleMRM.loc[:, 'intensity'])
                self.canvas.draw()
                self.figX.canvas.mpl_connect('button_press_event', self.f_mouseclick) 
        except:
            QMessageBox.critical(self, "ERROR","An error occurred. Please try again")

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
            self.ax1.bar(Xrange,self.integrationsTemp.values,facecolor = '0.75', linewidth = 0.0)
            self.canvas1.draw()
        except:
            QMessageBox.critical(self, "ERROR","An error occurred. Please try again")
            
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
            QMessageBox.critical(self, "ERROR","An error occurred. Please try again")                      
            
    def rmmpl2(self):
        # NOTE: mplvl is the name of the layout of the QWidget mplwindow (defined in Designer)
        self.figX2.delaxes(self.ax2)
        
    def f_turnAlignmentON(self):
        self.flagAlignmentModeON = True
        
    def f_turnIntegrationON(self):
        self.flagIntegrationModeON = True
        
    def f_turnReloadDataON(self):
        self.flagReloadDataModeON = True
        self.reload()
        
    def reload(self):
        if self.flagReloadDataModeON == True:
            self.transitionsAll = copy.deepcopy(self.transitionsAllCopy)
            self.addmpl() 
            self.flagReloadDataModeON = False
        else:
            pass

        
    def f_mouseclick(self, event):
        try:
            if self.flagAlignmentModeON == True:
                self.alignPoints.append(event.xdata)
                print(self.alignPoints)
    
                if len(self.alignPoints) == 2:
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
        except:
            QMessageBox.critical(self, "ERROR","An error occurred. Please try again")   

    # alignment
    def align(self):
        try:
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
                idxTempSample = sampleMRM.loc[idxMinAlign:idxMaxAlign,'intensity'].argmax() # index of max y in alignment window
                time_at_yMax.append(sampleMRM.loc[idxTempSample,'time']) 
                
                yMaxAlign.append(np.amax(sampleMRM.loc[idxMinAlign:idxMaxAlign,'intensity']))
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
        except:
            QMessageBox.critical(self, "ERROR","An error occurred. Please try again")   
            
    def integrate(self):
        try:
            self.flagWipePlots = True
            intStart = self.integratePoints[0]
            intEnd = self.integratePoints[1]
            self.integrationsTemp = pd.DataFrame()
            self.xTempAll = []
            self.yTempAll = []
            counter1 = 0
            for sampleMRM in self.transitionsAll[self.listWidget_samples.currentRow()]:
                integralTemp, xTemp, yTemp = trapezoidalInt(sampleMRM.loc[:,'time'], sampleMRM.loc[:, 'intensity'], intStart, intEnd)
                transitionsName = [self.infoOfFile[self.listWidget_samples.currentRow()][2] + ' > ' +self.infoOfFile[self.listWidget_samples.currentRow()][3]]  
#                transitionsName = [self.infoOfFile[self.listWidget_samples.currentRow()][3] + ' > ' +self.infoOfFile[self.listWidget_samples.currentRow()][4]]  

                integralTemp2 = pd.DataFrame(integralTemp, index=[self.fileNameShort[counter1]], columns=transitionsName)
                self.integrationsTemp = self.integrationsTemp.append(integralTemp2)
                self.xTempAll.append(xTemp)
                self.yTempAll.append(yTemp)
                counter1 +=1
            self.integrationsAll = pd.concat([self.integrationsAll, self.integrationsTemp], axis=1)
            self.addmpl1()
            self.addmpl2()
        except:
            QMessageBox.critical(self, "ERROR","An error occurred. Please try again")           

    def f_saveFile(self):
        try:
            fileName = QFileDialog.getSaveFileName(self,'Save File')
            self.integrationsAll.to_csv(path_or_buf=fileName[0], sep=',', na_rep='', float_format=None, columns=None, header=True, index=True, index_label='Sample name', mode='w')
        except:
            QMessageBox.critical(self, "ERROR","An error occurred. Please try again")   
    
    def f_quit(self, event):
        reply = QMessageBox.question(self, "Message", "Are you sure you want to close the application? Any unsaved work will be lost.", QMessageBox.Close | QMessageBox.Cancel, QMessageBox.Cancel)

        if reply == QMessageBox.Close:
            app.quit()
        else:
            pass
###
#Add a help as a HTML page that opens when clicking 'help'
                
if __name__ == '__main__':

    app = QApplication(sys.argv)
    MainWindowMRM_1 = MainWindowMRM()
    MainWindowMRM_1.show()
    sys.exit(app.exec_())  

    
