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
MARKERS = []

def cameraRead(CAMERA_FILE):

    '''Reads blender camera data export files.'''

    cameraTrack = {}

    for c, line in enumerate(CAMERA_FILE):
        if c == 0:
            #CLIP.append(line[23:])
            cameraTrack['clip'] = line[23:-1]
        elif c == 2:
            split = line[:-1].split(" ")
            #FRAME_RANGE.append((split[1], split[3]))
            cameraTrack['frame_range'] = (split[1], split[3])
        elif c == 4:
            split = line[:-1].split(" ")
            #RESOLUTION.append((split[1], split[3]))
            cameraTrack['resolution'] = (split[1], split[3])
        elif c == 6:
            split = line[:-1].split(" ")
            #SENSOR.append((split[1], split[3]))
            cameraTrack['sensor'] = (split[1], split[3])
        elif c == 8:
            split = line[:-1].split(" ")
            #LENS.append(split[1])
            cameraTrack['lens'] = split[1]
        elif c == 10:
            split = line[:-1].split(" ")
            #AOV.append((split[1], split[3]))
            cameraTrack['aov'] = (split[3], split[5])
        elif c > 12:
            split = line[:-1].split(" ")
            cameraTrack[int(split[0])] = (split[1], split[2], split[3],
                                          split[4], split[5], split[6])

    CAMERA_FILE.close()
    return cameraTrack

def trackerRead(TRACKER_FILE):

    '''Reads blender tracker data export files.'''

    trackTrack = {}

    for t, line in enumerate(TRACKER_FILE):
        if t == 0:
            #CLIP.append(line[24:-1])
            trackTrack['clip'] = line[24:-1]
        elif t == 2:
            split = line[:-1].split(" ")
            #FRAME_RANGE.append((split[1], split[3]))
            trackTrack['frame_range'] = (split[1], split[3])
        elif t == 4:
            split = line[:-1].split(" ")
            #RESOLUTION.append((split[1], split[3]))
            trackTrack['resolution'] = (split[1], split[3])
        elif t == 6:
            split = line[:-1].split(" ")
            #TRACK_NUM.append(split[1])
            trackTrack['track_num'] = split[1]
        elif t > 8:
            split = line[:-1].split(" ")
            if split[0] == "#####":
                currentMarker = split[1]
                trackTrack[currentMarker] = {}
                if currentMarker not in MARKERS:
                    MARKERS.append(currentMarker)
            else:
                try:
                    trackTrack[currentMarker][int(split[0])] = (split[1], split[2])
                except IndexError:
                    pass

    TRACKER_FILE.close()
    return trackTrack

# read in files
A_CAM = cameraRead(C1_CAM)
B_CAM = cameraRead(C2_CAM)
A_TRACK = trackerRead(C1_TRACK)
B_TRACK = trackerRead(C2_TRACK)

def angleOfViewCalc(cam, aov, trackPos):

    '''Calculates the angle of view distortion on the projected
    track and adds that to the camera rotation.  Returns tuple.'''

    trackAOV = []
    finalRotation = []

    # for o in range(0, 2): # ORIGINAL Y-UP
    #     trackAOV.append((float(trackPos[o]) - 0.5) * float(aov[o]))
    #     finalRotation.append(float(trackAOV[o]) + float(cam[o]))

    # finalRotation.append(float(cam[2]))

    # Revised Z-Up Implementation
    trackAOV.append((float(trackPos[0]) - 0.5) * float(aov[0])) # x
    finalRotation.append(float(trackAOV[0]) + float(cam[0])) # x
    finalRotation.append(float(cam[1])) # y
    trackAOV.append((float(trackPos[1]) - 0.5) * float(aov[1])) # z
    finalRotation.append(float(trackAOV[1]) + float(cam[2])) # z

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
    trackPosition = track[marker][int(frame)]

    # account for marker based angle modifers
    rotation = angleOfViewCalc(cameraRotation, cameraAOV, trackPosition)

    # calculate arbitary second point on projected line
    newPoint = []
    for n in range(0, 3):
        newPoint.append(math.cos(rotation[n]) * 10 + float(originPoint[n]))

    return (np.array([originPoint[0], originPoint[1], originPoint[2]]),
            np.array([newPoint[0], newPoint[1], newPoint[2]]))

def closestDistanceBetweenLines(a0, a1, b0, b1):

    '''Given two lines defined by numpy.array pairs (a0,a1,b0,b1)
    Return the closest points on each segment and their distance'''

    # Modified from code written by Eric Vignola(Fnord):
    # https://stackoverflow.com/a/18994296

    # Calculate denomitator
    A = a1 - a0
    B = b1 - b0
    magA = np.linalg.norm(A)
    magB = np.linalg.norm(B)

    _A = A / magA
    _B = B / magB

    cross = np.cross(_A, _B)
    denom = np.linalg.norm(cross)**2

    # If lines are parallel (denom=0) test if lines overlap.
    # If they don't overlap then there is a closest point solution.
    # If they do overlap, there are infinite closest positions, but there is a closest distance
    if not denom:
        d0 = np.dot(_A, (b0-a0))

        # Segments overlap, return distance between parallel segments
        return None, None, np.linalg.norm(((d0*_A)+a0)-b0)

    # Lines criss-cross: Calculate the projected closest points
    t = (b0 - a0)
    detA = np.linalg.det([t, _B, cross])
    detB = np.linalg.det([t, _A, cross])

    t0 = detA/denom
    t1 = detB/denom

    pA = a0 + (_A * t0) # Projected closest point on segment A
    pB = b0 + (_B * t1) # Projected closest point on segment B

    return pA, pB, np.linalg.norm(pA-pB)

# confirm range is solvable
MIN_CAM = max(int(A_CAM['frame_range'][0]), int(B_CAM['frame_range'][0]))
MAX_CAM = min(int(A_CAM['frame_range'][1]), int(B_CAM['frame_range'][1]))
MIN_TRACK = max(int(A_TRACK['frame_range'][0]), int(B_TRACK['frame_range'][0]))
MAX_TRACK = min(int(A_TRACK['frame_range'][1]), int(B_TRACK['frame_range'][1]))

TRACK_RANGE = (max(MIN_CAM, MIN_TRACK), min(MAX_CAM, MAX_TRACK))

if TRACK_RANGE[1] < TRACK_RANGE[0]:
    raise Exception("No overlapping frames for solve!")

def lineCross(marker, frame, camA, camB, trackA, trackB):

    '''Finds the closest point of 2 projected lines.
    Returns a triple.'''

    # define lines
    lineA = pointsOnLine(camA, trackA, frame, marker)
    lineB = pointsOnLine(camB, trackB, frame, marker)

    # calculate intersect
    intersect = closestDistanceBetweenLines(lineA[0].astype('float64'),
                                            lineA[1].astype('float64'),
                                            lineB[0].astype('float64'),
                                            lineB[1].astype('float64'))

    # define intersecting points and line
    pointA = intersect[0].tolist()
    pointB = intersect[1].tolist()
    lineDistance = intersect[2]

    # calculate midpoint
    midpoint = []
    for q in range(0, 3):
        midpoint.append((pointA[q] + pointB[q]) / 2)
    midpoint.append(lineDistance)
    return midpoint # (x, y, z, distance)

# calculate midpoint for all markers
EXPORT = {}
for mark in MARKERS:
    EXPORT[mark] = {}
    for w in range(int(TRACK_RANGE[0]), int(TRACK_RANGE[1]) + 1):
        if w in A_TRACK[mark] and w in B_TRACK[mark]: # check tracking data exists for given frame
            EXPORT[mark][w] = lineCross(mark, w, A_CAM, B_CAM, A_TRACK, B_TRACK)

# export coordinate data
exportPath = filedialog.asksaveasfilename(initialfile="mocapSolved.txt")
with open(exportPath, "x") as dataFile:
    dataFile.write("SOLVED DATA EXPORT for {} and {} \n\n".format(A_CAM['clip'], B_CAM['clip']))
    dataFile.write("RANGE {} to {}\n\n".format(TRACK_RANGE[0], TRACK_RANGE[1]))
    # loop through nested dictionaries for file export
    for solve in EXPORT:
        dataFile.write("\n##### {}\n".format(solve))
        for keyframe in EXPORT[solve]:
            dataFile.write("{:05d} {:8f} {:8f} {:8f}\n".format(keyframe,
                                                               EXPORT[solve][keyframe][0],
                                                               EXPORT[solve][keyframe][1],
                                                               EXPORT[solve][keyframe][2]))
