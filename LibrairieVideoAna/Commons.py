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
            