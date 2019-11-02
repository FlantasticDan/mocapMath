"""Tools for tracking markers across frames."""

import os
import numpy as np
import cv2
from shapely.geometry.point import Point
from shapely.geometry import LineString
import markerDetection as detect

def fixedUpdateTracking(imgSequence, interval=24):
    """
    Tracks markers across an image sequence with no tracker
    recovery but forces alignment at a fixed interval.

    Args:
        imgSequence: Array of openCV numpy arrays.
        interval (int): Number of frames between tracker initialization.

    Returns:
        Dictionary of Marker IDs corresponding to array of centroids.
    """
    img = 0
    sinceInterval = 0
    currentImg = imgSequence[img]
    detection = detect.markerID(currentImg)

    for color in detect.COLOR_ID:
        for pattern in detect.PATTERN_ID:
            marked = detection[color][pattern]
            if marked is None:
                continue
            trackedBoxes = fixedUpdateTracker(imgSequence[img:img+interval], marked[1])
            for box in trackedBoxes:
                print(box)

def fixedUpdateTracker(imgSequence, corners):
    """Tracks markers across an image sequence for the Fixed Updated Method."""
    boundingBox = cv2.boundingRect(np.array(corners))
    boxes = []
    boxes.append(boundingBox)

    tracker = cv2.TrackerCSRT_create()
    tracker.init(imgSequence[0], boundingBox)

    iteration = 1
    while iteration < len(imgSequence):
        success, boundingBox = tracker.update(imgSequence[iteration])
        if success is False:
            print('Tracker Lost')
            break
        boxes.append(boundingBox)
        iteration += 1
    
    return boxes

def directoryToImgSequence(directoryPath):
    """From a directory, returns a list of openCV image objects."""
    imgSequence = []
    for image in os.listdir(directoryPath):
        imgPath = os.path.join(directoryPath, image)
        img = cv2.imread(imgPath)
        imgSequence.append(img)
    return imgSequence


# ## DEBUG CODE ##
# import tkinter as tk
# from tkinter import filedialog

# root = tk.Tk()
# root.withdraw()

# dirPath = filedialog.askdirectory(title='Select a Directory Containing an Image Sequence')
# images = directoryToImgSequence(dirPath)
# fixedUpdateTracking(images)
