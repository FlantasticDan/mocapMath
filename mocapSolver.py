#!/usr/bin/env python3

# solves 3d motion capture points from exported camera and tracker data

import math
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
            #CLIP.append(line[23:])
            cameraTrack['clip'] = line[23:-1]
        elif i == 2:
            split = line[:-1].split(" ")
            #FRAME_RANGE.append((split[1], split[3]))
            cameraTrack['frame_range'] = (split[1], split[3])
        elif i == 4:
            split = line[:-1].split(" ")
            #RESOLUTION.append((split[1], split[3]))
            cameraTrack['resolution'] = (split[1], split[3])
        elif i == 6:
            split = line[:-1].split(" ")
            #SENSOR.append((split[1], split[3]))
            cameraTrack['sensor'] = (split[1], split[3])
        elif i == 8:
            split = line[:-1].split(" ")
            #LENS.append(split[1])
            cameraTrack['lens'] = split[1]
        elif i == 10:
            split = line[:-1].split(" ")
            #AOV.append((split[1], split[3]))
            cameraTrack['aov'] = (split[1], split[3])
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
            #CLIP.append(line[24:-1])
            trackTrack['clip'] = line[24:-1]
        elif i == 2:
            split = line[:-1].split(" ")
            #FRAME_RANGE.append((split[1], split[3]))
            trackTrack['frame_range'] = (split[1], split[3])
        elif i == 4:
            split = line[:-1].split(" ")
            #RESOLUTION.append((split[1], split[3]))
            trackTrack['resolution'] = (split[1], split[3])
        elif i == 6:
            split = line[:-1].split(" ")
            #TRACK_NUM.append(split[1])
            trackTrack['track_num'] = split[1]
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

def angleOfViewCalc(cam, aov, track):

    '''Calculates the angle of view distortion on the projected
    track and adds that to the camera rotation.  Returns tuple.'''

    trackAOV = []
    finalRotation = []

    for i in range(0, 1):
        trackAOV[i] = ((track[i] - 0.5) * aov[i])
        finalRotation[i] = trackAOV[i] + cam[i]

    finalRotation[2] = cam[2]

    return finalRotation


def pointsOnLine(cameraTransform, track, frame, marker):

    '''Calculates 2 points on the line drawn between the camera origin and the
    projected point on the track projection.  Returns as 2 numpy arrays.'''

    # extract camera variables
    originPoint = (cameraTransform[frame][0], cameraTransform[frame][1], cameraTransform[frame][2])
    cameraRotation = (cameraTransform[frame][3], cameraTransform[frame][4],
                      cameraTransform[frame][5])
    cameraAOV = (cameraTransform['aov'][0], cameraTransform['aov'][1])

    # extract tracker variables
    for x in track[marker]:
        if x[0] == frame:
            trackPosition = (x[1], x[2])

    # account for marker based angle modifers
    rotation = angleOfViewCalc(cameraRotation, cameraAOV, trackPosition)

    # calculate arbitary second point on projected line
    newPoint = []
    for i in range(0, 2):
        newPoint[i] = math.cos(rotation[i]) * 10 + originPoint[i]

    return (np.array([originPoint[0], originPoint[1], originPoint[2]]),
            np.array([newPoint[0], newPoint[1], newPoint[2]]))
