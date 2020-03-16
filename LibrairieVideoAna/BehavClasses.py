# -*- coding: utf-8 -*-
"""
Created on Fri Nov 30 13:33:55 2018

@author: Timothe
"""

import numpy as np
import math
import pickle
import re

class MazeData:
    
    def __init__(self, Filename):
        
        self.Filename = Filename
        regexpresult=re.match(r"(.*mouse([0-9]+)_([0-9]+)).txt", self.Filename)
        self.MouseNo=regexpresult.group(2)
        self.SessionNo=regexpresult.group(3)
        self.FilenameNoextension=regexpresult.group(1)
        self.file_object  = open(self.Filename, "r")
        self.RawContent = self.file_object.readlines()

    def Organize(self):
        ArrContent = np.zeros((0,5))
        LastLine=[]
        Catch=0
        ActualTime=0
        self.Mode="ChangeBased"
        for lines in range(len(self.RawContent)):
            CurrtLine = self.RawContent[lines][:-1].split("\t")
            for item in range(len(CurrtLine)):
                if not CurrtLine[item]:
                    CurrtLine.pop(item)
            if len(CurrtLine)<4 :
                if Catch==1:
                    break
                continue
            else:
                if Catch == 0:
                    Catch = 1
                else:
                     ActualTime=ActualTime+1
                     
                if CurrtLine == LastLine:
                    if self.Mode == "ChangeBased":
                        self.Mode="TimingBased"                        
                    continue
                else:
                    LastLine = CurrtLine
                    CurrtLine=list(map(int, CurrtLine))
                    if self.Mode == "TimingBased":
                        OutLine=[ActualTime, CurrtLine[0], -1, CurrtLine[1], CurrtLine[2]]
                    elif self.Mode == "ChangeBased":
                        if len(CurrtLine)<5:
                            OutLine=[CurrtLine[0], CurrtLine[1], -1, CurrtLine[2], CurrtLine[3]]
                        else :
                            OutLine=[CurrtLine[0], CurrtLine[1], CurrtLine[2], CurrtLine[3], CurrtLine[4]]
                    else:
                        raise ValueError('Class ''Mode'' property does not match any value expected during ''Organize'' method call')
                    ArrContent=np.vstack((ArrContent, OutLine))
        if np.amax(ArrContent[:,0])>2000000:
            ArrContent[:,0]=ArrContent[:,0]/1000
        self.OrganizedContent=ArrContent
        
        if (np.all(self.OrganizedContent[0,1:])):
            self.Begining=self.OrganizedContent[0,0]
        else:
            self.Begining=0
        
        self.Duration=self.OrganizedContent[-1,0]-self.Begining
        self.DurationMinSec=[math.floor(self.Duration/60000), math.floor((self.Duration % 60000)/1000)]
        
        
    def LickRate(self,seconds):
        lastValue=0       
        ArrLickRate = [0] * math.ceil(self.Duration/(seconds*1000))
        
        for value in range(len(self.OrganizedContent)):
            if self.OrganizedContent[value,1] != lastValue:
                time=math.floor((self.OrganizedContent[value,0]-self.Begining)/(1000*seconds))
                ArrLickRate[time]=ArrLickRate[time]+1  
                lastValue=self.OrganizedContent[value,1]
                
        if self.DurationMinSec[1] < seconds-5 :
            self.ArrLickRate=ArrLickRate[:-1]
        else:
            self.ArrLickRate=ArrLickRate        
    
    def SaveLoad(self,ask):#use sql to save and load dynamically
        if ask=="save":
            with open(self.FilenameNoextension+'.pkl', 'wb') as f: 
                pickle.dump([self.OrganizedContent, self.Mode, self.Duration, self.DurationMinSec], f)
        elif ask=="load":
            with open('objs.pkl', 'rb') as f:
                self.OrganizedContent, self.Mode, self.Duration, self.DurationMinSec = pickle.load(f)
            
    
        

    