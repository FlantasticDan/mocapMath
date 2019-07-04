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

# define headers
CLIP = []
FRAME_RANGE = []
RESOLUTION = []
SENSOR = []
LENS = []
AOV = []
TRACK_NUM = []

def cameraRead(CAMERA_FILE):

    '''Reads blender camera data export files.'''

    cameraTrack = {}

    for i, line in enumerate(CAMERA_FILE):
        if i == 0:
            CLIP.append(line[23:])
        elif i == 2:
            split = line[:-1].split(" ")
            FRAME_RANGE.append((split[1], split[3]))
        elif i == 4:
            split = line[:-1].split(" ")
            RESOLUTION.append((split[1], split[3]))
        elif i == 6:
            split = line[:-1].split(" ")
            SENSOR.append((split[1], split[3]))
        elif i == 8:
            split = line[:-1].split(" ")
            LENS.append(split[1])
        elif i == 10:
            split = line[:-1].split(" ")
            AOV.append((split[1], split[3]))
        elif i > 12:
            split = line[:-1].split(" ")
            cameraTrack[int(split[0])] = (split[1], split[2], split[3],
                                          split[4], split[5], split[6])

    CAMERA_FILE.close()
    return cameraTrack

def trackerRead(TRACKER_FILE):

    '''Reads blender tracker data export files.'''

    trackTrack = {}

    for i, line in enumerate(TRACKER_FILE):
        if i == 0:
            CLIP.append(line[24:-1])
        elif i == 2:
            split = line[:-1].split(" ")
            FRAME_RANGE.append((split[1], split[3]))
        elif i == 4:
            split = line[:-1].split(" ")
            RESOLUTION.append((split[1], split[3]))
        elif i == 6:
            split = line[:-1].split(" ")
            TRACK_NUM.append(split[1])
        elif i > 8:
            split = line[:-1].split(" ")
            if split[0] == "#####":
                currentMarker = split[1]
                trackTrack[currentMarker] = []
            else:
                try:
                    trackTrack[currentMarker].append((int(split[0]), split[1], split[2]))
                except ValueError:
                    pass

    TRACKER_FILE.close()
    return trackTrack

A_CAM = cameraRead(C1_CAM)
B_CAM = cameraRead(C2_CAM)
A_TRACK = trackerRead(C1_TRACK)
B_TRACK = trackerRead(C2_TRACK)
