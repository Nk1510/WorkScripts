# -*- coding: utf-8 -*-
"""
Created on Wed Jul 10 10:55:41 2019

@author: ADMIN
"""

from HirisSeqReader import HirisSeqReader, VideoArrayWrite, Foldersearch, Seq_to_Video
from termcolor import colored
import os
import re
import logging
from datetime import datetime
#from cv2 import VideoWriter, VideoWriter_fourcc, imread, resize
#import matplotlib.pyplot as plt
#import matplotlib.image as mpimg
#import numpy as np
#import imutils


now = datetime.now()

logsBasename = r"G:\CompressionExport\CompressionLogs"
logsFilename = now.strftime("LOGS_%y%m%d_%H-%M-%S.log")

logging.basicConfig(filename=os.path.join(logsBasename,logsFilename),level=logging.DEBUG,format='%(asctime)s %(levelname)s %(name)s %(message)s', datefmt = '%d/%m/%Y %H:%M:%S %p --')

logging.info("")
logging.info("NEW PROGRAMM CALL AT DATE :" + now.strftime("%Y%m%d AND HOUR %H:%M:%S"))
logging.info("-------------------------------------------------------")
logger = logging.getLogger("root")



try :
#    Root = r"F:\MazeWhiskerImaging\batchS_test"
#    Root = r"E:\MazeVideos\BatchS\VideoSideview"
    Root = r"F:\MazeWhiskerImaging"
    output_path_RAW = r"G:\CompressionExport"
    regex = (r"(\w*\\[mM]ouse\d*\\\d{6}_?(VSD)?_?\d*)")
    
    DirsList = os.listdir(Root)
    #print(DirsList)

    #handler = logging.handlers.RotatingFileHandler(filename=os.path.join(logsBasename,logsFilename))
    #handler.doRollover()
  
    
    logger.setLevel(logging.WARNING)
    #handlers = logging.handlers
    #print(handlers)
    TOTAL_FILES = 0
    for Dir in DirsList:
        SubDirsLisr = os.listdir(os.path.join(Root,Dir))
        for Subdir in SubDirsLisr :
            CurrentPath = os.path.join(Root,Dir,Subdir)
            ListOfFiles = Foldersearch(CurrentPath,"Trial.seq")
            for Video in ListOfFiles:
                
                path,file = os.path.split(Video)
                matches = re.finditer(regex, path, re.MULTILINE)
                
                folderStruct = False
                for matchnum, match in enumerate(matches,  start = 1):
                    folderStruct = match.group()
#                    print(folderStruct)
                            
                if not folderStruct:
                    continue
                
                output_path = os.path.join(output_path_RAW,folderStruct)
                
                path,file = os.path.split(Video)
                if file.endswith(".seq") and path != "":
                    output_name = os.path.basename(path)
                else:
                    if path == "" or path == None:
                        output_name = file
                
                FullOutputPathname = os.path.join(output_path,output_name+".mp4")
                
                if os.path.exists(FullOutputPathname):
                    continue
                else :
                    TOTAL_FILES = TOTAL_FILES + 1
                
    print(TOTAL_FILES)
    PROCESSED_FILES = 0
    for Dir in DirsList:
        SubDirsLisr = os.listdir(os.path.join(Root,Dir))
    #    print(SubDirsLisr)
        for Subdir in SubDirsLisr :
            CurrentPath = os.path.join(Root,Dir,Subdir)
            print("Scanning folder {}".format(CurrentPath))
            logger.info("Scanning folder {}".format(CurrentPath))
    
            ListOfFiles = Foldersearch(CurrentPath,"Trial.seq")
#            ListOfFiles = Foldersearch(CurrentPath,"mouse126s03.seq")
            
    #        print(ListOfFiles)
            n=1
            for Video in ListOfFiles:
                
    #            if VideoArray == False:
    #                continue
                path,file = os.path.split(Video)
                matches = re.finditer(regex, path, re.MULTILINE)
                
                folderStruct = False
                for matchnum, match in enumerate(matches,  start = 1):
                    folderStruct = match.group()
#                    print(folderStruct)
                            
                if not folderStruct:
                    continue
                
                output_path = os.path.join(output_path_RAW,folderStruct)
                
                logger.debug(output_path)
                
                path,file = os.path.split(Video)
                if file.endswith(".seq") and path != "":
                    output_name = os.path.basename(path)
                else:
                    if path == "" or path == None:
                        output_name = file
                
                FullOutputPathname = os.path.join(output_path,output_name+".avi")
                
#                if not os.path.exists(FullOutputPathname):
                    
                    
    #                VideoArray = HirisSeqReader(Video)
                
    #                VideoArrayWrite(VideoArray,output_path,input_path=Video)
                    
                Status = Seq_to_Video(Video,output_path,input_path=Video, extension = ".mp4", codec = "HVEC" )
                if Status :
                    PROCESSED_FILES = PROCESSED_FILES + 1
                    print(colored("Video n°{:2d} of {:2d} - {:2d}% complete".format(PROCESSED_FILES,TOTAL_FILES,int((PROCESSED_FILES/TOTAL_FILES)*100)),"magenta"))
                    logger.info("Video n°{:2d} of {:2d} - {:2d}% complete".format(PROCESSED_FILES,TOTAL_FILES,int((PROCESSED_FILES/TOTAL_FILES)*100)))
#                    print(colored("Video n°{:2d} of {:2d} - {:2d}% complete".format(n,len(ListOfFiles),int((n/len(ListOfFiles))*100)),"magenta"))
#                    logger.info("Video n°{:2d} of {:2d} - {:2d}% complete".format(n,len(ListOfFiles),int((n/len(ListOfFiles))*100)))
#                else :
#                    print("Video {} Already Exist, searching next".format(output_name+".avi"))
    #                logger.debug("Video {} Already Exist, searching next".format(output_name+".avi"))
                n=n+1
                
                print()
    
    loggers = ["root","Seq_to_Video"]
    for logname in loggers:
        log = logging.getLogger(logname)
        handlers = list(log.handlers)
    
        for handler in handlers :
            log.removeHandler(handler)
            handler.flush()
            handler.close()
    print(TOTAL_FILES)

except Exception as e :
    print(colored("Error : {}".format(e),"red"))
    logger.error("Error : {}".format(e))



#imgplot = plt.imshow(VideoArray[:,:,0],cmap='gray_r')
#plt.show(imgplot)

