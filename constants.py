# import pygame 
import os 
import cv2 
import argparse
from os.path import join as jn
from collections import namedtuple

import random
import json 

import sys
import cv2
import numpy as np
from PyQt5.QtCore import Qt, QPoint, QTimer
from PyQt5.QtGui import QImage, QPixmap, QKeySequence
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QApplication, QLabel, QMainWindow, QPushButton,QColorDialog,QMessageBox,QShortcut
import uuid

from datetime import datetime


# Determine the width and height ratio of the camera
from picamera2 import Picamera2
import time
########################### ARGPARSE arguments ###################################
# parser = argparse.ArgumentParser(description='Multistack with the picamera and raspberry pi')
# args = parser.parse_args()

##################################################################################
# pygame.init()
# display_info = pygame.display.Info()
# define the dimensions of the screen
# W = int(display_info.current_w*args.res)
# H = int(W*cameraRatio)
# W = 1920
# H = 1080




cap = Picamera2() 
cap.preview_configuration.main.size = (980, 740)
cap.preview_configuration.main.format = "RGB888"
cap.preview_configuration.align() 
cap.configure("preview")
cap.start() 


# DD LATERAL_PADDING_MENU
# LATERAL_PADDING = (int,int)
# interp. how many pixels to leave as padding to accomodate the lateral panel of the application
# Define the named tuple with fields 'x' and 'y'
Coordinate = namedtuple('Coordinate', ['x', 'y'])
LATERAL_PADDING = Coordinate(400,0)
TOP_PADDING = Coordinate(0,80)

# DD. SAVEPATH 
# savePath = str
# interp. the location of the file that will store the program's output
savePath = jn(os.path.dirname(__file__),"output.txt")

# DD. BRUSH_SETTINGS
# brush_settings = {"color":(int, int, int)}
# interp. a set of parameters represented as a mutable object to be used globally within different submodules of the program
brush_settings = {"color":(0, 255, 0), "size":20,"resize_sensitivity":5, "is_brush_mode":"brush"}

# DD. DISPLAY_SETTINGS
# display_settings = {"image":np.array, "mask":np.array}
# interp. a set of numpy arrays representing images and masks for the program
display_settings = {"image":None, "mask":None}

cursor_settings = {"in_display":False}

os_settings = {"project_folder":"", "current_folder":"", "current_prefix":"", "format":"png"}

# DD. SCALE_SETTINGS
# scale_settings = {"calibration":dict|None, "color":(int,int,int)}
# interp. global scale bar state. "calibration" holds the loaded calibration dict
# {"name":str, "pixels":float, "distance":float, "unit":str} measured on the 980x740 preview;
# "color" is the bar color as an RGB tuple
scale_settings = {"calibration":None, "color":(255, 255, 255)}

# DD. CALIBRATIONS_DIR
# calibrations_dir = str
# interp. folder where scale bar calibrations are stored as <name>.json files
CALIBRATIONS_DIR = jn(os.path.dirname(os.path.abspath(__file__)), "calibrations")
os.makedirs(CALIBRATIONS_DIR, exist_ok=True)

# DD. CAMERA_SETTINGS
# camera_settings = {"brightness":float, "contrast":float, "saturation":float,
#                    "awb":str, "gain_red":float, "gain_blue":float}
# interp. image tuning parameters applied to the camera through picamera2 controls.
# brightness in [-1.0, 1.0]; contrast and saturation in [0.0, 2.0]; awb is one of
# AWB_MODES or "manual", in which case gain_red/gain_blue are used as ColourGains;
# flip_h/flip_v mirror the preview and the saved photos horizontally/vertically
camera_settings = {"brightness":0.0, "contrast":1.0, "saturation":1.0,
                   "awb":"auto", "gain_red":1.0, "gain_blue":1.0,
                   "flip_h":False, "flip_v":False}

# DD. AWB_MODES
# interp. mapping from white balance preset name to its libcamera AwbMode value
AWB_MODES = {"auto":0, "tungsten":1, "fluorescent":2, "indoor":3, "daylight":4, "cloudy":5}

# DD. PRESETS_FILE
# interp. JSON file storing named camera settings presets
# {"preset_name": {"brightness":float, "contrast":float, ...}}
PRESETS_FILE = jn(os.path.dirname(os.path.abspath(__file__)), "camera_presets.json")

# DD. UNIT_TO_MM
# interp. conversion factor from each supported scale bar unit to millimeters
UNIT_TO_MM = {"mm": 1.0, "µm": 0.001, "cm": 10.0}

# DD. NOMENCLATURE_FILE
# interp. user-editable file listing the allowed 3-letter structure codes and
# single-letter orthographic views used to validate the structured prefix fields
NOMENCLATURE_FILE = jn(os.path.dirname(os.path.abspath(__file__)), "nomenclature.txt")
DEFAULT_NOMENCLATURE = """# Nomenclature for structured image prefixes.
# Edit this file while the application is CLOSED, then restart it to apply changes.
# Lines starting with '#' are comments. Format: key=value1,value2,value3

# 3-letter codes for anatomical structures / body parts
structures=pro,opi,che,ped,leg,spi,epi

# Single-letter orthographic views:
# d=dorsal, v=ventral, l=lateral, a=anterior, p=posterior/prolateral, r=retrolateral
views=d,v,l,a,p,r
"""

# DD. PREVIEW_SIZE
# interp. resolution of the preview frame shown in the display label, used to scale
# scale bar measurements up to the full sensor resolution at capture time
PREVIEW_WIDTH = 980
PREVIEW_HEIGHT = 740