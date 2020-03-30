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

from scipy.optimize import curve_fit
from scipy.interpolate import interp1d
from scipy.io import loadmat
from scipy import signal as sig
import pandas as pd
import numpy as np

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

def Easyinterp(Input):
    
    if ~ len(np.shape(Input)) == 1:
        Input = np.flatten(Input)
    
    X = np.arange(0,np.size(Input),1)
    Xinterp = np.arange(0,np.size(Input),0.1)
    f2 = interp1d(X, abs(Input), kind='slinear', fill_value="extrapolate")
    raw_interp = f2(Xinterp)
    
    output = np.reshape(raw_interp, (1, np.size(raw_interp)) )
    
    return output

def diff(Input1):
    X = np.diff(abs(Input1), n=1)
    return X

def calculateNewSize(width,height,WishForNEwWidth):
    ratio = WishForNEwWidth/width
    Nheight = int(height * ratio)
    Nwidth = int(width * ratio)    
    return Nwidth , Nheight


def HighestPeakFrom(peaks,values):
    if len(peaks) > 0 :
        values = values.get('peak_heights')
        peak = peaks[np.argmax(values)]
        value = values[np.argmax(values)]
        return peak, value 
    else:
        return np.nan, np.nan
    
def sigmoid(x, L ,x0, k, b):
    y = L / (1 + np.exp(-k*(x-x0)))+b
    return (y)
    
def getSigmoidEdgePeak(Y_data,**kwargs):
    
    Y_data = Y_data.flatten()
    
    if 'lowpass_raw' in kwargs :
        lowpass = kwargs.get('lowpass_raw')
        Y_data = sig.filtfilt(lowpass[0], lowpass[1], Y_data)            
    
    X_data = np.arange(0,np.shape(Y_data)[0],1)
    
    p0 = [max(Y_data), np.median(X_data), 1, min(Y_data)]
    
    popt, pcov = curve_fit(sigmoid, X_data, Y_data, p0 , method='dogbox')
    
    if 'interp' in kwargs :
        interp_multplicator = kwargs.get('interp')
    else :
        interp_multplicator = False
        
    if interp_multplicator :
        X_data = np.arange(0,np.shape(Y_data)[0],1/interp_multplicator)
    
    FittedSlice = sigmoid(X_data, *popt)
    
    if 'lowpass_diff' in kwargs :
        lowpass = kwargs.get('lowpass_diff')
        DerivedSlice = sig.filtfilt(lowpass[0], lowpass[1], np.diff(FittedSlice))
    else :
        DerivedSlice = np.diff(FittedSlice)
        
    return np.reshape(DerivedSlice, (1, np.size(DerivedSlice))) , np.reshape(FittedSlice, (1, np.size(FittedSlice)))