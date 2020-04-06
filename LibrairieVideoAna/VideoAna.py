import mysql.connector
import pandas as pd
import sqlalchemy as sql
import sys, os
from .Commons import *

sys.path.append(os.path.dirname(os.path.abspath("__filename__")))

from LibrairieVSDAna.ReadVSDfile import Check_SessionIsVSD

def GetSessionFolder(session,sql_engine,**kwargs) :
    
    
    """# ---- Example call : 
        # Path = GetSessionFolder(1555, sql_engine, FOV = 'Topview')
    
    # ---- Arguments detail :
        # session : 
            #integer input as the session_id

        # FOV : 
            # string input as the desired field of view.
            #
            # Note that whisker field of view ("Topview", "closeup" and "sideview" - case insensitive)
            # will return the folder containing the compressed video trials (or compression failed subfolders with .seq files)
            # while "Widefield" will return the avi file directly

        # sql_engine 
            # takes the engine used to acess the maze database, can be defined as follows in your main code :
                #
                # import sqlalchemy as sql
                # import mysql.connector
                #
                # connect_stringLab = 'mysql+mysqlconnector://RedCentral:21User*91!@157.136.60.198/maze'
                # sql_engine = sql.create_engine(connect_stringLab)
                #
            # then used for this function as described in the example up above:
                #
                # Path = GetSessionFolder(1555, sql_engine, FOV = 'Topview')

        # ---- Other concerns
            # For speed reasons, if all videos are desired, the kwarg FOV = 'all' can be used and the return will be a dictionnary
            # with all types of folders / videos associated with field of views

            # For now, this function assumes the videos path asked exist and it is up to the user to check that path to folders or path to videos returned actually lead to existing data."""
    
    ## MODIF 02/03/20 : ADD INT(SESSION) TO AVOID BAD COMPARISON  / STRING CONVERTED ON THE FLY FOR MYSQL REQUEST BUT NOT FOR DATAFRAME
   
    query = ("""
        SELECT session_id, session_date, mouse_number, mb.batch_name
        FROM mouses_sessions ms 
        INNER JOIN mouse_batches mb 
        ON mb.id_batches = ms.mouse_batch
        INNER JOIN mouses mo
        ON mo.mouses_id = ms.mouses_id 
        WHERE 
            DATE(session_date) = ( 
            SELECT DATE(session_date)
            FROM mouses_sessions
            WHERE session_id = {0} 
            ) 
            AND session_status = 'active' 
            AND ms.mouses_id = ( 
            SELECT mouses_id 
            FROM mouses_sessions
            WHERE session_id = {0}
            ) 
        ORDER BY session_date;
        """)
    session = int(session)
    
    VSD = Check_SessionIsVSD(session,sql_engine)
    
    if VSD :
        VSD = 'VSD'
    else:
        VSD = ''
    
    result = pd.read_sql_query(query.format(session), sql_engine, params = {"multi":"True"})
    display(result)
    
    Batch = result.batch_name[result['session_id'] == session].iloc[0]
    Mouse = result.mouse_number[result['session_id'] == session].iloc[0]
    Date = result.session_date[result['session_id'] == session].iloc[0].strftime('%y%m%d')
    DaySession = result.index[result['session_id'] == session][0] + 1
    #Date = Date.strftime('%y%m%d')
    
    KnownFOVS = ['WideField','TopView','CloseUp','SideView','VSD']
        
    if 'FOV' in kwargs:
        
        FOV = kwargs.get("FOV")
        
        if FOV.lower() == 'all'.lower() :
            FOV = KnownFOVS
            Nodict = 0
            Session_Path = {}
        else :
            FOV = [FOV]
            Nodict = 1
            
    else : 
        Nodict = 0
        FOV = KnownFOVS.copy()
        Session_Path = {}
    
    for Item in FOV :
        
        
        if QuickRegexp(Item,r'.*VSD.*',case = True) :
            base  ='MICAM'
            sub1 = 'VSD'
            sub2 = ''
            submouse = 'Mouse'+str(Mouse)
            video = 2
            
        elif QuickRegexp(Item,r'.*wide_?field.*',case = True) :
            base  ='BehavioralVideos'
            sub1 = 'WideField_Video'
            sub2 = ''
            submouse = ''
            video = 1
            
        elif QuickRegexp(Item,r'.*top_?view.*',case = True) :
            base  ='BehavioralVideos'
            sub1 = 'Whisker_Video'
            sub2 = 'Whisker_Topview'
            submouse = 'Mouse'+str(Mouse)
            video = 0
            
        elif QuickRegexp(Item,r'.*side_?view.*',case = True) :
            base  ='BehavioralVideos'
            sub1 = 'Whisker_Video'
            sub2 = 'Whisker_Sideview'
            submouse = 'Mouse'+str(Mouse)
            video = 0
            
        elif QuickRegexp(Item,r'.*close_?up.*',case = True) :
            base  ='BehavioralVideos'
            sub1 = 'Whisker_Video'
            sub2 = 'Whisker_Closeup'
            submouse = 'Mouse'+str(Mouse)
            video = 0
            
        else :
            raise RuntimeError('Specified field of view is missspelled or does not exist in curentely defined arboresence.')
        
        if video == 1 :
            Path = os.path.join(base,sub1,sub2,Batch,submouse,str(Date)+'_'+str(DaySession),'Mouse'+str(Mouse)+'_'+str(session)+'_[basename+prendre[0:-4]+regexp].avi')
        elif video == 2:
            Path = os.path.join(base,sub1,submouse,str(Date)+'_VSD'+str(DaySession))
        else :
            Path = os.path.join(base,sub1,sub2,Batch,submouse,str(Date)+'_'+VSD+str(DaySession))
        if Nodict : 
            return Path
        else :
             Session_Path.update({Item: Path})
    
    return Session_Path