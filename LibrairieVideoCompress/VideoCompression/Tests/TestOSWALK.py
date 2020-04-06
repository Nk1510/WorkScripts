# -*- coding: utf-8 -*-
"""
Created on Tue Jan 28 21:12:58 2020

@author: ADMIN
"""


import os
import tkinter as tk
from tkinter import filedialog
import re

root = tk.Tk()
root.withdraw()
initialdirs = r"F:/Sophie"
file_path = filedialog.askdirectory(parent=root,initialdir=initialdirs,title='Please select a directory containing mouses')
print(file_path)
regex1 = (r"^[Ss]ouris\d+$")


for root, dirs, files in os.walk(file_path):
#    print(root,dirs,files)
#    print()
#    print()
    for subdir in dirs :
        matches = re.finditer(regex1, subdir, re.MULTILINE)
        Mouseno = False
        for matchnum, match in enumerate(matches,  start = 1):
            Mouseno = match.group()
            print(Mouseno)
        if not Mouseno:
            continue
        print(os.path.join(root,subdir),initialdirs,root)
        commonprefix = os.path.commonprefix((initialdirs,root))
        print(commonprefix)
        print(os.path.relpath(root,commonprefix))
        print(os.path.commonpath((root,initialdirs)))
        print()
    
    




