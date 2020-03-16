# -*- coding: utf-8 -*-
"""
Created on Wed Mar  4 14:47:27 2020

@author: Timothe
"""

import struct
import numpy as np
import os, sys
import pyprind
import sqlalchemy as sql
import pandas as pd

sys.path.append(os.path.dirname(os.path.abspath("__filename__")))

from LibrairieVideoCompress.VideoCompression.HirisSeqReader_V2 import RegFileSearch, AlphaNum_Sort

def GetVSD_FileList(SessionPath):
    
    Files = RegFileSearch(SessionPath,'.*\.rsh$')
    Files = AlphaNum_Sort(Files)
    
    return Files

def GetVSDEventsID(session_id, SQLengine):
    
    query = ("""
    SELECT mouse_number, MS.session_id, timestamp, SD.event_value, event_origin FROM mouses_sessions as MS
	
    INNER JOIN session_detail as SD
	ON MS.session_id = SD.session_id
    
	INNER JOIN event_def as ED
	ON SD.event_value = ED.event_value
    
	INNER JOIN mouses as MO
	ON MO.mouses_id = MS.mouses_id
    
	INNER JOIN training_set_def as TS
	ON TS.training_set_id = MS.training_set_id
    
    where MS.session_id = {0} 
    """)
                     
    df = pd.DataFrame(columns = ['Trial_nb', 'VSD','Expect', 'Surprise','All_Events','All_Timestamps'])
    result_2 = pd.read_sql_query(query.format(session_id), SQLengine)
    
    lastStartEvent = 0
    Trialnb = 0
    Eventindex = 0
    VSD = 1
    Expect = 1
    Surprise = 1
    TimeStampList = []
    ValuesList = []
    for index, row in result_2.iterrows():
        if row['event_value'] == 255 or row['event_value'] == 60 or row['event_value'] == 50 :
        
            if abs(lastStartEvent - row['timestamp']) > 100 :
                
                df.at[Trialnb, 'All_Events'] = ValuesList
                df.at[Trialnb, 'All_Timestamps'] = TimeStampList
                TimeStampList = []
                ValuesList = []
                lastStartEvent = row['timestamp']
                
                Trialnb = Trialnb + 1
                df.at[Trialnb, 'Trial_nb'] = int(Trialnb)
            else :
                df.at[Trialnb, 'Trial_nb'] = int(Trialnb)
            
        if row['event_value'] == 50 :
            df.at[Trialnb, 'VSD'] = int(VSD)
            VSD = VSD +1   
        
        if row['event_value'] == 20 :
            df.at[Eventindex, 'Expect'] = np.nan
            df.at[Eventindex, 'Surprise'] = np.nan
            Eventindex = Eventindex + 1
        if row['event_value'] == 21 :
            df.at[Eventindex, 'Expect'] = int(Expect)
            Expect = Expect + 1
            Eventindex = Eventindex + 1
        if row['event_value'] == 22 :
            df.at[Eventindex, 'Surprise'] = int(Surprise)
            Surprise = Surprise +1
            Eventindex = Eventindex + 1
            
        TimeStampList.append(row['timestamp'])
        ValuesList.append(row['event_value'])
        #df.at[Trialnb, 'All_Events'] = df.at[Trialnb, 'All_Events'].append(row['event_value'])
    if len(TimeStampList) != 0:
        df.at[Trialnb, 'All_Events'] = ValuesList
        df.at[Trialnb, 'All_Timestamps'] = TimeStampList
    
    return df
    

def Check_SessionIsVSD(session_id,SQLengine):

    queryVSD = ("""
     SELECT ts.VSD from training_set_def as ts
    inner join mouse_batches as mb
    on ts.batch = mb.id_batches
    inner join mouses_sessions as ms
    on ms.training_set_id = ts.training_set_id
    where ms.session_id = {0}
     """)
    result = pd.read_sql_query(queryVSD.format(session_id), SQLengine)
    State = result.VSD[0]
    if State:
        return True
    else :
        return False


def GetVSD_Data(InputPath):
    
    Files = ReadRSH(InputPath)
    Data = ReadRSD(Files)
    
    return Data

def ReadRSH(InputPath):
    
    Files = []
    with open(InputPath,'r') as F:
        Line = F.readline()
        while Line :
            if "Data-File-List" in Line:
                FileLine = F.readline()
                while FileLine:
                    if '.rsd' in FileLine or '.rsh' in FileLine :
                        Files.append(os.path.join( os.path.dirname(InputPath) , FileLine.rstrip()))
                    FileLine = F.readline()
                break
            Line = F.readline()
    print(Files)
    return Files

def ReadRSD(InputPath):
    
    FilesPerSequence = 256
    
    for ItemIndex in range(len(InputPath)):
        
        with open( InputPath[ItemIndex] ,'rb') as F:
            
            Size = os.path.getsize(InputPath[ItemIndex])
            
            bar = pyprind.ProgBar(int(Size/1600),bar_char='░', title='{}'.format(InputPath[ItemIndex]))
            
            IntData = []
            byte = F.read(2) #Reading 16 bytes "short integer" Z (negative & positive) natural numbers data (centered around 0 : -32,768 to 32,767)
                        
            cnt = 1
            while byte :
                
                IntData.append(struct.unpack('h', byte))
                byte = F.read(2)
                if cnt % 800 == 0:
                    bar.update() 
                cnt = cnt + 1
            del bar
 
            Data = np.resize(IntData,(FilesPerSequence,100,128))
            

            if ItemIndex == 0:
                
                Image0 = Data[0,:,20:120]
                VarimagesImages = Data[1:,:,20:120]
                
                Images = np.empty((len(InputPath) * FilesPerSequence ,np.shape(VarimagesImages)[1] ,np.shape(VarimagesImages)[2]))
                
                for I in range(FilesPerSequence):
                
                    if I == 0:
                        Images[I,:,:] = Image0
                    else :
                        Images[I,:,:] = VarimagesImages[I-1,:,:] + Image0

            else:
                
                VarimagesImages = Data[:,:,20:120]
                
                for I in range(FilesPerSequence):
                    
                    Images[I+(ItemIndex * FilesPerSequence),:,:] = VarimagesImages[I,:,:] + Image0
                    
            
                         
            # AnalogIn1 = Data[:,0:79,13:13]
            # AnalogIn2 = Data[:,0:79,15:15]
            
            # Stim1 = Data[:,0:79,8:8]
            # Stim2 = Data[:,0:79,9:9]

            #DF_underF = np.empty((np.shape(VarimagesImages)[0]+1,np.shape(VarimagesImages)[1],np.shape(VarimagesImages)[2]))
            
    return Images
            
    
if __name__ == "__main__" :
    
    root = r"\\157.136.60.11\EqShulz\Timothe\MICAM\VSD\Mouse25\200302_VSD1"
    
    inpath = "Last2-2-1.rsh"
    
    Files = ReadRSH(os.path.join(root,inpath))
    
    Data = ReadRSD(Files)