# -*- coding: utf-8 -*-
"""
Created on Tue Dec 17 14:28:30 2019

@author: Timothe
"""

from VideoCompression.HirisSeqReader import HirisSeqReader, VideoArrayWrite, Foldersearch, Seq_to_Video
from termcolor import colored
import os
import sys
import re
import logging
from datetime import datetime
import tkinter as tk
from tkinter import filedialog

now = datetime.now()

logsBasename = r"C:\Users\Timothe\NasgoyaveOC\Professionnel\ThèseUNIC\Scripts\Logs\VideoCompression"
logsFilename = now.strftime("LOGS_%y%m%d_%H-%M-%S.log")

logging.basicConfig(filename=os.path.join(logsBasename,logsFilename),level=logging.DEBUG,format='%(asctime)s %(levelname)s %(name)s %(message)s', datefmt = '%d/%m/%Y %H:%M:%S %p --')

logging.info("")
logging.info("NEW PROGRAMM CALL AT DATE :" + now.strftime("%Y%m%d AND HOUR %H:%M:%S"))
logging.info("-------------------------------------------------------")
logger = logging.getLogger("root")

try :
    root = tk.Tk()
    root.withdraw()

    file_path = filedialog.askdirectory(parent=root,initialdir="D:/",title='Please select a directory containing mouses')
    print(file_path)
    
#    Root = r"D:\TestSophie"
#    output_path_RAW = r"D:\TestSophie"
    
    Root = file_path
    output_path_RAW = file_path
    regex1 = (r"^[Ss]ouris\d+$")
    regex2 = (r"(\w*\\[sS]ouris\d*\\\d{6}_?(VSD)?_?\d*)")
    SubdirStorage = "Compressed"
    
    DirsList = os.listdir(Root)
    
    logger.setLevel(logging.WARNING)
    TOTAL_FILES = 1
    PROCESSED_FILES = 0
    for Dir in DirsList:
        dirpath = os.path.join(Root,Dir)
        print(dirpath)
        print(Dir)
        if os.path.isdir(dirpath) :
            matches = re.finditer(regex1, Dir, re.MULTILINE)
            Mouseno = False
            for matchnum, match in enumerate(matches,  start = 1):
                Mouseno = match.group()
                print(Mouseno)
            if not Mouseno:
                continue
            Output_Root = False
            if not os.path.exists(os.path.join(dirpath,SubdirStorage)):
                try :
                    os.makedirs(os.path.join(dirpath,SubdirStorage))
                    Output_Root = os.path.join(dirpath,SubdirStorage)
                except FileExistsError:
                    pass
            Output_Root = os.path.join(dirpath,SubdirStorage)
            print(Output_Root)
            ListOfFiles = Foldersearch(dirpath,"1.seq")
            print(ListOfFiles)
            for Video in ListOfFiles:
                
                path,file = os.path.split(Video)
                vout_name = os.path.basename(path)
                Status = Seq_to_Video(Video,Output_Root,output_name = Mouseno+"_"+vout_name , extension = ".avi", codec = "MJPG" )

                if Status :
                    PROCESSED_FILES = PROCESSED_FILES + 1
                    print(colored("Video n°{:2d} of {:2d} - {:2d}% complete".format(PROCESSED_FILES,TOTAL_FILES,int((PROCESSED_FILES/TOTAL_FILES)*100)),"magenta"))
                    logger.info("Video n°{:2d} of {:2d} - {:2d}% complete".format(PROCESSED_FILES,TOTAL_FILES,int((PROCESSED_FILES/TOTAL_FILES)*100)))
    #                    print(colored("Video n°{:2d} of {:2d} - {:2d}% complete".format(n,len(ListOfFiles),int((n/len(ListOfFiles))*100)),"magenta"))
    #                    logger.info("Video n°{:2d} of {:2d} - {:2d}% complete".format(n,len(ListOfFiles),int((n/len(ListOfFiles))*100)))
    #                else :
    #                    print("Video {} Already Exist, searching next".format(output_name+".avi"))
    #                logger.debug("Video {} Already Exist, searching next".format(output_name+".avi"))
                print()
            
                
except Exception as e :
    
    exc_type, exc_obj, exc_tb = sys.exc_info()
    fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
    errors = "Exception : " + str(exc_type) + "Object : " + str(exc_obj) + "TB : " + str(exc_tb) +  "File : " + str(fname) + " Line : " +  str(exc_tb.tb_lineno)
    print(colored("Invalid error {} from : {}\n".format(e,errors),"red"))
    logger.error("Invalid error {} from : {}\n".format(e,errors))