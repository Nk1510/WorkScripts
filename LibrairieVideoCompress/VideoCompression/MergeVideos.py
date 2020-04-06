# -*- coding: utf-8 -*-
"""
Created on Wed Oct 30 21:08:57 2019

@author: ADMIN
"""
import cv2
from cv2 import VideoWriter, VideoWriter_fourcc
import os
import matplotlib.pyplot as plt
import numpy as np
import pyprind



def MergeSideTop(VideoWhiskPath,VideoSidePath,**kwargs):
    
    if "OutputFolder" in kwargs:
        OutputFolder = kwargs.get("OutputFolder")
    else:
        OutputFolder = r"G:\CompressionExport\Merges"
    
    
    VideosWhisk = os.listdir(VideoWhiskPath)
    VideosSide = os.listdir(VideoSidePath)
    
#    print(VideosWhisk)
#    print(VideosSide)
#    print(os.path.join(VideoWhiskPath,VideosWhisk[0]))
#    print(os.path.join(VideoSidePath,VideosSide[0]))
    
    if len(VideosWhisk) != len(VideosSide):
        return False
    
    NBfiles= len(VideosWhisk)
    
    if NBfiles == 0:
        return False
    
    filetest_VideosWhisk = cv2.VideoCapture(os.path.join(VideoWhiskPath,VideosWhisk[0]))
    filetest_VideoSidePath = cv2.VideoCapture(os.path.join(VideoSidePath,VideosSide[0]))
    if (filetest_VideosWhisk.isOpened()== False):
        print("Error opening video stream or file")
        return False
    if (filetest_VideoSidePath.isOpened()== False):
        print("Error opening video stream or file")
        return False
    success,imageWhisk = filetest_VideosWhisk.read()
    success,imageSide = filetest_VideoSidePath.read()
    imageSide = np.rot90(imageSide,1)
    plt.imshow(imageWhisk,cmap='gray_r')
    plt.show()
    plt.imshow(imageSide,cmap='gray_r')
    plt.show()
    
    heightWhisk, widthWhisk , layerWhisk = imageWhisk.shape
    heightSide, widthSide , layerSide = imageSide.shape
    
    filetest_VideosWhisk.release()
    filetest_VideoSidePath.release()
    
    print("NBfiles {}, heightWhisk {}, heightSide {}, widthWhisk {}, widthSide {}, layerWhisk {}, layerSide {}".format(NBfiles,heightWhisk,heightSide,widthWhisk,widthSide,layerWhisk,layerSide))
    
    
    FinalWidth = widthWhisk + widthSide
    FinalHeight = max(heightWhisk,heightSide)
    
    print("FinalWidth {}, FinalHeight {}".format(FinalWidth,FinalHeight))
    
    
    for videoID in range(len(VideosWhisk)):
        
        VIDCAP_VideosWhisk = cv2.VideoCapture(os.path.join(VideoWhiskPath,VideosWhisk[videoID]))
        VIDCAP_VideoSidePath = cv2.VideoCapture(os.path.join(VideoSidePath,VideosSide[videoID]))
        
        lengthWhisk = int(VIDCAP_VideosWhisk.get(cv2.CAP_PROP_FRAME_COUNT))
        lengthSide = int(VIDCAP_VideoSidePath.get(cv2.CAP_PROP_FRAME_COUNT))
        
        FinalLen = min(lengthWhisk,lengthSide)
        
        codec = "HVEC"
        size = FinalWidth , FinalHeight
        fourcc = VideoWriter_fourcc(*codec)
        if os.path.exists(os.path.join(OutputFolder,VideosWhisk[videoID])):
            continue
        
        vidoutput = VideoWriter(os.path.join(OutputFolder,VideosWhisk[videoID]), fourcc, 30, size, False)
        
        try :
            bar = pyprind.ProgBar(FinalLen,bar_char='░')
            for FrameID in range(FinalLen):
                Frame = np.zeros([FinalHeight, FinalWidth])
                
                success,imageWhisk = VIDCAP_VideosWhisk.read()
                success,imageSide = VIDCAP_VideoSidePath.read()
                imageSide = np.rot90(imageSide,1)
                Frame[0:heightWhisk,0:widthWhisk] = imageWhisk[:,:,0]
                Frame[0:heightSide,widthWhisk:FinalWidth] = imageSide[:,:,0]
                
                vidoutput.write(np.uint8(Frame))
                bar.update()
            
        except Exception as e:
            print(e)
        
        print("Folder percentage completion : {}".format(int(videoID/len(VideosWhisk))*100))
        
            
        VIDCAP_VideosWhisk.release()
        VIDCAP_VideoSidePath.release()
        vidoutput.release()

    return True

WhiskeFolder = r"G:\CompressionExport\batchS_test"
SideFolder = r"G:\CompressionExport\VideoSideView"
OutputFolder = r"G:\CompressionExport\Merges"


FoldersW_1 = os.listdir(WhiskeFolder)
FoldersS_1 = os.listdir(SideFolder)

for FolderDive1_W in FoldersW_1 :
    for FolderDive1_S in FoldersS_1:
        if FolderDive1_W == FolderDive1_S :
            print("Match : {} and {} Entering ".format(FolderDive1_W,FolderDive1_S))
            FoldersW_2 = os.listdir(os.path.join(WhiskeFolder,FolderDive1_W))
            FoldersS_2 = os.listdir(os.path.join(SideFolder,FolderDive1_S))
            for FolderDive2_W in FoldersW_2 :
                for FolderDive2_S in FoldersS_2:
                    if FolderDive2_S == FolderDive2_W :
                        print("Match : {} and {} Entering ".format(FolderDive2_W,FolderDive2_S))
                        if not os.path.exists(os.path.join(OutputFolder,FolderDive1_W,FolderDive2_W)):
                            os.makedirs(os.path.join(OutputFolder,FolderDive1_W,FolderDive2_W))
                        Bool = MergeSideTop(os.path.join(WhiskeFolder,FolderDive1_W,FolderDive2_W),os.path.join(SideFolder,FolderDive1_S,FolderDive2_S), OutputFolder = os.path.join(OutputFolder,FolderDive1_W,FolderDive2_W))