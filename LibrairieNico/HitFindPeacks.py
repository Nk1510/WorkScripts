import cv2
from matplotlib import pyplot as plt
from ipywidgets import interact, interactive, fixed, interact_manual
import ipywidgets as widgets
import numpy as np
from PIL import Image
from PIL import ImageFilter
from matplotlib import animation
from PIL import ImageEnhance
from tkinter import filedialog
import tkinter as tk
import pickle
from os import sys
import matplotlib.pyplot as plt
import argparse
from statistics import mean
import os

from scipy.interpolate import interp1d
from scipy.io import loadmat
from scipy import signal as sig
import pandas as pd
import numpy as np




def FindReferenceSystem(video):
    
    HandleBEHAV = cv2.VideoCapture(video, 0)
    length = int(HandleBEHAV.get(cv2.CAP_PROP_FRAME_COUNT))
    
    for framne_nb in range(length-1) :
        _ , IMG1 = HandleBEHAV.read()
        
        linemask= IMG1[140:141, : , 0]
        #print(np.shape(linemask))

        linemask = linemask.flatten()

        smoothmask = smooth(linemask)
        #print(np.shape(smoothmask))
        diffmask = np.diff(smoothmask,n=1)


        X = np.arange(0,np.size(diffmask),1)
        Xinterp = np.arange(0,np.size(diffmask),0.1)

        #print(np.shape(X))
        #print(Xinterp)

        f2 = interp1d(X, abs(diffmask), kind='cubic', fill_value="extrapolate")
        Peaks , values = sig.find_peaks(f2(Xinterp), height = 5.5)
        
        if np.size(Peaks) == 2 : 
            #ListObj1.append(Peaks[0])
            #ListObj2.append(Peaks[1])
            
            #print('2 peaks found at frame : {}, {}'.format(framne_nb, Peaks))
            
            Peaks1 = (((Peaks [0])*10**-1)  - 18)
            Peaks2 = (((Peaks [1])*10**-1)  + 12)
            return [Peaks1,Peaks2] , framne_nb
        
        else :
            continue 

def FindReferenceSystem2(video_path):
    
    HandleBEHAV = cv2.VideoCapture(video_path, 0)
    length = int(HandleBEHAV.get(cv2.CAP_PROP_FRAME_COUNT))
    
    _ , IMG1 = HandleBEHAV.read()

    linemask2= IMG1[601:602, : , 0]

    linemask2 = np.invert(linemask2)
    linemask2 = linemask2.flatten()

    smoothmask = smooth(linemask2)

    b, a = butter(8, 0.075)
    smoothfiltered = filtfilt(b, a, smoothmask)

    diffmask = np.diff(smoothfiltered,n=1)

    PeaksNO2 , values = sig.find_peaks(diffmask, height = 1)

    if np.size(PeaksNO2) == 1 : 
        Peaks3 = ((PeaksNO2 [0])  - 15)
        Peaks4 = ((PeaksNO2 [0])  + 10)
        return [Peaks3,Peaks4]



def OscObj2 (video_path): 
    
    HandleBEHAV = cv2.VideoCapture(video_path, 0)
    length = int(HandleBEHAV.get(cv2.CAP_PROP_FRAME_COUNT))
    _ , IMG1 = HandleBEHAV.read()
    ListObj3 = []

    for framne_nb in range(length-1) :

        _ , IMG1 = HandleBEHAV.read()

        Check = np.vstack((Check , IMG1[601:602, : , 0]))

        linemask = IMG1[601:602, int(Reference_peaks2[0]):int(Reference_peaks2[1])]

        lineIMG = linemask.copy()

        linemask3 = linemask.flatten()

        smoothmask = smooth(linemask3)

        X = np.arange(0,np.size(smoothmask),1)
        Xinterp = np.arange(0,np.size(smoothmask),0.1)
        f2 = interp1d(X, abs(smoothmask), kind='slinear', fill_value="extrapolate")

        raw_interp = f2(Xinterp)

        interpol_img = np.reshape(raw_interp,(1, np.shape(raw_interp)[0]))
        interpol_img = np.vstack((interpol_img,interpol_img,interpol_img,interpol_img,interpol_img,interpol_img,interpol_img,interpol_img,interpol_img,interpol_img))

        b, a = butter(8, 0.075)
        smoothfiltered = filtfilt(b, a, raw_interp)

        diffmask = np.diff(smoothfiltered,n=1)

        DPeaks , values = sig.find_peaks(abs(diffmask), height = 0.045)
        
        

        if np.size(DPeaks) > 0:
            ListObj3.append(DPeaks[0])

        else :

            ListObj3.append(np.nan)

            
    LineFrame = Check[ 0:np.shape(Check)[0] , int(Reference_peaks2[0]):int(Reference_peaks2[1])]

    #print(np.shape(LineFrame))

    Modif = smooth(LineFrame[0,:])

    InterpFrame = Easyinterp(Modif)

    DiffFrame = np.diff(abs(InterpFrame), n=1)

    listmax = [ np.argmin(DiffFrame) ]


    for I in range(1,np.shape(LineFrame)[0],1):

        Modif = np.vstack( ( Modif, smooth(LineFrame[I,:]) ) )
        InterpFrame = np.vstack( ( InterpFrame , Easyinterp(Modif[I,:] ) ) )
        DiffFrame = np.vstack ( ( DiffFrame , diff(InterpFrame[I,:] ) ) )

        listmax.append(np.argmin(DiffFrame[I,:]))





            
def HitDetection(Trial):


    HandleBEHAV = cv2.VideoCapture(Trial, 0)

    length = int(HandleBEHAV.get(cv2.CAP_PROP_FRAME_COUNT))

    ListObj1 = []
    ListObj2 = []


    Reference_peaks, frame = FindReferenceSystem(Trial)


	
    for framne_nb in range(length-1) :


        _ , IMG1 = HandleBEHAV.read()

        linemask2 = IMG1[140:141, int(Reference_peaks[0]):int(Reference_peaks[1])]

        linemask3 = linemask2

        lineIMG = linemask3.copy()

        linemask3 = linemask3.flatten()

        smoothmask = smooth(linemask3)

        diffmask = np.diff(smoothmask,n=1)

        X = np.arange(0,np.size(diffmask),1)
        Xinterp = np.arange(0,np.size(diffmask),0.1)

        f2 = interp1d(X, abs(diffmask), kind='cubic', fill_value="extrapolate")
        DPeaks , values = sig.find_peaks(f2(Xinterp), height = 6)

        if np.size(DPeaks) == 2:

            ListObj1.append(DPeaks[0])
            ListObj2.append(DPeaks[1])
               

        else :

            ListObj1.append(np.nan)
            ListObj2.append(np.nan)

    Listpeaks = []
    Listframe = []    

    SD = np.nanstd(ListObj1)
    MeanPeaks = np.nanmean(ListObj1)
	

    for framne_nb in range(length-1) :
        if ListObj1[framne_nb] >= (MeanPeaks + (4 * SD)):
            Listframe.append(framne_nb)
            Listpeaks.append(ListObj1[framne_nb])

        elif ListObj1[framne_nb] <= (MeanPeaks - (4 * SD)) :
            Listframe.append(framne_nb)
            Listpeaks.append(ListObj1[framne_nb])
			

    if len(Listframe)== 0:
        pass
    else:
        outfile = os.path.join(os.path.dirname(Trial), os.path.basename(Trial) [:-4] + '_Hits.pckl')
        with open(outfile,'wb') as pickleHandle:
            whatever = pickle.dump(Listframe, pickleHandle)
    print('La liste des frames inclues dans l\'interval est :', (Listframe), ' video' , os.path.basename(Trial) [:-4] )  