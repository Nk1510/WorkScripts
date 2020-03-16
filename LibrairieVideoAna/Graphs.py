# -*- coding: utf-8 -*-
"""
Created on Sat Feb 29 21:37:37 2020

@author: Timothe
"""

import matplotlib.pyplot as plt
import matplotlib.patches as pat
import argparse
import cv2

class collect_points() :
   omega = []
   def __init__(self,array):
       self.array = array
   def onclick(self,event):
       self.omega.append((int(round(event.ydata)),   int(round(event.xdata))))

   def indices(self):
       plot = plt.imshow(self.array, cmap = plt.cm.hot, interpolation =  'nearest', origin= 'upper')
       fig = plt.gcf()
       ax = plt.gca()
       zeta = fig.canvas.mpl_connect('button_press_event', self.onclick)
       plt.colorbar()
       plt.show()
       return self.omega
    
    
class LineBuilder:
    def __init__(self, line):
        self.line = line
        self.xs = list(line.get_xdata())
        self.ys = list(line.get_ydata())
        self.cid = line.figure.canvas.mpl_connect('button_press_event', self)

    def __call__(self, event):
        print('click', event)
        if event.inaxes!=self.line.axes: return
        self.xs.append(event.xdata)
        self.ys.append(event.ydata)
        self.line.set_data(self.xs, self.ys)
        self.line.figure.canvas.draw()


def click_and_crop(event, x, y, flags, param):
    
    
    # initialize the list of reference points and boolean indicating
    # whether cropping is being performed or not
    refPt = []
    image = []
    cropping = False
    
	# grab references to the global variables
	global refPt, cropping
	# if the left mouse button was clicked, record the starting
	# (x, y) coordinates and indicate that cropping is being
	# performed
    
	if event == cv2.EVENT_LBUTTONDOWN:
		refPt = [(x, y)]
		cropping = True
	# check to see if the left mouse button was released
	elif event == cv2.EVENT_LBUTTONUP:
		# record the ending (x, y) coordinates and indicate that
		# the cropping operation is finished
		refPt.append((x, y))
		cropping = False
		# draw a rectangle around the region of interest
		cv2.rectangle(image, refPt[0], refPt[1], (0, 255, 0), 2)
		cv2.imshow("image", image)

    plt.show()
    
    
if __name__ == "__main__" :
    import numpy as np
    plt.ion()
    # %matplotlib qt
    # in ipython console
    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.set_title('click to build line segments')
    array = np.random.rand(10,10)*255   
    #indices = collect_points(array)
    
    plot = ax.imshow(array, cmap = plt.cm.hot, interpolation =  'nearest', origin= 'upper')
    
    
    rect = pat.Rectangle((50,100),40,30,linewidth=1,edgecolor='r',facecolor='none')
    
    ax.add_patch(rect)
    # print(indices.indices())
    #line, = ax.plot([0], [0])  # empty line
    #linebuilder = LineBuilder(array)

    
    
    
    
    
    