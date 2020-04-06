# -*- coding: utf-8 -*-
"""
Created on Wed Dec 11 12:51:22 2019

@author: master
"""
from multiprocessing import Process, Queue

import matplotlib.pyplot as plt
import numpy as np
import cv2
import os
import win32net

def readfiles(q,root_folder,Subfolder):
    
    root_folder="//157.136.60.11/EqShulz/Timothe"
    print(root_folder)
    use_dict = {}
    use_dict['remote'] = root_folder
    use_dict['password'] = "0bal-seiglE"
    use_dict['username'] = "Daniel"
    print(use_dict)
    try:
        win32net.NetUseAdd(None, 1, use_dict)
        print("Network connection established")
    except Exception as e:
        print(e)
        print("Network connection failed")
        
    for root, dirnames, filenames in os.walk(root_folder):
        for filename in filenames:
            datafile = os.path.join(root, filename)
            q.put(datafile + "\n")
            basename = os.path.basename(os.path.dirname(datafile))
            q.put(basename + "\n")
            q.put(filename + "\n")
            q.put("\n")
#            for line in datafile:
#                q.put(line)
    q.close()
    
if __name__ == '__main__' :
    root_folder =  "//157.136.60.11/EqShulz/Timothe"
#    readfiles(1)
    q = Queue()
    p = Process(target = readfiles, args = (q,))
    p.start()
    Str = ""
    while p.is_alive() or not q.empty():
        for li in q.get():
            if li == "\n":
                print(Str)
                Str = ""
            else :
                Str =  Str + li