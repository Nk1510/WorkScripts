# -*- coding: utf-8 -*-
"""
Created on Thu Sep 12 22:14:39 2019

@author: ADMIN
"""
import numpy as np
import cv2
from cv2 import VideoWriter, VideoWriter_fourcc
import matplotlib.pyplot as plt
import os
import pyprind
import math 


DIR =  [r'G:\CompressionExport\Merges\Mouse18\191107_2']

OutputFile = [r"G:\CompressionExport\Vignettes\BatchS_191107_2_Mouse18.mp4"]

  #Max = 100
Max = 150




for ROLL in range(len(DIR)):
    files = os.listdir(DIR[ROLL])
    
    print(files[0])
    
    vidcap = cv2.VideoCapture(os.path.join(DIR[ROLL],files[0]))
    
    if (vidcap.isOpened()== False):
            print("Error opening video stream or file")
            
    success,image = vidcap.read()
    
    plt.imshow(image,cmap='gray_r')
    plt.show()
    
    length = int(vidcap.get(cv2.CAP_PROP_FRAME_COUNT))
    
    
    height, width , layer = image.shape
    
    vidcap.release()
    
    
    NBfiles= len(files)
        
    #ROWSIZE = int(math.sqrt(NBfiles))
#    ROWSIZE = int(math.sqrt(Max))
    ROWSIZE = math.ceil(math.sqrt(NBfiles))
    print(ROWSIZE) 
    
    new_h = int(height/ROWSIZE)
    new_w = int(width/ROWSIZE)
    
    print(new_h,new_w,NBfiles,length)
    
    VideoArray = np.zeros([new_h, new_w, NBfiles, length])
    
    
    fc = 0
    bar = pyprind.ProgBar(len(files),bar_char='░')
    for f in files:
    
        vidcap = cv2.VideoCapture(os.path.join(DIR[ROLL],f))
        
        if (vidcap.isOpened()== False):
            print("Error opening video stream or file")
            
        success,image = vidcap.read()
        frame = 0
        
        while success:
            
            resize = cv2.resize(image, (new_w, new_h))
            VideoArray[:,:,fc,frame]=resize[:,:,0]
            
            success,image = vidcap.read()
            frame = frame +1
    
        vidcap.release()
        fc=fc+1
        bar.update()
        
    
    #
    #imgplot = plt.imshow(image,cmap='gray_r')
    #plt.show(imgplot)
    codec = "HVEC"
    size = new_w * ROWSIZE , new_h * ROWSIZE
    fourcc = VideoWriter_fourcc(*codec)
    vid = VideoWriter(OutputFile[ROLL], fourcc, 30, size, False)
    
    for I in range(length):
        print(I)
        column = 0
        row = 0
    #    VignetteBuffer = np.full([new_h * ROWSIZE, new_w * ROWSIZE,3],0)
        VignetteBuffer = np.full([new_h * ROWSIZE, new_w * ROWSIZE],0)
        for J in range(NBfiles):
    #            print(I, J, column*new_h , (column+1)*new_h, row*new_w, (row+1)*new_w, "FULLSIZE : ", new_h * ROWSIZE, new_w * ROWSIZE)
    #        VignetteBuffer[column*new_h:(column+1)*new_h , row*new_w : (row+1)*new_w , 0] = VideoArray[:,:,J,I]
            VignetteBuffer[column*new_h:(column+1)*new_h , row*new_w : (row+1)*new_w ] = VideoArray[:,:,J,I]
    #        VignetteBuffer[:,:,1]=VignetteBuffer[:,:,0]
    #        VignetteBuffer[:,:,2]=VignetteBuffer[:,:,0]
            row = row + 1
            if row >= ROWSIZE :
                column = column + 1
                row = 0
                
        vid.write(np.uint8(VignetteBuffer))
    #        plt.imshow(VignetteBuffer,cmap='gray_r')
    #        plt.show()
    #        cv2.imwrite(r"G:\CompressionExport\test{}.bmp".format(I), VignetteBuffer)
    vid.release()
print("Done")
    