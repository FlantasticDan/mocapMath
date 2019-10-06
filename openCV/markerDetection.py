import tkinter as tk
from tkinter import filedialog
import os
import sys
import cv2
import numpy as np
from shapely.geometry.point import Point
from shapely.geometry.polygon import Polygon

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

# Declare Image to be Analyzed
imageFile = resource_path(filedialog.askopenfilename(title="Select an Image"))
img = cv2.imread(imageFile, flags=cv2.IMREAD_COLOR)

## MARKER DETECTION ##

# Image Pre-Processing
grey = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
grey_inv = cv2.bitwise_not(grey)
threshold, mask = cv2.threshold(grey_inv, 255, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

# Shape Detection
canny = cv2.Canny(mask, 100, 200)
contour = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

# Identify Squares from Shapes
squares = []
count = -1
for s, shape in enumerate(contour[0]):
    peri = cv2.arcLength(shape, True)
    corners = cv2.approxPolyDP(shape, 0.02 * peri, True)
    if len(corners) is 4 and peri > 50: # check shape is a quadrangle of useable size
        a = Point(corners[0][0][0], corners[0][0][1])
        b = Point(corners[1][0][0], corners[1][0][1])
        c = Point(corners[2][0][0], corners[2][0][1])
        ab = a.distance(b)
        bc = b.distance(c)
        lineRatio = max((ab, bc)) / min ((ab, bc))
        if lineRatio < 2: # check that quadrangle is likely a square
            count += 1
            squares.append([])
            squares[count] = []
            for pt in corners:
                squares[count].append([pt[0][0], pt[0][1]])

# Sort for Interior Squares
removal = []
for sq, square in enumerate(squares):
    test = Polygon([(squares[sq][0][0], squares[sq][0][1]),
                    (squares[sq][1][0], squares[sq][1][1]),
                    (squares[sq][2][0], squares[sq][2][1]),
                    (squares[sq][3][0], squares[sq][3][1])])
    for bound, uh in enumerate(squares):
        if bound == sq:
            pass
        else:
            bounding = Polygon([(squares[bound][0][0], squares[bound][0][1]),
                                (squares[bound][1][0], squares[bound][1][1]),
                                (squares[bound][2][0], squares[bound][2][1]),
                                (squares[bound][3][0], squares[bound][3][1])])
            if test.contains(bounding):
                removal.append(sq)
                break

# Delete all Exterior Squares
removal.sort(reverse = True)
for index in removal:
    del squares[index]

# Create Marker Crops
size = 96 # must be a multiple of 8
square = np.array([[0, 0], [0, size], [size, size], [size, 0]], dtype="float32")
markers = []
for rawMarker in squares:
    perspective = cv2.getPerspectiveTransform(np.array(rawMarker, dtype="float32"), square)
    warped = cv2.warpPerspective(img, perspective, (size, size))
    markers.append(warped)

## MARKER IDENTIFICATION ##

# Create bits
bitSize = int(size / 8)
markerIDs = []

# Loop through markers
for marker in markers:
    tag = np.empty([8, 8, 4])
    yChunk = 0
    while yChunk < 8:
        xChunk = 0
        while xChunk < 8:
            tag[yChunk, xChunk] = cv2.mean(marker[(yChunk*bitSize) : ((yChunk+1)*bitSize), # Average each bit
                                                  (xChunk*bitSize) : ((xChunk+1)*bitSize)])
            xChunk += 1
        yChunk += 1
    
    # Threshold bits per channel BGR
    cleanTag = np.delete(tag, 3, 2)
    cleanTag = np.array(cleanTag, dtype="uint8")
    grayTag = cv2.cvtColor(cleanTag, cv2.COLOR_BGR2GRAY)
    _, gray = cv2.threshold(grayTag, 128, 1, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    _, blue = cv2.threshold(cleanTag[:, :, 0], 128, 1, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    _, green = cv2.threshold(cleanTag[:, :, 1], 128, 1, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    _, red = cv2.threshold(cleanTag[:, :, 2], 128, 1, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    # Decode Markers #
    # Check Permimeter Bits
    barrier = True
    for bit in gray[0]:
        if bit != 0:
            barrier = False
            break
    if barrier is True:
        for bit in gray[7]:
            if bit != 0:
                barrier = False
                break
    count = 1
    while count < 7:
        if gray[count][0] != 0 or gray[count][7] != 0:
            barrier = False
            break
        count += 1

    # Check for Notch
    if barrier is True:
        rotation = 0
        notch = False
        while notch is False and rotation < 4:
            if gray[1][1] == 0 and gray[1][2] == 0 and gray[2][1] == 0:
                notch = True
                break
            else:
                gray = np.rot90(gray)
                rotation += 1

    # Check for Parity Bit
    if barrier is True and notch is True:
        if gray[5][6] == 1:
            parity = True
        else:
            parity = False


## DEV CODE ##

# Show Found Markers
# for m, mark in enumerate(markers):
#     cv2.imshow("Marker {}".format(m), mark)
# cv2.waitKey(0)

# Export Intermediate Images
# exportPath = filedialog.askdirectory(title="Output Directory")
# cv2.imwrite(exportPath + "\Canny.jpg", canny)
# cv2.imwrite(exportPath + "\Mask.jpg", mask)
