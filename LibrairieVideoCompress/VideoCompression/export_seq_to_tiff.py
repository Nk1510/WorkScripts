#!/usr/bin/env python
# -*- coding: latin-1 -*-

import struct
import csv
import mmap
import datetime
import array
import logging
import os
import csv
import glob
import time

import configparser
import numpy as np
import cv2
#from cv2 import cv

def export_seq_to_tiff(seq_path, tiff_path):
    """
        Lecture du fichier binaire de séquence sqb
        Les données sont représentées par la structure en C suivante :
            typedef struct
            {   
                long offset;        // 4 bits -> + 4 bits vides car mémoire alignée
                double TimeStamp;   // 8 bits
                int binfile;        // 4 bits -> + 4 bits vides car mémoire alignée
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
    
    with open(sqb_path,'rb') as f :
        for i in range(0, int(num_images)):
            offset = struct.unpack('l', f.read(4))
            padding = f.read(4)
            timestamp = struct.unpack('d', f.read(8))
            binfile = struct.unpack('i', f.read(4))
            padding = f.read(4)
            
            print(offset)
            
            bin_path = "%s\\%s%0.5d.bin" % (pathstr, bin_file, binfile[0])
            tiff_file_path =  "%s_%0.5d.tif" %(tiff_path, i)
            
            f_bin = open(bin_path, 'rb')
            f_bin.seek(offset[0], os.SEEK_SET)
            
            bytes = f_bin.read(height*width*bpp)
            
            if bpp == 2:
                buffer = np.frombuffer(bytes, dtype=np.uint16)
            else:
                buffer = np.frombuffer(bytes, dtype=np.uint8)
            
            nparr2 = buffer.reshape(height, width)
            cv2.imwrite(tiff_file_path, nparr2)
            f_bin.close()


if __name__ == '__main__':
    _read_sqb_convert_to_tiff("G:\\2018-03-07T17.07.58\\seq_cam1_Slave_Image container.seq", "G:\\2018-03-07T17.07.58\\test2_tiff")


    