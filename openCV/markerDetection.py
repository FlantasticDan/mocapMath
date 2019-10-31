"""Tools for detecting and identifying markers in images."""

import tkinter as tk
from tkinter import filedialog
from statistics import mode
import os
import sys
import cv2
import numpy as np
from shapely.geometry.point import Point
from shapely.geometry.polygon import Polygon
from shapely.geometry import LineString

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

# Marker Pattern Importer
def importPattern(filepath):
    """ Return a numPy array given a .txt file path."""
    markerPattern = ""
    with open(resource_path(filepath), "r") as pattern:
        for line in pattern:
            markerPattern += line.rstrip('\n') + " "
    patternList = markerPattern.split(" ")
    del patternList[64]
    shape = np.reshape(patternList, (8, 8))
    return shape.astype(dtype="float16")

# Import Marker Patterns
CIRCLE = (importPattern("markerArrays\\circle.txt"), "circle")
LINE = (importPattern("markerArrays\\line.txt"), "line")
SLASH = (importPattern("markerArrays\\slash.txt"), "slash")
SQUARE = (importPattern("markerArrays\\square.txt"), "square")
TRIANGLE = (importPattern("markerArrays\\triangle.txt"), "triangle")
Y = (importPattern("markerArrays\\y.txt"), "y")
PATTERNS = (CIRCLE, LINE, SLASH, SQUARE, TRIANGLE, Y)

# Pattern Tester
def checkPattern(mystery):
    """Checks an unknown array against known patterns, returns the matching pattern's identifier."""
    for pattern in PATTERNS:
        if np.allclose(mystery, pattern[0], 0, 0.5):
            return pattern[1]
    return False

# Color Finder
def findColor(blueChannel, greenChannel, redChannel):
    """
    Determine the color of processed marker arrays.

    Args:
        blueChannel: NumPy array of a marker's binary blue channel.
        greenChannel: NumPy array of a marker's binary green channel.
        redChannel: NumPy array of a marker's binary red channel.

    Returns:
        Color ID string of the given marker channels or False if undetermined
    """
    x3x3 = checkColor(redChannel[3][3], greenChannel[3][3], blueChannel[3][3])
    x3x4 = checkColor(redChannel[3][4], greenChannel[3][4], blueChannel[3][4])
    x4x3 = checkColor(redChannel[4][3], greenChannel[4][3], blueChannel[4][3])
    x4x4 = checkColor(redChannel[4][4], greenChannel[4][4], blueChannel[4][4])
    colorBits = [x3x3, x3x4, x4x3, x4x4]
    try:
        return mode(colorBits)
    except ValueError:
        for bit in colorBits:
            if bit is not False:
                return bit

def checkColor(r, g, b):
    """Returns color ID string for given bit."""
    if r == 1:
        if b == 1:
            if g == 0:
                return "magenta"
            else:
                return False
        else:
            if g == 0:
                return "red"
            else:
                return "yellow"
    else:
        if b == 1:
            if g == 0:
                return "blue"
            else:
                return "cyan"
        else:
            if g == 1:
                return "green"
            else:
                return False

# Determine Image Object Type
def findImgObject(imgObject):
    """Takes an image object (file path to image or image array) and return it in array form."""
    if os.path.exists(imgObject):
        return cv2.imread(imgObject)
    return imgObject

def hsvAdjustment(image):
    """Applys a threshold to saturation values and an alignment to hue values."""
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    # Threshold Saturation
    saturation = hsv[:, :, 1] # [0, 255]
    np.place(hsv[:, :, 1], saturation > 64, 255)

    # Align Hue
    hue = hsv[:, :, 0] # [0, 179]
    np.place(hsv[:, :, 0], np.logical_or(hue < 15, hue > 173), 0) # red
    np.place(hsv[:, :, 0], np.logical_and(hue >= 15, hue <= 45), 30) # yellow
    np.place(hsv[:, :, 0], np.logical_and(hue > 45, hue <= 75), 60) # green
    np.place(hsv[:, :, 0], np.logical_and(hue > 75, hue <= 105), 90) # cyan
    np.place(hsv[:, :, 0], np.logical_and(hue > 105, hue <= 135), 120) # blue
    np.place(hsv[:, :, 0], np.logical_and(hue > 135, hue <= 173), 150) # magenta

    # Clamp Black
    value = hsv[:, :, 2]
    np.place(hsv[:, :, 2], value < 85, 0)

    return cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)

# Image Pre-Processing
def imageProcessing(imgPath):
    """
    Processes an image for marker detection.

    Args:
        imgPath: Path to an openCV compatiable image.

    Returns:
        Array of contours, openCV image object.
    """
    # Pre-Processing
    img = findImgObject(imgPath)
    img = hsvAdjustment(img)
    grey = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    greyInv = cv2.bitwise_not(grey)

    # Masking
    _, mask = cv2.threshold(greyInv, 255, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    # mask = cv2.adaptiveThreshold(greyInv, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 11, 2)

    # Shape Detection
    contour = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    return contour[0], img

# Find Center of Quadrangles
def findCenter(a, b, c, d):
    """Returns the center of a quadrangle given 4 Shapley points in clockwise order."""
    ac = LineString([a, c])
    bd = LineString([b, d])
    center = ac.intersection(bd)
    try:
        return (center.x, center.y)
    except AttributeError:
        return None

# Check for Square
def isSquare(shape, minPerimeter=150):
    """Returns the corners and center of a sqaure-like contour or false if not square-like."""
    peri = cv2.arcLength(shape, True)
    corners = cv2.approxPolyDP(shape, 0.02 * peri, True)
    if len(corners) is 4 and peri > minPerimeter: # check shape is a quadrangle of useable size
        a = Point(corners[0][0][0], corners[0][0][1])
        b = Point(corners[1][0][0], corners[1][0][1])
        c = Point(corners[2][0][0], corners[2][0][1])
        d = Point(corners[3][0][0], corners[3][0][1])
        ab = a.distance(b)
        bc = b.distance(c)
        lineRatio = max((ab, bc)) / min((ab, bc))
        if lineRatio < 2: # check that quadrangle is likely a square
            center = findCenter(a, b, c, d)
            return corners, center
    return False, False

# Identify Squares from Shapes
def findSquares(contour):
    """Returns dictionary of square-like 'corners' and 'center(s)' from a set of contours."""
    squares = []
    c = -1
    for shape in contour:
        corners, center = isSquare(shape)
        if corners is not False:
            c += 1
            squares.append([])
            squares[c] = {}
            squares[c]['corners'] = []
            for pt in corners:
                squares[c]['corners'].append([pt[0][0], pt[0][1]])
            squares[c]['center'] = center
    return squares

# Sort for Interior Squares
def removeExteriorSquares(squares):
    """Sorts a sqaure-like dictionary returning a dictionary void of exterior bounding squares."""
    removal = []
    return squares
    # Check for Squares contatined in other Squares
    for sq, _ in enumerate(squares):
        test = Polygon([(squares[sq]['corners'][0][0], squares[sq]['corners'][0][1]),
                        (squares[sq]['corners'][1][0], squares[sq]['corners'][1][1]),
                        (squares[sq]['corners'][2][0], squares[sq]['corners'][2][1]),
                        (squares[sq]['corners'][3][0], squares[sq]['corners'][3][1])])
        for bd, _ in enumerate(squares):
            if bd == sq:
                pass
            else:
                bding = Polygon([(squares[bd]['corners'][0][0], squares[bd]['corners'][0][1]),
                                 (squares[bd]['corners'][1][0], squares[bd]['corners'][1][1]),
                                 (squares[bd]['corners'][2][0], squares[bd]['corners'][2][1]),
                                 (squares[bd]['corners'][3][0], squares[bd]['corners'][3][1])])
                if test.contains(bding):
                    removal.append(sq)
                    break

    # Delete all Exterior Squares
    removal.sort(reverse=True)
    for index in removal:
        del squares[index]

    return squares

# Create Marker Crops
def markerDeformer(squares, img, size=256):
    """
    Deforms and crops an image into marker sqaures.

    Args:
        sqaures: Sqaure-like dictionary.
        img: openCV image object from which the square-like dictionary was derived.

    Returns:
        A list of tuples in the form:
            (openCV image object of marker crop,
             center point coordinates in original image,
             list of corner coordinates from original image)
    """
    square = np.array([[0, 0], [0, size], [size, size], [size, 0]], dtype="float32")
    markers = []
    for rawMarker in squares:
        persp = cv2.getPerspectiveTransform(np.array(rawMarker['corners'], dtype="float32"), square)
        warped = cv2.warpPerspective(img, persp, (size, size))
        markers.append((warped, rawMarker['center'], rawMarker['corners']))

    return markers # (marker image, center point of marker)

## MARKER DETECTION ##
def findMarkers(imagePath):
    """
    Finds markers in an image.

    Args:
        imagePath: Path to an openCV compatiable image.

    Returns:
        A list of tuples in the form:
            (openCV image object of marker crop,
             center point coordinates in original image,
             list of corner coordinates from original image)
    """
    imageContours, image = imageProcessing(imagePath)
    foundSquares = findSquares(imageContours)
    sortedSquares = removeExteriorSquares(foundSquares)
    foundMarkers = markerDeformer(sortedSquares, image)

    return foundMarkers

## MARKER IDENTIFICATION ##

# Create Marker Binary Maps
def createMarkerBinaryMaps(warpedMarker, bitSize=32):
    """Returns thresholded 8x8 numPy bit per channel arrays from marker images."""
    tag = np.empty([8, 8, 4])
    yChunk = 0
    while yChunk < 8:
        xChunk = 0
        while xChunk < 8: # Average each channel of each bit
            tag[yChunk, xChunk] = cv2.mean(warpedMarker[(yChunk*bitSize) : ((yChunk+1)*bitSize),
                                                        (xChunk*bitSize) : ((xChunk+1)*bitSize)])
            xChunk += 1
        yChunk += 1

    # Threshold Bits per Channel BGR
    cleanTag = np.delete(tag, 3, 2)
    cleanTag = np.array(cleanTag, dtype="uint8")
    grayTag = cv2.cvtColor(cleanTag, cv2.COLOR_BGR2GRAY)
    _, grayBinary = cv2.threshold(grayTag, 128, 1, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    _, blueBinary = cv2.threshold(cleanTag[:, :, 0], 128, 1, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    _, greenBinary = cv2.threshold(cleanTag[:, :, 1], 128, 1, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    _, redBinary = cv2.threshold(cleanTag[:, :, 2], 128, 1, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    return grayBinary, blueBinary, greenBinary, redBinary

def isBoxed(binary):
    """Determines if a bit array contains the marker border box."""
    for bit in binary[0]:
        if bit != 0:
            return False
    for bit in binary[7]:
        if bit != 0:
            return False
    c = 1
    while c < 7:
        if binary[c][0] != 0 or binary[c][7] != 0:
            return False
        c += 1

    return True

def isOriented(binary):
    """Determines if a bit array contains the marker orientation bits."""
    rot = 0
    while rot < 4:
        if binary[1][1] == 0 and binary[1][2] == 0 and binary[2][1] == 0 and binary[5][6] == 1:
            return True, rot, binary
        else:
            binary = np.rot90(binary)
            rot += 1
    return False, False, binary

def isAMarker(binary):
    """Determines if a bit array is a marker."""
    # Check Permimeter Bits
    barrier = isBoxed(binary)

    # Check for Notch
    if barrier is True:
        orientation, rot, binary = isOriented(binary)
    else:
        return False, False, binary

    # Check Parity Bit
    if orientation is True:
        return True, rot, binary

    return False, False, binary

def findPattern(grayChannel, redChannel, greenChannel, blueChannel, rot):
    """
    Finds the marker pattern from bit channel arrays.

    Args:
        grayChannel: NumPy bit array for the marker image's gray channel.
        redChannel: NumPy bit array for the marker image's red channel.
        graeenChannel: NumPy bit array for the marker image's green channel.
        blueChannel: NumPy bit array for the marker image's blue channel.
        rot (int): number of rotations performed to orient bit array.

    Returns:
        Pattern ID String.
    """
    pattern = checkPattern(grayChannel)
    if pattern is False:
        redChannel = np.rot90(redChannel, rot)
        pattern = checkPattern(redChannel)
        if pattern is False:
            greenChannel = np.rot90(greenChannel, rot)
            pattern = checkPattern(greenChannel)
            if pattern is False:
                blueChannel = np.rot90(blueChannel, rot)
                pattern = checkPattern(blueChannel)
    return pattern

def identifyMarker(unkownMarker):
    """
    Identifies the color, pattern, center and corners of a marker.

    Args:
        unknownMarker: A tuple in the form: (openCV image object of marker crop,
                                             center point coordinates in original image,
                                             list of corner coordinates from original image)

    Returns:
        Color ID String, Pattern ID String, Marker Center Coordinates (x, y), Marker Corner Array.
    """
    gray, blue, green, red = createMarkerBinaryMaps(unkownMarker[0])
    isMarker, rotation, gray = isAMarker(gray)

    if isMarker is False:
        isMarker, rotation, red = isAMarker(red)
        if isMarker is False:
            return None

    # Pattern Identification
    pattern = findPattern(gray, red, green, blue, rotation)
    if pattern is False: # Rotate gray once and force pattern search again
        gray = np.rot90(gray)
        isMarker, newRotation, gray = isAMarker(gray)
        rotation = newRotation + rotation + 1
        if isMarker is False:
            isMarker, rotation, red = isAMarker(red)
            if isMarker is False:
                return None
        pattern = findPattern(gray, red, green, blue, rotation)

    # Determine Color
    color = findColor(blue, green, red)

    return color, pattern, unkownMarker[1], unkownMarker[2] # (color, pattern, center, [corners])

def markerID(imagePath):
    """"Returns an Identified Markers Dictionary from an openCV compatible image path."""
    markerIDs = []
    markers = findMarkers(imagePath)
    for marker in markers:
        markerIDs.append(identifyMarker(marker))
    return organizeMarkerIDs(markerIDs)

def organizeMarkerIDs(unsortedIDs):
    """Returns an organized marker dictionary from Marker ID List."""
    colors = ['red', 'yellow', 'green', 'cyan', 'blue', 'magenta', False]
    patterns = ['triangle', 'square', 'circle', 'slash', 'line', 'y', False]

    sortedIDs = {}

    for c in colors:
        sortedIDs[c] = {}
        for p in patterns:
            sortedIDs[c][p] = None

    for marker in unsortedIDs:
        if marker is None:
            continue
        sortedIDs[marker[0]][marker[1]] = (marker[2], marker[3])

    return sortedIDs

def getMarkerColor(colorStr):
    """Given a color ID string returns the RGB tuple from the color ID String."""
    if colorStr == 'blue':
        return (255, 0, 0)
    elif colorStr == 'red':
        return (0, 0, 255)
    elif colorStr == 'green':
        return (0, 255, 0)
    elif colorStr == 'cyan':
        return (255, 255, 0)
    elif colorStr == 'yellow':
        return (0, 255, 255)
    elif colorStr == 'magenta':
        return (255, 0, 255)
    return (0, 0, 0)

def drawMarkerID(imagePath, markers):
    """
    Draws marker identification graphics ontop of source image.

    Args:
        imagePath: File path to the source openCV compatible image.
        markers: List of identified markers.

    Returns:
        Annotated openCV image object.
    """
    img = cv2.imread(imagePath)
    colors = ['red', 'yellow', 'green', 'cyan', 'blue', 'magenta', False]
    patterns = ['triangle', 'square', 'circle', 'slash', 'line', 'y', False]
    font = cv2.FONT_HERSHEY_SIMPLEX

    for c in colors:
        markerColor = getMarkerColor(c)
        for p in patterns:
            if markers[c][p] is None:
                continue
            corners = np.array([markers[c][p][1][0], markers[c][p][1][1],
                                markers[c][p][1][2], markers[c][p][1][3]])
            center = (int(markers[c][p][0][0]), int(markers[c][p][0][1]))
            cv2.polylines(img, [corners], True, markerColor, 10)
            cv2.putText(img, "{}".format(p), center, font, 2, (0, 0, 0), 10)
            cv2.putText(img, "{}".format(p), center, font, 2, markerColor, 4)

    return img

## DEV CODE ##

# # Pattern Debug
# PATPATH = filedialog.askdirectory(title="Debug Directory")
# import random
# def patternDebug(markerImg, grayBinary, redBinary, greenBinary, blueBinary, rot):

#     # Generate Identifier
#     random_number = random.randint(0,16777215)
#     hexID = format(random_number, 'x')

#     cv2.imwrite("{}\{}.jpg".format(PATPATH, hexID), markerImg)

#     np.savetxt("{}\{}_red.txt".format(PATPATH, hexID), np.rot90(redBinary, rot), '%1d')
#     np.savetxt("{}\{}_green.txt".format(PATPATH, hexID), np.rot90(greenBinary, rot), '%1d')
#     np.savetxt("{}\{}_blue.txt".format(PATPATH, hexID), np.rot90(blueBinary, rot), '%1d')
#     np.savetxt("{}\{}_gray.txt".format(PATPATH, hexID), grayBinary, '%1d')

#     return

# # Declare Image to be Analyzed
# imageFile = resource_path(filedialog.askopenfilename(title="Select an Image"))

# # Print Marker Summary
# array = markerID(imageFile)
# markFail = 0
# colorFail = 0
# shapeFail = 0
# bigFail = 0
# colorWin = 0
# shapeWin = 0
# fullWin = 0

# for mk in array:
#     if mk is None:
#         markFail += 1
#     else:
#         if mk[0] is False:
#             colorFail += 1
#         else:
#             colorWin += 1
#         if mk[1] is False:
#             shapeFail += 1
#         else:
#             shapeWin += 1
#         if mk[0] is False and mk[1] is False:
#             bigFail += 1
#         else:
#             fullWin += 1

# print(" T  |  F  | Category")
# print("{:^3d} | {:^3d} | Marker Detections".format(fullWin, bigFail))
# print("{:^3d} | {:^3d} | Color Detections".format(colorWin, colorFail))
# print("{:^3d} | {:^3d} | Shape Detections".format(shapeWin, shapeFail))
# print("{:^3d} | --- | Marker Rejections".format(markFail))

# # Print Array of Marker IDs
# print(markerID(imageFile))

# # Export Images
# exportPath = filedialog.askdirectory(title="Output Directory")
# cv2.imwrite(exportPath + "\marked.jpg", drawMarkerID(imageFile, markerID(imageFile)))

# Analyze directory of Images
# imageDir = filedialog.askdirectory(title="Image Directory")
# for image in os.listdir(imageDir):
#     img = os.path.join(imageDir, image)
#     print(markerID(img))
#     cv2.imwrite("{}\{}_marked.jpg".format(exportPath, image), drawMarkerID(img, markerID(img)))
