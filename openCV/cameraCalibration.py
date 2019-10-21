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
        fov: (horizontal, vertixal) field of view in degrees
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


### DEV CODE ###

# # Test Calibration
# iDir = filedialog.askdirectory(title="Select Directory")
# print(cameraCalibration(iDir, 23.5, 15.6, 9, 7))
