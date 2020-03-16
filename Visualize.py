# -*- coding: utf-8 -*-
"""
Created on Mon Mar  2 15:39:15 2020

@author: Timothe
"""

import sys, os
import numpy as np
import matplotlib.cm as pltcm
from matplotlib.backends.qt_compat import QtCore, QtWidgets
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from PyQt5.QtWidgets import QSlider, QPushButton, QLineEdit, QLabel, QGroupBox, QHBoxLayout, QVBoxLayout, QGridLayout, QCheckBox, QWidget
from PyQt5.QtCore import Qt, QThread, pyqtSignal

#import mysql.connector
import sqlalchemy as sql
#import pandas as pd
import scipy.ndimage as scp
import cv2


sys.path.append(r"C:\Users\nkhefif\Desktop\Scripts")

from LibrairieVideoAna.Qt_Explore import MyMplCanvas
from LibrairieVideoAna.VideoAna import GetSessionFolder
from LibrairieVideoAna.Commons import ProgressBarImage
from LibrairieVSDAna.ReadVSDfile import GetVSD_Data, GetVSDEventsID, GetVSD_FileList, Check_SessionIsVSD

from termcolor import colored

from cv2 import VideoWriter, VideoWriter_fourcc, imread

class MyStaticMplCanvas(MyMplCanvas,QThread):
    
    """Simple canvas with a sine plot."""
    
    # def __init__(self, *args, **kwargs):
    #     MyMplCanvas.__init__(self, *args, **kwargs)

    def compute_initial_figure(self):
        t = np.arange(0.0, 3.0, 0.01)
        s = np.sin(2 * np.pi * t)
        self.axes.plot(t, s)
        self.cbar = False
        
    def update_figure(self, frame, **kwargs):
        
        if "Vauto" in kwargs: 
            Vauto = kwargs.get("Vauto")
        else :
            Vauto = True
        
        if "Vmin" in kwargs:
            Vmin = kwargs.get("Vmin")
        else :
            Vmin = 0.975
            
        if "Vmax" in kwargs:
            Vmax = kwargs.get("Vmax")
        else : 
            Vmax = 1.025
            
        if "Cmap" in kwargs:
            Cmap = kwargs.get("Cmap")
        else : 
            Cmap = 'gray'
            
        Cmap = pltcm.get_cmap(Cmap)
        Cmap.set_bad(color='white')
        
        if "Barrels" in kwargs :
            Barrels = kwargs.get("Barrels")
            if Barrels is not False :
                for I in range(np.shape(frame)[0]):
                    for J in range(np.shape(frame)[1]):    
                        if Barrels[I,J] > 100 :
                            frame[I,J] = np.nan
            
        if "Rot" in kwargs:
            Rot = kwargs.get("Rot")
        else :
            Rot = 0
            
        if "Interp" in kwargs :
            interp_method = kwargs.get("Interp")
        else :
            interp_method = 'none'
            
        if Rot :
            frame = np.rot90(frame,Rot)
        
        try:
            self.axes.clear()
            #t = np.arange(0.0, frame, 0.01)
            #s = np.sin(frame * np.pi * t)
            #self.axes.plot(t, s)
            if Vauto :
                im = self.axes.imshow(frame, cmap=Cmap, interpolation=interp_method)
            else:
                im = self.axes.imshow(frame, cmap=Cmap, vmin=Vmin, vmax=Vmax, interpolation=interp_method)
            if self.cbar != False :
                self.cbar.remove()
            self.cbar = self.fig.colorbar(im, ax = self.axes )
            self.draw()
        except Exception as e:
            print("Error in update_figure while setting frame {} : {} ".format(frame,e))
        


class LoadVideo(QThread):
    
    LoadIntermediateFrame = pyqtSignal()
    LoadFullFile = pyqtSignal()
    
    def __init__(self, VideoHandle, typed):
        super(LoadVideo, self).__init__()
        
        self.VideoHandle = VideoHandle
        self.PBimage = []
        self.FrameArray = []
        self.wait = 1
        self.type_data = typed
                 
    def run(self):
        print("Entered loading Trial with values : {} : {}".format(self.VideoHandle,self.type_data))
        if self.type_data == 0 :
            Nextprogress = 0.05
            width  = int(self.VideoHandle.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(self.VideoHandle.get(cv2.CAP_PROP_FRAME_HEIGHT))
            length = int(self.VideoHandle.get(cv2.CAP_PROP_FRAME_COUNT))
            self.FrameArray = np.empty((height,width,length))
            
            for i in range(length):
                _ , IMG = self.VideoHandle.read()
                self.FrameArray[:,:,i] = IMG[:,:,0]
                if i/length > Nextprogress :
                    self.PBimage = ProgressBarImage(Nextprogress)
                    Nextprogress = Nextprogress + 0.05
                    self.LoadIntermediateFrame.emit()
            self.LoadFullFile.emit()
            
            # while self.wait:
            #     self.msleep(1)
            # print("Frames Loading finished")
        else :
            self.FrameArray = GetVSD_Data(self.VideoHandle)
            self.LoadFullFile.emit()


class VisualizeGUI(QtWidgets.QMainWindow):
    
    def __init__(self):
        QtWidgets.QMainWindow.__init__(self)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.setWindowTitle("application main window")
        
        self.LocalPath = r"\\157.136.60.11\EqShulz\Timothe"
        
        connect_string = 'mysql+mysqlconnector://RedCentral:21User*91!@157.136.60.198/maze?use_pure=True'
        self.sql_engine = sql.create_engine(connect_string)
        
        self.file_menu = QtWidgets.QMenu('&File', self)
        self.file_menu.addAction('&Quit', self.fileQuit,
                                 QtCore.Qt.CTRL + QtCore.Qt.Key_Q)
        self.menuBar().addMenu(self.file_menu)
        
        self.VideoPath = ""
        self.videoHandle = []
        self.VideoFileList = []
        self.FrameArray = []
        self.VSDFrameArray = []
        
        self.VSDinTrial  = 0
        self.Init = 0

        self.main_widget = QtWidgets.QWidget(self)
        
        
        self.sc = MyStaticMplCanvas(self.main_widget, width=5, height=4, dpi=100)
        
        self.sc_VSD = MyStaticMplCanvas(self.main_widget, width=5, height=4, dpi=100)
        
        
        
        FrameSliderBox = QGroupBox()
        
        self.Frameslider = QSlider(Qt.Horizontal, self.main_widget)
        self.Frameslider.setMinimum(0)
        self.Frameslider.setMaximum(0)
        self.Frameslider.setValue(0)
                
        Framesliderlabel = QLabel("Frames")
        Framesliderlabel.setBuddy(self.Frameslider)
        self.FrameIDsliderlabel = QLabel("-")
        self.FrameIDsliderlabel.setBuddy(self.Frameslider)
        
        self.Frameslider.valueChanged.connect(self.UpdateFigures)
        self.Frameslider.valueChanged.connect(self.UpdateFrameIDLabel)
        self.Frameslider.setMinimumWidth(280)
        
        l = QHBoxLayout()
        l.addWidget(Framesliderlabel)
        l.addWidget(self.Frameslider)
        l.addWidget(self.FrameIDsliderlabel)
        
        FrameSliderBox.setLayout(l)
        
        
        TrialSliderBox = QGroupBox()
        
        self.TrialSlider = QSlider(Qt.Horizontal, self.main_widget)
        self.TrialSlider.setMinimum(0)
        self.TrialSlider.setMaximum(0)
        self.TrialSlider.setValue(0)
                
        TrialSliderlabel = QLabel("Trials")
        TrialSliderlabel.setBuddy(self.TrialSlider)
        self.TrialIDSliderlabel = QLabel("-")
        self.TrialIDSliderlabel.setBuddy(self.TrialSlider)
        
        self.TrialSlider.sliderReleased.connect(self.UpdateFrameSlider)
        self.TrialSlider.valueChanged.connect(self.UpdateTrialIDLabel)
        self.TrialSlider.setMinimumWidth(280)
        
        l = QHBoxLayout()
        l.addWidget(TrialSliderlabel)
        l.addWidget(self.TrialSlider)
        l.addWidget(self.TrialIDSliderlabel)
        
        TrialSliderBox.setLayout(l)
        
        
        VSDcontastBox = QGroupBox()
        
        self.VSDMax = QLineEdit("1.025")
        self.VSDMin = QLineEdit("0.975")
        self.AutoVSD = QCheckBox("Auto")
        self.Cmap = QLineEdit("jet")
        self.Interp = QLineEdit("none")
        self.InterpValue = QLineEdit("2")
        
        self.VSDMax.setMaximumWidth(50)
        self.VSDMin.setMaximumWidth(50)
        self.Cmap.setMaximumWidth(50)
        self.Interp.setMaximumWidth(50)
        self.InterpValue.setMaximumWidth(50)
        
        self.VSDMax.returnPressed.connect(self.UpdateFigures)
        self.VSDMin.returnPressed.connect(self.UpdateFigures)
        self.AutoVSD.stateChanged.connect(self.UpdateFigures)
        self.Cmap.returnPressed.connect(self.UpdateFigures)
        self.Interp.returnPressed.connect(self.UpdateFigures)
        self.InterpValue.returnPressed.connect(self.UpdateFigures)   
        
        l = QGridLayout()
        
        l.addWidget(self.VSDMax,0,0,1,1)
        l.addWidget(self.VSDMin,1,0,1,1)
        l.addWidget(self.AutoVSD,2,0,1,1)
        l.addWidget(self.Cmap,0,1,1,1)
        l.addWidget(self.Interp,1,1,1,1)
        l.addWidget(self.InterpValue,2,1,1,1)
        
        VSDcontastBox.setLayout(l)
        
        VSDCalculationsBox = QGroupBox()
        
        self.Substract = QCheckBox("Substract")
        self.Frame = QLineEdit("0")
        self.BarrelsChkBox = QCheckBox("BarrelMap")
        
        self.Frame.setMaximumWidth(50)
        
        self.Substract.stateChanged.connect(self.UpdateFigures)
        self.Frame.returnPressed.connect(self.UpdateFigures)
        self.BarrelsChkBox.stateChanged.connect(self.UpdateFigures)
        
        l = QGridLayout()
        
        l.addWidget(self.Substract,0,0,1,1)
        l.addWidget(self.Frame,1,0,1,1)
        l.addWidget(self.BarrelsChkBox,2,0,1,1)
        
        
        VSDCalculationsBox.setLayout(l)
        
        
        self.ControlBOX = QGroupBox()
        
        l = QGridLayout()
        
        l.addWidget(TrialSliderBox,0,0,1,3)
        l.addWidget(FrameSliderBox,1,0,1,3)
        
        l.addWidget(VSDcontastBox,0,3,2,1)
        l.addWidget(VSDCalculationsBox,0,4,2,1)
        
        self.ControlBOX.setLayout(l)
        
        self.ControlBOX.setDisabled(True)

                
        self.OpenButton = QPushButton("Open Video")
        self.OpenButton.clicked.connect(self.OpenVideo)
        
        self.SessionBox = QLineEdit("1656")
        self.INFOLABEL = QLabel("-")
        
        
        l = QtWidgets.QVBoxLayout(self.main_widget)
        
        
        
        self.addToolBar(NavigationToolbar(self.sc, self))
                
        l.addWidget(self.OpenButton)
        l.addWidget(self.SessionBox)
        l.addWidget(self.INFOLABEL)
        l.addWidget(self.sc)
        l.addWidget(self.sc_VSD)
        l.addWidget(self.ControlBOX)
        

        self.main_widget.setFocus()
        self.setCentralWidget(self.main_widget)

    
    # def UpdateVSDScale(self):
        
    #     print("Updating scale with values : {} : {}".format())
        
        
    def UpdateFigures(self):
        
        self.sc.update_figure(self.FrameArray[:,:,self.Frameslider.value()], Vauto = True)
        
        if self.VSDinTrial == 1:
            
            if self.Substract.isChecked() == True:
                CurrFrame = self.VSDFrameArray[int(self.Frameslider.value()),:,:] / self.VSDFrameArray[int(self.Frame.text()),:,:]
            else :
                CurrFrame = self.VSDFrameArray[int(self.Frameslider.value()),:,:] 
                
            if self.Interp.text() != 'none':
                CurrFrame = scp.gaussian_filter(CurrFrame,int(self.InterpValue.text()))
                
            if self.BarrelsChkBox.isChecked() == True :
                _barrels = self.Barrels
            else:
                _barrels = False
            
            if self.AutoVSD.isChecked() == True :
                self.sc_VSD.update_figure(CurrFrame, Vauto = True, Cmap = self.Cmap.text())
            else :
                Min = float(self.VSDMin.text())
                Max = float(self.VSDMax.text())
                self.sc_VSD.update_figure(CurrFrame, Vmin = Min, Vmax = Max, Vauto = False, Cmap = self.Cmap.text(), Barrels = _barrels)
                
        self.UpdateInfoLabel()
        
    def UpdateInfoLabel(self):
        
        if Check_SessionIsVSD(self.Session,self.sql_engine):
        
            if not np.isnan(self.Expect_EVENTS[self.TrialSlider.value()]):
                Special = "Expext trial n°{}".format(self.Expect_EVENTS[self.TrialSlider.value()])
            elif not np.isnan(self.Surprise_EVENTS[self.TrialSlider.value()]):
                Special = "Surprise trial n°{}".format(self.Surprise_EVENTS[self.TrialSlider.value()])
            else :
                Special = ''
        else :
            Special = ''
            
        self.INFOLABEL.setText('Session {}- Trial{}- Frame{} {}'.format(self.Session,self.TrialSlider.value(),self.Frameslider.value(),Special))
        
    def fileQuit(self):
        self.close()

    def closeEvent(self, ce):
        self.fileQuit()
        
    # def DisableAllButTrials(self):
        
    #     self.ControlBOX.setDisabled(True)
        
        
    # def EnableAll(self):
    
    # def DisableAll(self:)
        
    def OpenVideo(self):
        
        if self.Init == 0:
            self.Init = 1
            
        self.ControlBOX.setDisabled(True)
        
        self.Session = self.SessionBox.text()
        self.VideoPath = os.path.join(self.LocalPath, GetSessionFolder(self.Session, self.sql_engine, FOV='topView'))
        
        print(self.VideoPath)
        
        if Check_SessionIsVSD(self.Session,self.sql_engine):
        
            self.VSDVideoPath = os.path.join(self.LocalPath, GetSessionFolder(self.Session, self.sql_engine, FOV = 'VSD'))
        
            Dataframe = GetVSDEventsID(self.Session, self.sql_engine)
            self.VSD_EVENTS = Dataframe['VSD'].tolist()
            self.Expect_EVENTS   = Dataframe['Expect'].tolist()
            self.Surprise_EVENTS = Dataframe['Surprise'].tolist()
            self.Behavior_Events = Dataframe['Trial_nb'].tolist()
            
        
            print(self.VSDVideoPath)
            
        else :
            print("No VSD for this session")

        try :
            self.UpdateTrialSlider()
            # self.TrialSlider.setEnabled(True)
            # if not os.path.isfile(self.VideoFileList[self.TrialSlider.value()]):
            #     raise ValueError("Video does not exist")
            self.Barrels = imread(r"\\157.136.60.11\EqShulz\Timothe\MICAM\VSD\Mouse25\BarrelMap\TransparentWhiteBarrels25.png",0)
                      
            
        except Exception as e :
            print(colored("Could not open video : {} Resulting error : {}".format(self.VideoFileList[self.TrialSlider.value()],e),"red"))
    
    def UpdateFrameIDLabel(self):
        
        self.FrameIDsliderlabel.setText(str(self.Frameslider.value()))
    
    def UpdateTrialIDLabel(self):
        
        self.TrialIDSliderlabel.setText(str(self.TrialSlider.value()))
    
    
    def AssignValuesAndExit(self):
        
        print("Entered BEHI Assign")
        self.FrameArray = self.LoadThread.FrameArray
        self.LoadThread.wait = 0
        self.LoadThread.exit() 
        self.sc.update_figure(self.FrameArray[:,:,self.Frameslider.value()])
        
        self.ControlBOX.setDisabled(False)
        
    def AssignVSDValuesAndExit(self):
        
        print("Entered VSD Assign")
        self.VSDFrameArray = self.LoadVSDThread.FrameArray
        self.LoadVSDThread.wait = 0
        self.LoadVSDThread.exit() 
        self.sc_VSD.update_figure(self.VSDFrameArray[self.Frameslider.value(),:,:])
    
    
    def UpdateFrameSlider(self):
        
        if self.Init == 0:
            self.FrameArray = np.zeros([100, 100])
        else :
        
            self.ControlBOX.setDisabled(True)
            
            old_value = self.Frameslider.value()
            print(self.VideoFileList[self.TrialSlider.value()])
            videoHandle = cv2.VideoCapture(self.VideoFileList[self.TrialSlider.value()])
            
            length = int(videoHandle.get(cv2.CAP_PROP_FRAME_COUNT))
            
            print(length)
            self.Frameslider.setMinimum(0)
            self.Frameslider.setMaximum(length-1)
            
            self.LoadThread = LoadVideo(videoHandle,0)
            self.LoadThread.LoadIntermediateFrame.connect(lambda : self.sc.update_figure(self.LoadThread.PBimage))
            self.LoadThread.LoadFullFile.connect(self.AssignValuesAndExit)
            self.LoadThread.start() 
            
            if Check_SessionIsVSD(self.Session,self.sql_engine):
                
                if np.max(self.VSD_EVENTS) == len(self.VSDVideoFileList):
                    print("VSD matching event numbers")
                
                
                if not np.isnan(self.VSD_EVENTS[self.TrialSlider.value()]):
                    
                    self.VSDinTrial = 1
                    
                    VSDvideoHandle = self.VSDVideoFileList[self.VSD_EVENTS[self.TrialSlider.value()]-1]
                    
                    self.LoadVSDThread = LoadVideo(VSDvideoHandle,1)
                    self.LoadVSDThread.LoadFullFile.connect(self.AssignVSDValuesAndExit)
                    self.LoadVSDThread.start() 
                    
                else :
                    
                    self.VSDinTrial = 0
                    
            if length >= old_value:
                self.Frameslider.setValue(old_value)
            else:
                self.Frameslider.setValue(length)
                
        self.UpdateInfoLabel()
        
    def UpdateTrialSlider(self):      
        
        Count = 0
        self.VideoFileList = []
        for root, dirs, files in os.walk(self.VideoPath, topdown=True):
            for name in files:
                if name[-4:] == '.avi':
                    self.VideoFileList.append(os.path.join(root, name))
                    Count = Count + 1
        print("Found {} behavioral videos".format(len(self.VideoFileList)))
        
        if len(self.VideoFileList) == 0:
            print("Can't Proceed for this session, no video found for behavior")
            return
        
        if Check_SessionIsVSD(self.Session,self.sql_engine):
            
            self.VSDVideoFileList = GetVSD_FileList(self.VSDVideoPath)
            print("Found {} VSD videos".format(len(self.VSDVideoFileList)))
            
            if len(self.VSDVideoFileList) == 0:
                print("Can't Proceed for this session, no video found for VSD")
                return
        
        self.TrialSlider.setMinimum(0)
        self.TrialSlider.setMaximum(Count)
        self.TrialSlider.setValue(0)

        self.UpdateFrameSlider()
        
    # def keyPressEvent(self, event):
    #     val = 0
    #     if event.key()==Qt.Key_Right:
    #         self.Frameslider.setValue(self.Frameslider.value() + 1)
    #         val = 1
    #     elif event.key()==Qt.Key_Left:
    #         self.Frameslider.setValue(self.Frameslider.value() - 1)
    #         val = 1
    #     if val == 1:
    #         self.UpdateFigures()
    #     else:
    #         QWidget.keyPressEvent(self, event)
        
        
    
if __name__ == "__main__":
    
    progname = os.path.basename(sys.argv[0])
    qApp = QtWidgets.QApplication(sys.argv)

    aw = VisualizeGUI()
    aw.setWindowTitle("%s" % progname)
    aw.show()
    sys.exit(qApp.exec_())