import os
import sys
import tkinter as tk
from tkinter import filedialog
import lox
import cv2
import numpy

# Configure Tkinter
root = tk.Tk()
root.withdraw()

imageDir = filedialog.askdirectory(title="Select Directory")

COUNT = 0
QUENE = len(os.listdir(imageDir))
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

@lox.thread(8)
def detectCorners(imagePath, imgFile):
    global COUNT

    imgC = cv2.imread(imagePath)
    found, intersects = cv2.findChessboardCorners(imgC, PATTERN, flags=cv2.CALIB_CB_FAST_CHECK)

    corners = []

    if found is True:
        for group in intersects:
            for intersect in group:
                corners.append((intersect[0], intersect[1]))
        COUNT += 1
        sys.stdout.write("\r{:02d} of {} | {} Processed        ".format(COUNT, QUENE, imgFile))
        sys.stdout.flush()
        return corners
    else:
        COUNT += 1
        sys.stdout.write("\r{:02d} of {} | {} Failed        ".format(COUNT, QUENE, imgFile))
        sys.stdout.flush()
        return [False, imgFile]

# Variables for Camera Calibration from Corner Detection
BOARD = makeChessboard(PATTERN[0], PATTERN[1])
objectPoints = []
imgPoints = []
success = 0
errors = 0

# Start Threads for Corner Detection
for image in os.listdir(imageDir):
    img = os.path.join(imageDir, image)
    detectCorners.scatter(img, image)

# Collect and Verify Corner Data from Threads
imgProcess = detectCorners.gather()

print("")

for result in imgProcess:
    if result[0] is not False:
        imgPoints.append(result)
        objectPoints.append(BOARD)
        success += 1
    else:
        errors += 1
        print("{} failed.".format(result[1]))

print("\n--- Corner Detection Results ---\nSuccess: {}\nFail: {}\n".format(success, errors))

# Convert to Numpy Arrays
oPts = numpy.array(objectPoints)
iPts = numpy.array(imgPoints)
objects = oPts.astype('float32')
images = iPts.astype('float32')

# Detect Image Dimensions
sizeImg = cv2.imread(os.path.join(imageDir, os.listdir(imageDir)[0]))
size = sizeImg.shape
dimensions = (size[1], size[0])

# Camera Matrix Calculations
initialMatrix = cv2.initCameraMatrix2D(objects, images, dimensions)
error, matrix, distortion, rotation, translation = cv2.calibrateCamera(objects, images,
                                                                       dimensions, initialMatrix,
                                                                       None)

print("--- Camera Matrix Calculations ---\nError: {:.4f} px".format(error))

fov = [None, None]
fov[0], fov[1], focal, principal, ratio = cv2.calibrationMatrixValues(matrix, dimensions,
                                                                      SENSOR[0], SENSOR[1])

print("Focal Length: {:.4f} mm\n".format(focal))
