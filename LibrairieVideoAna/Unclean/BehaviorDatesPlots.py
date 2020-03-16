# -*- coding: utf-8 -*-
"""
Created on Tue Mar  5 19:49:17 2019

@author: Timothe
"""

import mysql.connector
import numpy as np
import matplotlib.pyplot as plt
import calendar
from datetime import datetime, timedelta


def BehaviorDatesPlots(query, mousesID):
    
    cnx = mysql.connector.connect(host="127.0.0.1",user="Tim",passwd="Turion162!",db="maze")
    
    DataArray= np.empty([2,0])
    
    cursor = cnx.cursor()
    Add=(int(mousesID[0]),)
    cursor.execute(query, Add)
    for sessions in cursor:
        DataArray = np.append(DataArray, [[float(sessions[0])], [sessions[1]]], axis = 1)       
    cursor.close()
    
    
    #print(DataArray)   
      
    for I in range(1,len(mousesID)):
        TempArray= np.empty([2,0])
        
        cursor = cnx.cursor()
        Add=(int(mousesID[I]),)
        cursor.execute(query, Add)
        for sessions in cursor:
            TempArray = np.append(TempArray, [[float(sessions[0])], [sessions[1]]], axis = 1)
        cursor.close()
        
        #print(TempArray)  
        
        buff = np.zeros([1,DataArray.shape[1]])
        
        buff.fill(np.nan)

        DataArray = np.insert(DataArray, DataArray.shape[0]-1 , buff, axis = 0)

        DataL = 0
        L=0
        
        #print(DataArray.shape[1])
        #print(TempArray.shape[1])
        
        while L < TempArray.shape[1]:
            
            #print(DataArray)
                       
            #print(L)
            #print(DataL)
            #print(L+DataL)
            
            if (L+DataL) < DataArray.shape[1] :
                
                #print(TempArray[1,L])
                #print(DataArray[-1,L+DataL])
            
                if TempArray[1,L] == DataArray[-1,L+DataL]:
                    DataArray[-2,L+DataL]=TempArray[0,L]

                elif TempArray[1,L] < DataArray[-1,L+DataL]:

                    buff = np.zeros([1,DataArray.shape[0]-2])
                    buff.fill(np.nan)
                    #print(buff)

                    buff = np.append(buff, [[TempArray[0,L],TempArray[1,L]]] ,axis = 1)
                    DataArray = np.insert(DataArray, L+DataL, buff, axis = 1)


                elif TempArray[1,L] > DataArray[-1,L+DataL]:
                    DataL = DataL+1
                    L=L-1
            else :
                
                buff = np.zeros([DataArray.shape[0]-2,1])
                buff.fill(np.nan)
                #print(buff)
                buff = np.append(buff, [[TempArray[0,L]],[TempArray[1,L]]] ,axis = 0)
                
                #print(buff)
                #print(DataArray)
                
                DataArray = np.append(DataArray, buff, axis = 1 )
                #print(DataArray)
            
            L=L+1
            # print("\n")
    
    #print("OUT")
    DateCapture = 0
    Catch = 0
    
    #print(DataArray.shape[1])
    
    for I in range(DataArray.shape[1]):
        #print(DataArray[-1,I])
        #print(DateCapture)
        
        if I > 0:
            if DateCapture == DataArray[-1,I]:
                if Catch == 1 :
                    DataArray[-1,I] = np.nan
                    #print("RemoveDate")
                    
                else :
                    DateCapture = DataArray[-1,I]
                    DataArray[-1,I] = np.nan 
                    Catch = 1
                    #print("Date Equal to precedent")
            else :
                Catch = 0
                
                DateCapture = DataArray[-1,I]
                #print("New date")
        else :  
            DateCapture = DataArray[-1,I]
            #print("I = 0")
        #print("\n")
        

    
    DataJ = 0
    for J in range(DataArray.shape[0]-1):
        buff = np.arange(DataArray.shape[1])
        buff= buff.astype(float)
        #print(buff)
        for U in range(DataArray.shape[1]):
            if np.isnan(DataArray[J+DataJ,U]) :
                buff[U] = np.nan
        #print(buff)
        DataArray = np.insert(DataArray, J+DataJ+1, buff ,axis = 0)
        DataJ = DataJ+1
            
    print(DataArray)
     
    return DataArray