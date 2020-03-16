# -*- coding: utf-8 -*-
"""
Created on Mon May 27 16:11:20 2019

@author: Timothe
"""

import mysql.connector
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import calendar
import datetime
from datetime import timedelta
import random

def SessionsList(mouse, trainingset):

    cnx = mysql.connector.connect(host="127.0.0.1",user="Tim",passwd="Turion162!",db="maze")

    cursor = cnx.cursor()

    query = ("""
              SELECT distinct(session_id) FROM maze.mouses_sessions as ms
                INNER JOIN mouses as mo ON mo.mouses_id = ms.mouses_id
                where training_set_id = %s and mouse_number = %s
                order by session_date
              """)
    Add= (trainingset,mouse)
    cursor.execute(query, Add)
    result=cursor.fetchall()
    cursor.close()
    SList=[y for x in result for y in x]
    
    return SList

def SessionDetail(sessionid,arglist):
    query = ("""
            SELECT event_value FROM session_detail sd
            WHERE session_id = %s AND event_value IN(""")
    i = 0
    for I in arglist :
        if i >= len(arglist)-1:
            query = query + str(I)
        else:
            query = query + str(I) + ", "  
        i = i+1   
    query = query + ") ORDER BY timestamp"
             
    cnx = mysql.connector.connect(host="127.0.0.1",user="Tim",passwd="Turion162!",db="maze")
    
    cursor = cnx.cursor()
    Add= (sessionid,)
    cursor.execute(query, Add)
    result=cursor.fetchall()
    cursor.close()
    Dlist = [y for x in result for y in x]
    
    return Dlist

def MouseList(trainingset):
    
    cnx = mysql.connector.connect(host="127.0.0.1",user="Tim",passwd="Turion162!",db="maze")
    
    cursor = cnx.cursor()
    query = ("""
        SELECT distinct(mouse_number) FROM maze.mouses_sessions as ms
        INNER JOIN mouses as mo ON mo.mouses_id = ms.mouses_id
        where training_set_id = %s
        order by mouse_number""")  
    Add= (trainingset,)
    cursor.execute(query, Add)
    result=cursor.fetchall()
    cursor.close()
    Mlist = [y for x in result for y in x]
    
    return Mlist

def TrainingsetName(trainingset):
    
    cnx = mysql.connector.connect(host="127.0.0.1",user="Tim",passwd="Turion162!",db="maze")
    cursor = self.cnx.cursor()
    query = ("""
            SELECT training_set_name, training_set_description FROM maze.training_set_def as ms
            where training_set_id = %s""")
    Add= (trainingset,)
    cursor.execute(query, Add)
    result=cursor.fetchall()
    cursor.close()
    Mlist = [y for x in result for y in x]
    print("Select: {} : {} : {}".format(trainingset,Mlist[0],Mlist[1]))
    return Mlist[0]
    
def _test():
    assert SessionDetail(0,[1]) == []

if __name__ == '__main__':
    _test()
