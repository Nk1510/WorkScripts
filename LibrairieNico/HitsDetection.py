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
import mat4py


def smooth(x,window_len=11,window='hanning'):
    """smooth the data using a window with requested size.
    
    This method is based on the convolution of a scaled window with the signal.
    The signal is prepared by introducing reflected copies of the signal 
    (with the window size) in both ends so that transient parts are minimized
    in the begining and end part of the output signal.
    
    input:
        x: the input signal 
        window_len: the dimension of the smoothing window; should be an odd integer
        window: the type of window from 'flat', 'hanning', 'hamming', 'bartlett', 'blackman'
            flat window will produce a moving average smoothing.

    output:
        the smoothed signal
        
    example:

    t=linspace(-2,2,0.1)
    x=sin(t)+randn(len(t))*0.1
    y=smooth(x)
    
    see also: 
    
    numpy.hanning, numpy.hamming, numpy.bartlett, numpy.blackman, numpy.convolve
    scipy.signal.lfilter
 
    TODO: the window parameter could be the window itself if an array instead of a string
    NOTE: length(output) != length(input), to correct this: return y[(window_len/2-1):-(window_len/2)] instead of just y.
    """

    if x.ndim != 1:
        raise Exception("smooth only accepts 1 dimension arrays.")

    if x.size < window_len:
        raise Exception("Input vector needs to be bigger than window size.")


    if window_len<3:
        return x


    if not window in ['flat', 'hanning', 'hamming', 'bartlett', 'blackman']:
        raise Exception("Window is on of 'flat', 'hanning', 'hamming', 'bartlett', 'blackman'")


    s=np.r_[x[window_len-1:0:-1],x,x[-2:-window_len-1:-1]]
    #print(len(s))
    if window == 'flat': #moving average
        w=np.ones(window_len,'d')
    else:
        w=eval('np.'+window+'(window_len)')

    y=np.convolve(w/w.sum(),s,mode='valid')
    return y


def calculateNewSize(width,height,WishForNEwWidth):
    ratio = WishForNEwWidth/width
    Nheight = int(height * ratio)
    Nwidth = int(width * ratio)    
    return Nwidth , Nheight

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