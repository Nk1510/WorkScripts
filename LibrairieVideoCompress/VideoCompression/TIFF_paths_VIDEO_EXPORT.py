# -*- coding: utf-8 -*-
"""
Created on Tue Dec 17 14:28:30 2019

@author: Timothe
"""
#%%
from HirisSeqReader import RegFileSearch, Seq_to_Video, QuickRegexp, Compress_Tiffvideo

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

logsBasename = r"C:\Users\hubatz\Documents\Python Scripts\Compression\Logs"
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
    inputBASE                  = r"F:\PYLON_OMISSIONS"
    outputBASE                 = r"F:\Compression\PYLON_OMISSIONS"
    
    if CHOOSE_INPUT_PATH_ON_START :
        inputBASE = filedialog.askdirectory(parent=root,initialdir=inputBASE,title='Please select an input directory containing "BehavioralVideos"')
    
    print(inputBASE)
    print(outputBASE)
    
    regex1 = (r"^[Ss]ouris\d+.*$")
    regex2 = (r"^[Ss]ession(\d+)$")
    regex3 = (r"(\d{6})")
    
    VideoSuffix = "_pylon" 
#    INPUT_CHECK = os.path.basename(inputBASE)
#    if INPUT_CHECK != "BehavioralVideos":
#        logger.warning("Chosen input directory didn't match root basename, incompatible Inupt / output : aborting")
#        sys.exit()    

    logger.setLevel(logging.WARNING)
    TOTAL_FILES = 1
    PROCESSED_FILES = 0
    
    for root, dirs, files in os.walk(inputBASE):
        
        for subdir in dirs :
           
            inputSUB = os.path.join(root,subdir)
            
            Mouseno = QuickRegexp(subdir,regex1)
            if Mouseno is False:
                continue
                    
            Session = QuickRegexp(os.path.basename(root),regex2,groups = True)
            if Session is False:
                logger.warning("No parent folder matched regexp2 at folder :".format(inputSUB))
                continue
            Session=Session[0]
            
            Date = QuickRegexp(os.path.basename(os.path.dirname(root)),regex3)
            if Date is False:
                logger.warning("No parent folder matched regexp2 at folder :".format(inputSUB))
                continue
            
            print(Mouseno,Session,Date)

            
            parentSubfolder = os.path.basename(root)
            
            commonINOUT = os.path.commonprefix((inputBASE,inputSUB))
            relativeArborescence = os.path.relpath(inputSUB,commonINOUT)
            outputSUB = os.path.join(outputBASE,relativeArborescence)
            if not os.path.exists(outputSUB):
                os.makedirs(outputSUB)
            
            
            ListOfFiles = RegFileSearch(inputSUB,".*\.tiff$")
            print(len(ListOfFiles))
            if len(ListOfFiles) > 0 :
            
                OutputName = os.path.join(outputSUB, Mouseno+"_"+Date+"_"+Session+VideoSuffix+".avi" )
                
                if not os.path.exists(OutputName):
                
                    Compress_Tiffvideo(ListOfFiles,OutputName,fps = 50)
                
                    print()
            
except Exception as e :
    
    exc_type, exc_obj, exc_tb = sys.exc_info()
    fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
    errors = "Exception : " + str(exc_type) + "Object : " + str(exc_obj) + "TB : " + str(exc_tb) +  "File : " + str(fname) + " Line : " +  str(exc_tb.tb_lineno)
    print(colored("Invalid error {} from : {}\n".format(e,errors),"red"))
    logger.error("Invalid error {} from : {}\n".format(e,errors))