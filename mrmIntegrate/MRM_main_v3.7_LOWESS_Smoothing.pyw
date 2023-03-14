#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: Jenny Hallqvist
"""
import sys
import os
import webbrowser
try:
    from urllib import pathname2url
except:
    from urllib.request import pathname2url
from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog, QMessageBox
from PyQt5 import uic , QtCore
import pandas as pd
import numpy as np
import copy
from MRM_importData_LOWESS_Smoothing import importData
from MRM_trapz_V02 import trapezoidalInt
import matplotlib
matplotlib.use("Qt5Agg")
from matplotlib.backends.backend_qt5agg import (FigureCanvasQTAgg as FigureCanvas, NavigationToolbar2QT as NavigationToolbar)


class MainWindowMRM(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('MRM_v2.ui', self)

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
              
        # ==================================================================================
        # Initiate window for main overlaid chromatogram
        # ==================================================================================
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
        self.canvas.setFocusPolicy(QtCore.Qt.ClickFocus )
        self.canvas.setFocus()  
        # ==================================================================================
        
        # ==================================================================================
        # Initiate window for bar plot
        # ==================================================================================
        self.figX1 = matplotlib.figure.Figure(figsize=(5,2), dpi=100)
        self.figX1.set_tight_layout({"pad": .0})
        self.figX1.patch.set_facecolor('white')
        self.canvas1 = FigureCanvas(self.figX1)    
        self.vl_histogram.addWidget(self.canvas1)
        self.ax1 = self.figX1.add_subplot(111)
        # ==================================================================================

        # ==================================================================================
        # Initiate window for chromatogram of integrated areas
        # ==================================================================================
        self.figX2 = matplotlib.figure.Figure(figsize=(5,2), dpi=100)
        self.figX2.set_tight_layout({"pad": .0})
        self.figX2.patch.set_facecolor('white')
        self.canvas2 = FigureCanvas(self.figX2)  
        self.vl_IntAreas.addWidget(self.canvas2)
        self.ax2 = self.figX2.add_subplot(111)   
        # ==================================================================================
        
    # ==================================================================================
    # Instance methods
    # ==================================================================================
    # Help in file menu
    def f_help(self):
        htmlURL = 'MRM_Help_v1_1.html'
        url = 'file:{}'.format(pathname2url(os.path.abspath(htmlURL)))
        webbrowser.open(url)
    # ==================================================================================
    # Reload data in case of bad alignment            
    def f_reloadData(self):
        try:
            self.transitionsAllCopy = copy.deepcopy(self.transitionsAll)  
        except:
            QMessageBox.critical(self, "ERROR #1","An error occurred. Please try again")   
    # ==================================================================================
    # Open file        
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
                if item[2] == 'SIC':
                    self.MRMtrans.append(item[3]+'__'+item[4])  
                else:
                    self.MRMtrans.append(item[2]+'__'+item[3])  
  
            self.listWidget_samples.addItems(self.MRMtrans)
            self.listWidget_samples.itemClicked.connect(self.f_selectItemFromList)
            self.flagListPopulated = True
            self.integrationsAll = pd.DataFrame()
            self.f_reloadData()
        except:
            pass
    # ==================================================================================
    # Plot selected transition
    def f_plotTransClicked(self):
        try:
            self.addmpl()
            if self.flagWipePlots == True:
                self.ax1.clear() 
                self.canvas1.draw()
                self.ax2.clear()
                self.canvas2.draw()
        except:
            QMessageBox.critical(self, "ERROR #2", "An error occurred. Please try again") 
    # ==================================================================================
    # Select transition from list
    def f_selectItemFromList(self,itemX):
            print ('\nRESULTS FROM SINGLE SELECTION\n')
            print('Current index, from list: ' + str(self.listWidget_samples.currentRow()))
            print('Current text, from list: ' + self.listWidget_samples.currentItem().text())
            print('Current Item, from itemX: ' + itemX.text())    
    # ==================================================================================

    # ==================================================================================
    # Populate main overlaid chromatogram  
    # ==================================================================================
    def addmpl(self):
        try:
            if self.flagListPopulated == True:
                self.rmmpl() 
                self.ax = self.figX.add_subplot(111)
                for sampleMRM in self.transitionsAll[self.listWidget_samples.currentRow()]:
                    self.ax.plot(sampleMRM.loc[:,'time'], sampleMRM.loc[:, 'intensity'])
                self.canvas.draw()
                self.figX.canvas.mpl_connect('button_press_event', self.f_mouseclick) 
        except:
            QMessageBox.critical(self, "ERROR #3","An error occurred. Please try again")
    # ==================================================================================
    # Detelte previous plot before adding new
    # ==================================================================================
    def rmmpl(self): 
        self.figX.delaxes(self.ax)
    # ==================================================================================

    # ==================================================================================
    # Populate bar plot
    # ==================================================================================    
    def addmpl1(self):
        try:
            self.rmmpl1() 
            self.ax1 = self.figX1.add_subplot(111)
            Xrange = range(len(self.integrationsTemp))
            self.ax1.bar(Xrange,self.integrationsTemp.iloc[:,0], facecolor = '0.75', linewidth = 0.0) 
            self.canvas1.draw()
        except:
            QMessageBox.critical(self, "ERROR #4","An error occurred. Please try again")
    # ==================================================================================
    # Detelte previous plot before adding new
    # ==================================================================================
    def rmmpl1(self):
        self.figX1.delaxes(self.ax1)      
    # ==================================================================================
        
    # ==================================================================================
    # Populate plot of integrated chromatogram
    # ==================================================================================  
    def addmpl2(self):
        try:
            colorsX = matplotlib.cm.rainbow(np.linspace(0,1,len(self.filesInFolder)))       
            self.rmmpl2() 
            self.ax2 = self.figX2.add_subplot(111)
            for sampleNr in range(len(self.filesInFolder)):
                self.ax2.fill_between(self.xTempAll[sampleNr], 0, self.yTempAll[sampleNr], 
                                      facecolor = colorsX[sampleNr], alpha = 0.1)
                self.ax2.plot(self.xTempAll[sampleNr], self.yTempAll[sampleNr], 
                              color = colorsX[sampleNr], linewidth = 0.5)
            self.canvas2.draw() 
        except:
            QMessageBox.critical(self, "ERROR #5","An error occurred. Please try again")                      
    # ==================================================================================
    # Detelte previous plot before adding new
    # ==================================================================================
    def rmmpl2(self):
        self.figX2.delaxes(self.ax2)
    # ==================================================================================
    
    # ==================================================================================
    # Integration method    
    # ==================================================================================
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
            QMessageBox.critical(self, "ERROR #6","An error occurred. Please try again")   

    def align(self):
        try:
            xMin = self.alignPoints[0]
            xMax = self.alignPoints[1]
            
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
            
            c = 0
            for sampleMRM in self.transitionsAll[self.listWidget_samples.currentRow()]:
                sampleMRM['time'] = sampleMRM['time'] - deltaTime[c]
                c+=1
            Xlimits = self.ax.get_xlim()
            self.addmpl()
            self.ax.set_ylim([0, max(yMaxAlign)])
            self.ax.set_xlim(Xlimits)
            self.canvas.draw()
        except:
            QMessageBox.critical(self, "ERROR #7","An error occurred. Please try again")   
            
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
                integralTemp, xTemp, yTemp = trapezoidalInt(sampleMRM.loc[:,'time'], 
                                                            sampleMRM.loc[:, 'intensity'], 
                                                            intStart, intEnd)
                
                if self.infoOfFile[self.listWidget_samples.currentRow()][2] == 'SIC':
                    transitionsName = [self.infoOfFile[self.listWidget_samples.currentRow()][3] + ' > ' +self.infoOfFile[self.listWidget_samples.currentRow()][4]]  
                else:                   
                    transitionsName = [self.infoOfFile[self.listWidget_samples.currentRow()][2] + ' > ' +self.infoOfFile[self.listWidget_samples.currentRow()][3]]  

                integralTemp2 = pd.DataFrame(integralTemp, 
                                             index=[self.fileNameShort[counter1]], 
                                             columns=transitionsName)
                self.integrationsTemp = self.integrationsTemp.append(integralTemp2)
                self.xTempAll.append(xTemp)
                self.yTempAll.append(yTemp)
                counter1 +=1
            self.integrationsAll = pd.concat([self.integrationsAll, self.integrationsTemp], axis=1)
            self.addmpl1() 
            self.addmpl2()
        except:
            QMessageBox.critical(self, "ERROR #8","An error occurred. Please try again")           

    def f_saveFile(self):
        try:
            fileName = QFileDialog.getSaveFileName(self,'Save File')
            self.integrationsAll.to_csv(path_or_buf=fileName[0], sep=',', na_rep='', 
                                        float_format=None, columns=None, 
                                        header=True, index=True, 
                                        index_label='Sample name', mode='w')
        except:
            QMessageBox.critical(self, "ERROR #9","An error occurred. Please try again")   
    
    def f_quit(self, event):
        reply = QMessageBox.question(self, "Message", "Are you sure you want to close the application? Any unsaved work will be lost.", QMessageBox.Close | QMessageBox.Cancel, QMessageBox.Cancel)

        if reply == QMessageBox.Close:
            self.close()
            app.quit()           
        else:
            pass
                
if __name__ == '__main__':
    app = QApplication(sys.argv)
    MainWindowMRM_1 = MainWindowMRM()
    MainWindowMRM_1.show()
    sys.exit(app.exec_())  



    
