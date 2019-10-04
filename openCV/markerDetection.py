import tkinter as tk
from tkinter import filedialog
import os
import sys
import cv2
import numpy as np
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
    if len(corners) is 4 and peri > 50: # check quadrangle is of useable size
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
size = 250
square = np.array([[0,0], [0, size], [size, size], [size, 0]], dtype = "float32")
markers = []
for rawMarker in squares:
    perspective = cv2.getPerspectiveTransform(np.array(rawMarker, dtype = "float32"), square)
    warped = cv2.warpPerspective(img, perspective, (size, size))
    markers.append(warped)

# DEV CODE #

# Show Found Markers
# for m, mark in enumerate(markers):
#     cv2.imshow("Marker {}".format(m), mark)
# cv2.waitKey(0)

# Export Intermediate Images
# exportPath = filedialog.askdirectory(title="Output Directory")
# cv2.imwrite(exportPath + "\Canny.jpg", canny)
# cv2.imwrite(exportPath + "\Mask.jpg", mask)
