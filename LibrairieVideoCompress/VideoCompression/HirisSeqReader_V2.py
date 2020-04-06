#!/usr/bin/env python
# -*- coding: utf-8 -*-
#Modif Timothé :
#    Supression de l'export en fichier tiffs,
#    Récuperation de l'array numpy contenant l'image et stack dans un array 3D retourné (VideoArray) avec la 3e dimension = temps
#    Ajout de quelques outputs pour suivre état de fonctionnement du script par utilisateur final
#    Ajout d'une barre de progression dans le même but
#    Création de la fonction VideoCompressionWrite qui prends la sortie de HirisSeqReader et crée 
#    le fichier à l'emplacement indiqué avec les paramètre souhaités
###

##Native imports
import struct
import os
from termcolor import colored
import sys
import gc
import logging
import re


##Unused imports

#import csv
#import mmap
#import datetime
#import array

#import glob
#import time

##Extension libraries imports
import configparser
import numpy as np
import pyprind
from cv2 import VideoWriter, VideoWriter_fourcc, imread

#import matplotlib.pyplot as plt
#import matplotlib.image as mpimg

#from cv2 import cv

def Seq_to_Video(seq_path,output_folder,**kwargs):
    """
        Lecture du fichier binaire de sÃ©quence sqb
        Les donnÃ©es sont reprÃ©sentÃ©es par la structure en C suivante :
            typedef struct
            {   
                long offset;        // 4 bits -> + 4 bits vides car mÃ©moire alignÃ©e
                double TimeStamp;   // 8 bits
                int binfile;        // 4 bits -> + 4 bits vides car mÃ©moire alignÃ©e
            } IMGDATA;
    """
        
    logger = logging.getLogger("Seq_to_Video")
    
    logger.setLevel(logging.INFO)
    
            
    if not os.path.exists(seq_path):
        print(colored("INFO : File do not exist, in folder : {}".format(seq_path),"red"))
        logger.error("INFO : File do not exist, in folder : {}".format(seq_path))
        return False, "input file do not exist"
    
    logger.info("Opening file {}".format(seq_path))
    
    if "alerts" in kwargs:
        alerts = kwargs.get("alerts")
    else:
        alerts = True    
    
    if "output_name" in kwargs:
        output_name = kwargs.get("output_name")
    else :
        input_path = seq_path
        path,file = os.path.split(input_path)
        if file.endswith(".seq") and path != "":
            output_name = os.path.basename(path)
        else:
            if path == "" or path == None:
                output_name = file
#                    sys.exit("ERROR 2 INVALID_PATH : You must either specify a filename with : output_name = ""Nameofyourfile"" (better practice is doing it iteratively) or the path input to get the seq file, used in HirisSeqReader, with input_path = ""pathtoyourvideo"" ")
            else :
                if "\\" not in path:
                    output_name = path
                else :
                    output_name = os.path.basename(path)
                    
    if "extension" in kwargs:
        extension = kwargs.get("extension")
    else:
        if alerts :
            print(colored("Using default extension (.avi) as none was specified","blue"))
            logger.debug("Using default extension (.avi) as none was specified")
        extension = ".avi"
        
    if "fps" in kwargs:
        fps = kwargs.get("fps")
    else:
        fps = 30
        if alerts :
            print(colored("Using default framerate (30 fps) as none was specified","blue"))
            logger.debug("Using default framerate (30 fps) as none was specified")
            
    if "codec" in kwargs:
        codec = kwargs.get("codec")
    else:
        codec = "MJPG"
        if alerts :
            print(colored("Using default codec (MJPG) as none was specified","blue"))
            logger.debug("Using default codec (MJPG) as none was specified")
        
    if "color" in kwargs:
        color = kwargs.get("color")
    else:
        color = False
        if alerts :
            print(colored("Interpreting data as greyscale images as no color info was specified","blue"))
            logger.debug("Interpreting data as greyscale images as no color info was specified")
            
    FullOutputPathname = os.path.join(output_folder,output_name+extension)
    
    logger.debug(output_folder)
    logger.debug(output_name)
    logger.debug(FullOutputPathname)
    
    if os.path.exists(FullOutputPathname):
        print("Video {} Already Exist, searching next".format(output_name+".avi"))
        logger.info("File {} already exist, skipping".format(FullOutputPathname))
        return False, "output file already exist"
    
    cfg = configparser.ConfigParser()
    cfg.read(seq_path)
    
    try:
        width = int(cfg.get('Sequence Settings', 'Width'))
        height = int(cfg.get('Sequence Settings', 'Height'))
        bpp = int(cfg.get('Sequence Settings', 'BytesPerPixel'))
        num_images = cfg.get('Sequence Settings', 'Number of files')
        bin_file = cfg.get('Sequence Settings', 'Bin File')
        sqb_path = seq_path.replace('.seq', '.sqb')
    except Exception as e:
        print(colored("Error : {} on file : {}".format(e,seq_path),"red"))
        logger.error("Error : {} on file : {}".format(e,seq_path))
        return False, "seq config read"
    
        
    pathstr = os.path.dirname(seq_path)
    if height < 10 or width < 10 :
        logger.error("Error on file : {}".format(seq_path) + "Width or Heidth not compliant (<10)")
        return False, "Dimension"
    if int(num_images) < 10 :
        #for files in os.path.dirname(seq_path) :
            #QuickRegexp(files)
            #if True:
        #        pass#ADD CODE HERE TO TEST IF FILE IS CORRUPTED OR SIMPLY END OF A SESSION
        logger.error("Error on file : {}".format(seq_path) + "Number of frames not compliant (<10)")
        return False, "Frames"
    
    if not os.path.exists(output_folder):
        try :
            os.makedirs(output_folder)
        except FileExistsError:
            pass
    
    size = width , height 
    fourcc = VideoWriter_fourcc(*codec)
    vid = VideoWriter(FullOutputPathname, fourcc, fps, size, color)  
            
#    VideoArray = np.empty([height,width,int(num_images)])
    
    print("Processing Sequence : {}".format(seq_path))
    print("Video format : {} x {}".format(height,width))
    
    print(colored("Writing to {}".format(FullOutputPathname),"green"))
    
       
    bar = pyprind.ProgBar(int(num_images),bar_char='░')
    
    with open(sqb_path,'rb') as f :
        try :
            for i in range(0, int(num_images)):
                offset = struct.unpack('l', f.read(4))
                
                #This variables are unused but file has to be read in a specific order to acess the valuable data 
    #            padding = f.read(4)
    #            timestamp = struct.unpack('d', f.read(8))
                f.read(4)
                struct.unpack('d', f.read(8))
                #End of unused variables
                
                binfile = struct.unpack('i', f.read(4))
                
                #This variables are unused but file has to be read in a specific order to acess the valuable data 
    #            padding = f.read(4)
                f.read(4)
                #End of unused variables
                
    #            print(offset)
                
                bin_path = "%s\\%s%0.5d.bin" % (pathstr, bin_file, binfile[0])
    #            tiff_file_path =  "%s_%0.5d.tif" %(tiff_path, i)
                
                f_bin = open(bin_path, 'rb')
                f_bin.seek(offset[0], os.SEEK_SET)
                
                bytes = f_bin.read(height*width*bpp)
                
                if bpp == 2:
                    buffer = np.frombuffer(bytes, dtype=np.uint16)
                else:
                    buffer = np.frombuffer(bytes, dtype=np.uint8)
                
                nparr2 = buffer.reshape(height, width)
    #            cv2.imwrite(tiff_file_path, nparr2)
                f_bin.close()
    #            imgplot = plt.imshow(nparr2,cmap='gray_r')
    #            plt.show(imgplot)
    #            print(np.shape(nparr2))
    #            input()
    #            VideoArray[:,:,i] = nparr2
                
                vid.write(np.uint8(nparr2))
                
                bar.update()
                
    #            for ImageIndex in range(np.size(VideoArray,2)):
                
    #        print(ImageIndex)
                
           
            vid.release()
        except Exception as e:
            print(colored("Error : {} on file : {}".format(e,seq_path),"red"))
            logger.error("Error : {} on file : {}".format(e,seq_path))
            return False, "binary file I/O"
    del bar
    del cfg
#    del VideoArray
    gc.collect()
    print()
    print("Video compression {} sucessfull".format(seq_path))
    logger.info("Video compression {} sucessfull".format(seq_path))
    return True, "none"




def HirisSeqReader(seq_path):
    """
        Lecture du fichier binaire de sÃ©quence sqb
        Les donnÃ©es sont reprÃ©sentÃ©es par la structure en C suivante :
            typedef struct
            {   
                long offset;        // 4 bits -> + 4 bits vides car mÃ©moire alignÃ©e
                double TimeStamp;   // 8 bits
                int binfile;        // 4 bits -> + 4 bits vides car mÃ©moire alignÃ©e
            } IMGDATA;
    """

    cfg = configparser.ConfigParser()
    cfg.read(seq_path)
    
    width = int(cfg.get('Sequence Settings', 'Width'))
    height = int(cfg.get('Sequence Settings', 'Height'))
    bpp = int(cfg.get('Sequence Settings', 'BytesPerPixel'))
    num_images = cfg.get('Sequence Settings', 'Number of files')
    bin_file = cfg.get('Sequence Settings', 'Bin File')
    sqb_path = seq_path.replace('.seq', '.sqb')
    
    pathstr = os.path.dirname(seq_path)
    if height < 0 or width< 0 or int(num_images) < 0 :
        return False
            
    VideoArray = np.empty([height,width,int(num_images)])
    
    
    
    print("Processing Sequence : {}".format(seq_path))
    print("Video format : {} x {}".format(height,width))
    bar = pyprind.ProgBar(int(num_images),bar_char='░')
    
    with open(sqb_path,'rb') as f :
        for i in range(0, int(num_images)):
            offset = struct.unpack('l', f.read(4))
            
            #This variables are unused but file has to be read in a specific order to acess the valuable data 
#            padding = f.read(4)
#            timestamp = struct.unpack('d', f.read(8))
            f.read(4)
            struct.unpack('d', f.read(8))
            #End of unused variables
            
            binfile = struct.unpack('i', f.read(4))
            
            #This variables are unused but file has to be read in a specific order to acess the valuable data 
#            padding = f.read(4)
            f.read(4)
            #End of unused variables
            
#            print(offset)
            
            bin_path = "%s\\%s%0.5d.bin" % (pathstr, bin_file, binfile[0])
#            tiff_file_path =  "%s_%0.5d.tif" %(tiff_path, i)
            
            f_bin = open(bin_path, 'rb')
            f_bin.seek(offset[0], os.SEEK_SET)
            
            bytes = f_bin.read(height*width*bpp)
            
            if bpp == 2:
                buffer = np.frombuffer(bytes, dtype=np.uint16)
            else:
                buffer = np.frombuffer(bytes, dtype=np.uint8)
            
            nparr2 = buffer.reshape(height, width)
#            cv2.imwrite(tiff_file_path, nparr2)
            f_bin.close()
#            imgplot = plt.imshow(nparr2,cmap='gray_r')
#            plt.show(imgplot)
#            print(np.shape(nparr2))
#            input()
            VideoArray[:,:,i] = nparr2
            bar.update()
    
    del bar
    del cfg
    print("Video reading sucessfull")
    return VideoArray
    

def VideoArrayWrite(VideoArray,output_folder,**kwargs):
    
    if not os.path.exists(output_folder):
        try :
            os.makedirs(output_folder)
        except FileExistsError:
            pass
    
    if "alerts" in kwargs:
        alerts = kwargs.get("alerts")
    else:
        alerts = True    
    
    if "output_name" in kwargs:
        output_name = kwargs.get("output_name")
    else:
        #ERROR 2 FLAG: LOOK FOR REASON HERE : BEGINING  
        if "input_path" in kwargs:
            input_path = kwargs.get("input_path")
            path,file = os.path.split(input_path)
            if file.endswith(".seq") and path != "":
                output_name = os.path.basename(path)
            else:
                if path == "" or path == None:
                    output_name = file
#                    sys.exit("ERROR 2 INVALID_PATH : You must either specify a filename with : output_name = ""Nameofyourfile"" (better practice is doing it iteratively) or the path input to get the seq file, used in HirisSeqReader, with input_path = ""pathtoyourvideo"" ")
                else :
                    if "\\" not in path:
                        output_name = path
                    else :
                        output_name = os.path.basename(path)
        else :
            #ERROR 2 FLAG : LOOK FOR REASON HERE : END   
            sys.exit("ERROR 2 FILE_NOT_FOUND : You must either specify a filename with : output_name = ""Nameofyourfile"" (better practice is doing it iteratively) or the path input to get the seq file, used in HirisSeqReader, with input_path = ""pathtoyourvideo"" ")
    print(output_name)         
    if "extension" in kwargs:
        extension = kwargs.get("extension")
    else:
        if alerts :
            print(colored("Using default extension (.avi) as none was specified","blue"))
        extension = ".avi"
        
    if "fps" in kwargs:
        fps = kwargs.get("fps")
    else:
        fps = 30
        if alerts :
            print(colored("Using default framerate (30 fps) as none was specified","blue"))
        
    if "codec" in kwargs:
        codec = kwargs.get("codec")
    else:
        codec = "MJPG"
        if alerts :
            print(colored("Using default codec (MJPG) as none was specified","blue"))
        
    if "color" in kwargs:
        color = kwargs.get("color")
    else:
        color = False
        if alerts :
            print(colored("Interpreting data as greyscale images as no color info was specified","blue"))
            
    FullOutputPathname = os.path.join(output_folder,output_name+extension)
    
    size = np.size(VideoArray,1) , np.size(VideoArray,0)    
        
    fourcc = VideoWriter_fourcc(*codec)
    
    
    vid = VideoWriter(FullOutputPathname, fourcc, fps, size, color)
    
    bar = pyprind.ProgBar(int(np.size(VideoArray,2)),bar_char='▓')
    
    for ImageIndex in range(np.size(VideoArray,2)):
        vid.write(np.uint8(VideoArray[:,:,ImageIndex]))
#        print(ImageIndex)
        bar.update()
    vid.release()
    del bar
    del VideoArray
    print("Video compression and writing sucessfull\n")
   
    gc.collect()
    
    
    
def Foldersearch(MainInputFolder,VideoName):
    DirList = os.listdir(MainInputFolder)
    NewDirlist=[]
    for Subdir in DirList:
        if os.path.exists(os.path.join(MainInputFolder,Subdir,VideoName)):
            NewDirlist.append(os.path.join(MainInputFolder,Subdir,VideoName))
    return NewDirlist


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

def BinarySearch(InputFolder,extension):
    DirList = os.listdir(InputFolder)
    NewDirlist=[]
    try:
        for Subdir in DirList:
            FILE = os.path.join(InputFolder,Subdir)
            if os.path.exists(FILE) and FILE.endswith(extension):
                NewDirlist.append(Subdir)
    except Exception as e:
        print(e)
    return NewDirlist

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

def AlphaNum_Sort(List):
    convert = lambda text: int(text) if text.isdigit() else text
    alphanum_key = lambda key: [convert(c) for c in re.split('([0-9]+)',key)]
    return sorted(List, key = alphanum_key)
            

def Repair_HIRIS(repairfolder,damagedVideopath,outputfolder,**kwargs):
    
    logger = logging.getLogger("Repair_HIRIS")
    
    logger.setLevel(logging.INFO)
    
    if "expectedFrames" in kwargs:
        expectedFrames = kwargs.get("expectedFrames")
    else:
        expectedFrames = 500 
    
    if "alerts" in kwargs:
        alerts = kwargs.get("alerts")
    else:
        alerts = True    
    
    if "output_name" in kwargs:
        output_name = kwargs.get("output_name")
    else :
        output_name = os.path.basename(os.path.dirname(damagedVideopath))
                    
    if "extension" in kwargs:
        extension = kwargs.get("extension")
    else:
        extension = ".avi"
        if alerts :
            print(colored("Using default extension (.avi) as none was specified","blue"))
            logger.debug("Using default extension (.avi) as none was specified")
        
        
    if "fps" in kwargs:
        fps = kwargs.get("fps")
    else:
        fps = 30
        if alerts :
            print(colored("Using default framerate (30 fps) as none was specified","blue"))
            logger.debug("Using default framerate (30 fps) as none was specified")
            
    if "codec" in kwargs:
        codec = kwargs.get("codec")
    else:
        codec = "MJPG"
        if alerts :
            print(colored("Using default codec (MJPG) as none was specified","blue"))
            logger.debug("Using default codec (MJPG) as none was specified")
        
    if "color" in kwargs:
        color = kwargs.get("color")
    else:
        color = False
        if alerts :
            print(colored("Interpreting data as greyscale images as no color info was specified","blue"))
            logger.debug("Interpreting data as greyscale images as no color info was specified")
    
    
    FullOutputvideo = os.path.join(outputfolder,output_name+extension)
    if os.path.exists(FullOutputvideo):
        return False, "out video exists"
    
    
    cfg = configparser.ConfigParser()
    cfg.read(damagedVideopath)
    
    try:
        width = int(cfg.get('Sequence Settings', 'Width'))
        height = int(cfg.get('Sequence Settings', 'Height'))
        bpp = int(cfg.get('Sequence Settings', 'BytesPerPixel'))
        
        RepairSubFolder = str(width)+"x"+str(height)+"-"+str(expectedFrames)
        
        TrialName = os.path.basename(damagedVideopath)
        sqb_Name = TrialName.replace('.seq', '.sqb')
        TrialName = TrialName[0:-4]
        sqb_path = os.path.join(repairfolder,RepairSubFolder,sqb_Name)
        
        pathstr = os.path.dirname(damagedVideopath)
        
        
    except Exception as e:
        print(colored("Error : {} on file : {}".format(e,damagedVideopath),"red"))
        logger.error("Error : {} on file : {}".format(e,damagedVideopath))
        return False, "seq config read"
    
    
    ListDAMAGED_BINs = BinarySearch(pathstr,".bin")
    ListCORRECTER_BINs = BinarySearch(os.path.join(repairfolder,RepairSubFolder),".bin")
    try :
        ListDAMAGED_BINs = AlphaNum_Sort(ListDAMAGED_BINs)
        ListCORRECTER_BINs = AlphaNum_Sort(ListCORRECTER_BINs)
    except Exception as e :
        print(colored("Error : {} on file : {}".format(e,damagedVideopath),"red"))
        logger.error("Error : {} on file : {}".format(e,damagedVideopath))
        return False, "sorting failed"
    
    if len(ListDAMAGED_BINs) != len(ListCORRECTER_BINs):
        print(colored("Insufficient nb of binaries for file : {}".format(damagedVideopath),"red"))
        logger.error("Insufficient nb of binaries for file : {}".format(damagedVideopath))
        return False, "insufficient binary files"
    
    try:
        size = width , height 
        fourcc = VideoWriter_fourcc(*codec)
        vid = VideoWriter(FullOutputvideo, fourcc, fps, size, color)  
    except Exception as e:
        print(colored("Error : {} on file : {}".format(e,FullOutputvideo),"red"))
        logger.error("Error : {} on file : {}".format(e,FullOutputvideo))
        return False, "videowirte open fail"
    
    print("Repairing Sequence : {}".format(damagedVideopath))
    print("Video format : {} x {}".format(height,width))
    
    print(colored("Writing to {}".format(FullOutputvideo),"green"))
    
       
    bar = pyprind.ProgBar(int(expectedFrames),bar_char='░')
    

    
    with open(sqb_path,'rb') as f :
        try :
            for i in range(0, int(expectedFrames)):
                offset = struct.unpack('l', f.read(4))
                
                #This variables are unused but file has to be read in a specific order to acess the valuable data 
    #            padding = f.read(4)
    #            timestamp = struct.unpack('d', f.read(8))
                f.read(4)
                struct.unpack('d', f.read(8))
                #End of unused variables
                
                binfile = struct.unpack('i', f.read(4))
                
                #This variables are unused but file has to be read in a specific order to acess the valuable data 
    #            padding = f.read(4)
                f.read(4)
                #End of unused variables
                
                bin_number = "_%0.5d.bin" % (binfile[0])
                Index = ListCORRECTER_BINs.index(TrialName+bin_number)
                
    #            print(offset)
                bin_path = os.path.join(pathstr,ListDAMAGED_BINs[Index])
                
                
    #            tiff_file_path =  "%s_%0.5d.tif" %(tiff_path, i)
                
                f_bin = open(bin_path, 'rb')
                f_bin.seek(offset[0], os.SEEK_SET)
                
                bytes = f_bin.read(height*width*bpp)
                
                if bpp == 2:
                    buffer = np.frombuffer(bytes, dtype=np.uint16)
                else:
                    buffer = np.frombuffer(bytes, dtype=np.uint8)
                
                nparr2 = buffer.reshape(height, width)
    #            cv2.imwrite(tiff_file_path, nparr2)
                f_bin.close()
    #            imgplot = plt.imshow(nparr2,cmap='gray_r')
    #            plt.show(imgplot)
    #            print(np.shape(nparr2))
    #            input()
    #            VideoArray[:,:,i] = nparr2
                
                vid.write(np.uint8(nparr2))
                
                bar.update()
                
    #            for ImageIndex in range(np.size(VideoArray,2)):
                
    #        print(ImageIndex)

        except Exception as e:
            vid.release()
            print(colored("Error : {} on file : {}".format(e,damagedVideopath),"red"))
            logger.error("Error : {} on file : {}".format(e,damagedVideopath))
            return False, "binary file I/O"
        
    vid.release()
    del bar
    del cfg
#    del VideoArray
    gc.collect()
    print()
    print("Video compression {} sucessfull".format(damagedVideopath))
    logger.info("Video compression {} sucessfull".format(damagedVideopath))
    return True, "none"
    
def Compress_Tiffvideo(TiffFiles,OutputVideo, ** kwargs):
    
    logger = logging.getLogger("Compress_Tiffvideo")
    
    logger.setLevel(logging.INFO)
    
    TiffFiles = AlphaNum_Sort(TiffFiles)
    
    print("Treating video : {} at {}".format(os.path.basename(OutputVideo),os.path.dirname(OutputVideo)))
    
    if "alerts" in kwargs:
        alerts = kwargs.get("alerts")
    else:
        alerts = True
    
    if "fps" in kwargs:
        fps = kwargs.get("fps")
    else:
        fps = 30
        if alerts :
            print(colored("Using default framerate (30 fps) as none was specified","blue"))
            logger.debug("Using default framerate (30 fps) as none was specified")
    
    if "codec" in kwargs:
        codec = kwargs.get("codec")
    else:
        codec = "MJPG"
        if alerts :
            print(colored("Using default codec (MJPG) as none was specified","blue"))
            logger.debug("Using default codec (MJPG) as none was specified")
    
    if "color" in kwargs:
        color = kwargs.get("color")
    else:
        color = False
        if alerts :
            print(colored("Interpreting data as greyscale images as no color info was specified","blue"))
            logger.debug("Interpreting data as greyscale images as no color info was specified")
    
    bar = pyprind.ProgBar(len(TiffFiles),bar_char='░')
    
    print("Processing a {} frames video".format(len(TiffFiles)))
    Index = 0
    bar.update()
    for File in TiffFiles:
        
        image = imread(File, 0)
        
        if Index == 0:
            Index = 1
            SIZE = np.shape(image)
            size = SIZE[1] , SIZE[0] 
            fourcc = VideoWriter_fourcc(*codec)
            vid = VideoWriter(OutputVideo, fourcc, fps, size, color)
            vid.write(np.uint8(image))
            
        else :
        
            vid.write(np.uint8(image))
                
        bar.update()
        
    try :
        del bar
        vid.release()
        return True
        
    except Exception as e:
        
        print(colored("Error Compress_Tiffvideo 2: {} on file : {}".format(e,OutputVideo),"red"))
        logger.error("Error Compress_Tiffvideo 2: {} on file : {}".format(e,OutputVideo))
        return False