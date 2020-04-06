# -*- coding: utf-8 -*-
"""
Created on Tue Dec 17 14:28:30 2019

@author: Timothe
"""
#%%
from HirisSeqReader import Foldersearch, QuickRegexp, Repair_HIRIS

from termcolor import colored

import sys
import os
import logging
from datetime import datetime
import tkinter as tk
from tkinter import filedialog
from distutils.dir_util import copy_tree

now = datetime.now()

#%% Changer ici le nom du dossier pour exporter les fichiers dompressé différent. ATTENTION : si il existe des données brutes déja exportées mais pas supprimées, elles seront à nouveau exportées dans ce nouveau sous dossier et il y aura ainsi des doublons 

logsBasename = r"C:\Users\ADMIN\Python\Logs"
logsFilename = now.strftime("LOGS_%y%m%d_%H-%M-%S.log")

logging.basicConfig(filename=os.path.join(logsBasename,logsFilename),level=logging.DEBUG,format='%(asctime)s %(levelname)s %(name)s %(message)s', datefmt = '%d/%m/%Y %H:%M:%S %p --')

logging.info("")
logging.info("NEW PROGRAMM CALL AT DATE :" + now.strftime("%Y%m%d AND HOUR %H:%M:%S"))
logging.info("-------------------------------------------------------")
logger = logging.getLogger("root")

try :
    root = tk.Tk()
    root.attributes("-topmost",True)
    root.withdraw()
    
    
    CHOOSE_INPUT_PATH_ON_START = 1
    TrialFileName              = "Trial" 
    inputBASE                  = r"G:\Compression\BehavioralVideos"
    repairfolder               = r"C:\Users\ADMIN\Python\HIRIS_Repairs"
    
    
    if CHOOSE_INPUT_PATH_ON_START :
        inputBASE = filedialog.askdirectory(parent=root,initialdir=inputBASE,title='Please select an input directory containing "BehavioralVideos"')
    
    print(inputBASE)
    
    regex1 = (r"^[Mm]ouse\d+$")
    regex2 = (r"(\d{6}_?(VSD)?_?\d{0,2})")
    
    INPUT_CHECK = os.path.basename(inputBASE)
    if INPUT_CHECK != "BehavioralVideos":
        logger.warning("Chosen input directory didn't match root basename, incompatible Inupt / output : aborting")
        sys.exit()    

    logger.setLevel(logging.WARNING)
    TOTAL_FILES = 1
    PROCESSED_FILES = 0
    
    for root, dirs, files in os.walk(inputBASE):
        
        for subdir in dirs :
           
            inputSUB = os.path.join(root,subdir)
            Session = QuickRegexp(subdir,regex2)
            if Session is False:
                continue
            
            parentSubfolder = os.path.basename(root)
            Mouseno = QuickRegexp(parentSubfolder,regex1)
            if Mouseno is False:
                logger.warning("No parent folder matched regexp1 at folder :".format(inputSUB))
                continue            
            
            ListOfFiles = Foldersearch(inputSUB,TrialFileName+".seq")
            print(ListOfFiles)
            for Video in ListOfFiles:      
     
                path,file = os.path.split(Video)
                vout_name = os.path.basename(path)
                
                Status, LOG = Repair_HIRIS(repairfolder, Video , inputSUB , output_name = Mouseno+"_"+vout_name+"_Repaired" , extension = ".avi", codec = "MJPG" )

                if Status :
                    PROCESSED_FILES = PROCESSED_FILES + 1
                    print(colored("Video n°{:2d} of {:2d} - {:2d}% complete".format(PROCESSED_FILES,TOTAL_FILES,int((PROCESSED_FILES/TOTAL_FILES)*100)),"magenta"))
                    logger.info("Video n°{:2d} of {:2d} - {:2d}% complete".format(PROCESSED_FILES,TOTAL_FILES,int((PROCESSED_FILES/TOTAL_FILES)*100)))
    #                    print(colored("Video n°{:2d} of {:2d} - {:2d}% complete".format(n,len(ListOfFiles),int((n/len(ListOfFiles))*100)),"magenta"))
    #                    logger.info("Video n°{:2d} of {:2d} - {:2d}% complete".format(n,len(ListOfFiles),int((n/len(ListOfFiles))*100)))
    #                else :
    #                    print("Video {} Already Exist, searching next".format(output_name+".avi"))
    #                logger.debug("Video {} Already Exist, searching next".format(output_name+".avi"))
                else:
                    if LOG == "Frames":
                        CRAPPYDATA_DIRSAVE = os.path.join(outputSUB,vout_name)
                        if not os.path.exists(CRAPPYDATA_DIRSAVE):
                            os.makedirs(CRAPPYDATA_DIRSAVE)
                            copy_tree(os.path.dirname(Video),CRAPPYDATA_DIRSAVE)
                        else:
                            continue
                    print(LOG)
                        
                        
                print()
            
except Exception as e :
    
    exc_type, exc_obj, exc_tb = sys.exc_info()
    fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
    errors = "Exception : " + str(exc_type) + "Object : " + str(exc_obj) + "TB : " + str(exc_tb) +  "File : " + str(fname) + " Line : " +  str(exc_tb.tb_lineno)
    print(colored("Invalid error {} from : {}\n".format(e,errors),"red"))
    logger.error("Invalid error {} from : {}\n".format(e,errors))