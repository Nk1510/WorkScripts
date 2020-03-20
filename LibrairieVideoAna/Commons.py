# -*- coding: utf-8 -*-
"""
Created on Tue Mar  3 08:59:19 2020

@author: Timothe
"""


import re
import numpy as np

def QuickRegexp(Line,regex,**kwargs):
    
    """Line : input string to be processed
    regex : input regex, can be easily designed at : https://regex101.com/
    kwargs :
    case = False / True : case sensitive regexp matching (defaul false)
    """
    
    if 'case' in kwargs:
        case = kwargs.get("case")
    else :
        case = False
        
    if case :
        matches = re.finditer(regex, Line, re.MULTILINE|re.IGNORECASE)
    else :
        matches = re.finditer(regex, Line, re.MULTILINE)
        
    for matchnum, match in enumerate(matches,  start = 1):
        MATCH = match.group()
        return(MATCH)
    return False

def ProgressBarImage(Fraction):
    
    if Fraction == 1:
        blue = np.zeros((10,100,3))
        blue[:,:,2] = np.ones((10,100))
        return(blue)
    elif Fraction == 0:
        blue = np.zeros((10,100,3))
        return(blue)
    else:
        blue = np.zeros((10,100,3))
        blue[:,:,2] = np.ones((10,100))
        blue[:,int(Fraction*100):,:] = np.ones((10,100-int(Fraction*100),3))
        return(blue)
    
    
def AlphaNum_Sort(List):
    convert = lambda text: int(text) if text.isdigit() else text
    alphanum_key = lambda key: [convert(c) for c in re.split('([0-9]+)',key)]
    return sorted(List, key = alphanum_key)

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

            