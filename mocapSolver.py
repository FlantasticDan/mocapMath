#!/usr/bin/env python3

# solves 3d motion capture points from exported camera and tracker data

import tkinter as tk
from tkinter import filedialog
import numpy as np

# configure UI to hide default window
root = tk.Tk()
root.withdraw()

# prompt for data exports
C1_CAM = open(filedialog.askopenfilename(title="Camera 1 | CAMERA DATA"))
C1_TRACK = open(filedialog.askopenfilename(title="Camera 1 | TRACKER DATA"))
C2_CAM = open(filedialog.askopenfilename(title="Camera 2 | CAMERA DATA"))
C2_TRACK = open(filedialog.askopenfilename(title="Camera 2 | TRACKER DATA"))

DATA_FILES = [C1_CAM, C1_TRACK, C2_CAM, C2_TRACK]

# define headers
CLIP = []
FRAME_RANGE = []
RESOLUTION = []
SENSOR = []
LENS = []
AoV = []

def cameraRead(CAMERA_FILE):

    '''Reads blender camera data export files.'''

    cameraTrack = {}

    for i, line in enumerate(CAMERA_FILE):
        if i == 0:
            CLIP.append(line[23:])
        elif i == 2:
            split = line.split(" ")
            FRAME_RANGE.append((split[1], split[3]))
        elif i == 4:
            split = line.split(" ")
            RESOLUTION.append((split[1], split[3]))
        elif i == 6:
            split = line.split(" ")
            SENSOR.append((split[1], split[3]))
        elif i == 8:
            split = line.split(" ")
            LENS.append(split[1])
        elif i == 10:
            split = line.split(" ")
            AoV.append((split[1], split[3]))
        elif i > 12:
            split = line.split(" ")
            cameraTrack[int(split[0])] = (split[1], split[2], split[3], split[4], split[5], split[6])

    return cameraTrack
