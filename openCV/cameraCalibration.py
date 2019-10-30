"""Tools for calibrating cameras from an image set of a calibration pattern."""

import os
import sys
import tkinter as tk
from tkinter import filedialog
import cv2
import numpy as np

# Configure Tkinter
root = tk.Tk()
root.withdraw()

# File Management
def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

def makeChessboard(col, row):
    """
    Creates a idealized coordinate array of a chessboard.

    Args:
        col (int): number of interior columns on the chessboard
        row (int): number of interior rows on the chessboard

    Returns:
        Raw 2D (z=0) chessboard coordinate array.
    """
    x = 0
    y = 0
    chessboard = []

    while y < row:
        while x < col:
            chessboard.append((x, y, 0))
            x = x + 1
        y = y + 1
        x = 0

    return chessboard

def sensorOptimizer(horizontal, vertical, imageSize):
    """
    Checks and adjusts a source image sensor size for compatiabilty with given image dimensions.

    Args:
        horizontal (float): sensor width in mm
        vertical (float): sensor height in mm
        imageSize (x,y): dimensions of given images in px

    Returns:
        (sensorWidth, sensorHeight)
    """

    sensor = (horizontal, vertical)
    if imageSize[0] / imageSize[1] != sensor[0] / sensor[1]:
        newSensor = (sensor[0], (imageSize[1] * sensor[0]) / imageSize[0])
        if newSensor[1] > sensor[1]:
            newSensor = ((sensor[1] * imageSize[0]) / imageSize[1], sensor[1])
            return newSensor
    return sensor

def detectCorners(imgPath, pattern):
    """
    Find all chessboard corners in an image.

    Args:
        imgPath: OpenCV compatiable image file path
        pattern (cols, rows): Size of the interior chessboard grid.

    Returns:
        Array of coordinates of chessboard corners in image space.
    """
    img = cv2.imread(imgPath)
    found, intersects = cv2.findChessboardCorners(img, pattern)

    if found is True:
        corners = []
        for group in intersects:
            for intersect in group:
                corners.append((intersect[0], intersect[1]))
        return corners
    
    return None

def createCalibrationArrays(board, combinedCorners):
    """
    Creates arrays from the chessboard and detected corners for solving camera properties.

    Args:
        board: 2D Chessboard Coordinate Array
        combinedCorners: Array of arrays of coordinates of detected chessboard corners

    Returns:
        imagePoints: Combined NumPy array of coordinates of detected chessboard corners
        objectPoints: Correlating 2D Chessboard Coordinate NumPy Array
    """

    imagePoints = []
    objectPoints = []

    for result in combinedCorners:
        if result is not None:
            imagePoints.append(result)
            objectPoints.append(board)

    imagePoints = np.array(imagePoints, dtype='float32')
    objectPoints = np.array(objectPoints, dtype='float32')

    return imagePoints, objectPoints

def getImageSize(imgPath):
    """Returns the dimensions of an image."""
    img = cv2.imread(imgPath)
    size = img.shape
    return (size[1], size[0])

def cameraCalibration(imgDirectory, sensorWidth, sensorHeight, patternColumns, patternRows):
    """
    Calculates necessary camera calibration metrics from an image set of a calibration chessboard.

    Args:
        imgDirectory: Path to a directory containing the image set.
        sensorWidth: Width of the Image Sensor in mm.
        sensorHeight: Height of the Image Sensor in mm.
        patternColums: Number of interior columns on calibration pattern.
        patternRows: Number of interior rows on calibration pattern.

    Returns:
        matrix: Camera Matrix
        distortion: Distortion Coefficents
        fov: (horizontal, vertical) field of view in degrees
    """
    # Initialize Variables
    detectedCorners = []
    patternSize = (patternColumns, patternRows)
    imageSize = None

    # Create Board Template
    board = makeChessboard(patternColumns, patternRows)

    # Detect Corners in each Image
    for image in os.listdir(imgDirectory):
        imgPath = os.path.join(imgDirectory, image)
        if imageSize is None:
            imageSize = getImageSize(imgPath)
        detectedCorners.append(detectCorners(imgPath, patternSize))

    # Confirm Sensor Size
    sensor = sensorOptimizer(sensorWidth, sensorHeight, imageSize)

    # Prepare Arrays for openCV Calculations
    imagePoints, objectPoints = createCalibrationArrays(board, detectedCorners)

    # Camera Matrix Calculations
    initialMatrix = cv2.initCameraMatrix2D(objectPoints, imagePoints, imageSize)
    error, matrix, distortion, rot, trans = cv2.calibrateCamera(objectPoints, imagePoints,
                                                                imageSize, initialMatrix, None)

    # FOV Calculation
    fovH, fovV, focal, principal, ratio = cv2.calibrationMatrixValues(matrix, imageSize,
                                                                      sensor[0], sensor[1])

    return matrix, distortion, (fovH, fovV)

def exportCalibration(export, matrix, distortion, fov):
    '''
    Save camera calibration for later reuse.

    Args:
        exportPath: File path to save export in.
        matrix: Camera Matrix
        distortion: Distortion Coefficents
        fov: (horizontal, vertical) field of view in degrees 

    Returns:
        File path to saved file.
    '''
    np.savez(export, matrix=matrix, distortion=distortion, fov=fov)

    return export

def importCalibration(filePath):
    """
    Imports camera calibration data.

    Args:
        filePath: Path to previously exported save file.

    Returns:
        matrix: Camera Matrix
        distortion: Distortion Coefficents
        fov: (horizontal, vertical) field of view in degrees
    """
    data = np.load(filePath)
    matrix = data['matrix']
    distortion = data['distortion']
    fov = data['fov']
    data.close()

    return matrix, distortion, fov

## Solve PnP ##

def importMarkerPlacement(filepath):
    """Returns list of marker identifiers & corresponsing world space placement from a filepath."""
    markerPlacement = []
    with open(filepath, 'r') as data:
        for line in data:
            split = line[:-1].split(" ")
            markerPlacement.append((split[0], split[1],
                                    (float(split[2]), float(split[3]), float(split[4]))))
    return markerPlacement # (color, shape, (x, y, z))

def correlatePlacementWithDetection(placement, detection):
    """
    Prepares supplied marker placement data and detected marker data for camera solve.

    Args:
        placement: Marker placement list.
        detection: Marker detection dictionary.

    Returns:
        imagePoints: Numpy array of 2D image points.
        objectPoints: Numpy array of corresponding 3D coordinates.
    """
    imgPts = []
    objPts = []

    # Loop Through Marker Placements
    for marker in placement:
        if detection[marker[0]][marker[1]] is None:
            continue
        imgPts.append(detection[marker[0]][marker[1]][0])
        objPts.append(marker[2])

    # Convert to Numpy Arrays
    imagePoints = np.array(imgPts)
    objectPoints = np.array(objPts)

    return imagePoints, objectPoints

def solveCamera(cameraMatrix, distortion, imagePoints, objectPoints):
    """
    Solves for camera position and rotation in world space.

    Args:
        cameraMatrix: Camera Matrix
        distortion: Distortion Coefficents
        imagePoints: Numpy array of 2D image points.
        objectPoints: Numpy array of corresponding 3D coordinates.

    Returns:
        position: Camera's position vector.
        rotation: Camera's position vector.
    """
    _, rotation, position, inliers = cv2.solvePnPRansac(objectPoints, imagePoints, 
                                                        cameraMatrix, distortion)

    return position, rotation

### DEV CODE ###

# # Test Calibration
# iDir = filedialog.askdirectory(title="Select Directory")
# print(cameraCalibration(iDir, 23.5, 15.6, 9, 7))

# # Test Export
# iDir = filedialog.askdirectory(title="Select Directory")
# m, d, f = cameraCalibration(iDir, 23.5, 15.6, 9, 7)
# exportCalibration(iDir, "thisIsATest", m, d, f)
# print(m)
# print(d)
# print(f)

# # Test Import
# fileLocal = filedialog.askopenfilename(title="Select the Calibration File")
# m, d, f = importCalibration(fileLocal)
# print(m)
# print(d)
# print(f)
# print(importMarkerPlacement(fileLocal))
