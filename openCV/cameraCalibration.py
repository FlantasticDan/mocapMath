import os
import tkinter as tk
from tkinter import filedialog
import cv2
import numpy

# Configure Tkinter
root = tk.Tk()
root.withdraw()

imageDir = filedialog.askdirectory(title="Select Directory")

PATTERN = (9, 7)
SENSOR = (23.5, 15.6) # Nikon D5300
#SENSOR = (7.06, 5.295) # Pixel 2 XL

def makeChessboard(col, row):
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

def detectCorners(imagePath):
    imgC = cv2.imread(imagePath)
    found, intersects = cv2.findChessboardCorners(imgC, PATTERN)

    corners = []

    if found is True:
        for group in intersects:
            for intersect in group:
                corners.append((intersect[0], intersect[1]))
    else:
        raise Exception
    
    return corners

# Variables for Camera Calibration from Corner Detection
BOARD = makeChessboard(PATTERN[0], PATTERN[1])
objectPoints = []
imgPoints = []
success = 0
errors = 0

# Chessboard Corner Detection
for image in os.listdir(imageDir):
    img = os.path.join(imageDir, image)
    try:
        foundPoints = detectCorners(img)
        imgPoints.append(foundPoints)
        objectPoints.append(BOARD)
        success = success + 1
    except Exception:
        print("{} has errored.".format(image))
        errors = errors + 1
    if success is 1:
        sizeImg = cv2.imread(img)
        size = sizeImg.shape
        dimensions = (size[1], size[0])

print("--- Corner Detection Results ---\nSuccess: {}\nFail: {}\n".format(success, errors))

# Convert to Numpy Arrays
oPts = numpy.array(objectPoints)
iPts = numpy.array(imgPoints)
objects = oPts.astype('float32')
images = iPts.astype('float32')

# Camera Matrix Calculations
initialMatrix = cv2.initCameraMatrix2D(objects, images, dimensions)
error, matrix, distortion, rotation, translation = cv2.calibrateCamera(objects, images,
                                                                       dimensions, initialMatrix,
                                                                       None)

print("--- Camera Matrix Calculations ---\nError: {:.4f} px".format(error))

fov = [None, None]
fov[0], fov[1], focal, principal, ratio = cv2.calibrationMatrixValues(matrix, dimensions,
                                                                      SENSOR[0], SENSOR[1])

print("Focal Length: {:.4f} mm".format(focal))
