"""Tools for tracking markers across frames."""

import os
import numpy as np
import cv2
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
    total = len(imgSequence) - 1
    start = 0
    end = interval

    # Create empty marker dictionary full of empty dictionaries to store output.
    tracks = detect.createEmptyMarkerDictionary({})

    # Loop over each Chunck
    while end <= total:
        if end > total:
            end = total # Catch last chunck to prevent an index error.
        detection = detect.markerID(imgSequence[start])
        for color in detect.COLOR_ID:
            for pattern in detect.PATTERN_ID:
                marked = detection[color][pattern] # Detect markers for first frame of the chunck.
                if marked is None:
                    continue
                trackedBoxes = fixedUpdateTracker(imgSequence[start:end], marked[1])
                for i, box in enumerate(trackedBoxes):
                    center = findCenterOfBounding(box)
                    tracks[color][pattern][i + start] = center
        start = end
        end += interval
    return tracks

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
            break
        boxes.append(boundingBox)
        iteration += 1

    return boxes

def findCenterOfBounding(bbox):
    """Given a bounding box, return the centeroid."""
    return (bbox[0] + (bbox[2] / 2), bbox[1] - (bbox[3] / 2))

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
# print(fixedUpdateTracking(images))
