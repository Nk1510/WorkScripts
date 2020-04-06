# -*- coding: utf-8 -*-
"""
Created on Fri Mar  6 21:15:06 2020

@author: hubatz
"""

import re
import os

def QuickRegexp(Line,regex, **kwargs):
    
    
    if "groups" in kwargs :
        Groups = kwargs.get("groups")

    else : 
        Groups = False
        
    if Groups:
        matches = re.match(regex, Line, re.MULTILINE)
        if matches :      
            tempMATCH = matches.groups()
            MATCH = []
            for Element in tempMATCH:
                if Element:
                    MATCH.append(Element)
            return MATCH
        else :
            return False
        
    else : 
        matches = re.finditer(regex, Line, re.MULTILINE)
        for matchnum, match in enumerate(matches,  start = 0):
            MATCH = match.group()
            return MATCH
            
    return False


def RegFileSearch(MainInputFolder,regexp, ** kwargs):
    File_List = os.listdir(MainInputFolder)
    if "checkfile" in kwargs: #Care : this function considerably slows down the process and is only necessary in multifolder search
        checkfile = kwargs.get("checkfile")
    else :
        checkfile = False
    if checkfile:
        check_list = []
        for f in File_List:
            if os.path.isfile(os.path.join(MainInputFolder, f)):
                print("Checked")
                check_list.append(f)    
        File_List = check_list
        
    NewDirlist=[] 
    for File in File_List:
        if QuickRegexp(File,regexp):
            NewDirlist.append(os.path.join(MainInputFolder,File))
            
    return NewDirlist

if __name__ == "__main__":

    
    path = r"F:\PYLON_OMISSIONS\Batch6_Pylon\Week6\200306\Session2\Souris37"
    
    
    regex1 = (r"^[Ss]ession(\d+)$")
    regex2 = (r"^[Ss]ouris\d+$")

    Session = QuickRegexp("Session15",regex1,groups = True)
    Souris = QuickRegexp("Souris17",regex2)
    print(Session)
    print(Souris)
    
    Files = RegFileSearch(path,".*\.tiff$",checkfile = False)
    
    print(len(Files))