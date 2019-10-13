import tkinter as tk
from tkinter import filedialog
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
    markerPattern = ""
    with open(resource_path(filepath), "r") as pattern:
        for line in pattern:
            markerPattern += line.rstrip('\n') + " "
    patternList = markerPattern.split(" ")
    del patternList[64]
    shape = np.reshape(patternList, (8, 8))
    return shape.astype(dtype="float16")

# Import Marker Patterns
CIRCLE = (importPattern("markerArrays\circle.txt"), "circle")
LINE = (importPattern("markerArrays\line.txt"), "line")
SLASH = (importPattern("markerArrays\slash.txt"), "slash")
SQUARE = (importPattern("markerArrays\square.txt"), "square")
TRIANGLE = (importPattern("markerArrays\\triangle.txt"), "triangle")
Y = (importPattern("markerArrays\y.txt"), "y")
PATTERNS = (CIRCLE, LINE, SLASH, SQUARE, TRIANGLE, Y)

# Pattern Tester
def checkPattern(mystery):
    for pattern in PATTERNS:
        if np.allclose(mystery, pattern[0], 0, 0.5):
            return pattern[1]
    return False

# Color Finder
def findColor(blueChannel, greenChannel, redChannel):
    r = redChannel[3][3]
    g = greenChannel[3][3]
    b = blueChannel[3][3]

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

# Image Pre-Processing
def imageProcessing(imgPath):

    # Pre-Processing
    img = cv2.imread(imgPath, flags=cv2.IMREAD_COLOR)
    img = cv2.addWeighted(img, 2, np.zeros(img.shape, img.dtype), 0, -150) # Add Contrast
    grey = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    grey_inv = cv2.bitwise_not(grey)
    _, mask = cv2.threshold(grey_inv, 255, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    # Shape Detection
    contour = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    return contour[0], img

# Find Center of Quadrangles
def findCenter(a, b, c, d):
    ac = LineString([a, c])
    bd = LineString([b, d])
    center = ac.intersection(bd)
    try:
        return (center.x, center.y)
    except AttributeError:
        return None

# Check for Square
def isSquare(shape, minPerimeter=50):
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
    removal = []

    # Check for Squares contatined in other Squares
    for sq, _ in enumerate(squares):
        test = Polygon([(squares[sq]['corners'][0][0], squares[sq]['corners'][0][1]),
                        (squares[sq]['corners'][1][0], squares[sq]['corners'][1][1]),
                        (squares[sq]['corners'][2][0], squares[sq]['corners'][2][1]),
                        (squares[sq]['corners'][3][0], squares[sq]['corners'][3][1])])
        for bound, _ in enumerate(squares):
            if bound == sq:
                pass
            else:
                bounding = Polygon([(squares[bound]['corners'][0][0], squares[bound]['corners'][0][1]),
                                    (squares[bound]['corners'][1][0], squares[bound]['corners'][1][1]),
                                    (squares[bound]['corners'][2][0], squares[bound]['corners'][2][1]),
                                    (squares[bound]['corners'][3][0], squares[bound]['corners'][3][1])])
                if test.contains(bounding):
                    removal.append(sq)
                    break

    # Delete all Exterior Squares
    removal.sort(reverse=True)
    for index in removal:
        del squares[index]
    
    return squares

# Create Marker Crops
def markerDeformer(squares, img, size=256):
    square = np.array([[0, 0], [0, size], [size, size], [size, 0]], dtype="float32")
    markers = []
    for rawMarker in squares:
        perspective = cv2.getPerspectiveTransform(np.array(rawMarker['corners'], dtype="float32"), square)
        warped = cv2.warpPerspective(img, perspective, (size, size))
        markers.append((warped, rawMarker['center'], rawMarker['corners']))
    
    return markers # (marker image, center point of marker)

## MARKER DETECTION ##
def findMarkers(imagePath):
    imageContours, image = imageProcessing(imagePath)
    foundSquares = findSquares(imageContours)
    sortedSquares = removeExteriorSquares(foundSquares)
    foundMarkers = markerDeformer(sortedSquares, image)

    return foundMarkers

## MARKER IDENTIFICATION ##

# Create Marker Binary Maps
def createMarkerBinaryMaps(warpedMarker, bitSize=32):
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

def isNotched(binary):
    rot = 0
    while rot < 4:
        if binary[1][1] == 0 and binary[1][2] == 0 and binary[2][1] == 0:
            return True, rot, binary
        else:
            binary = np.rot90(binary)
            rot += 1
    return False, False, binary

def hasParity(binary, rotation):
    if binary[5][6] == 1:
        return True, rotation, binary
    else:
        binary = np.rot90(binary)
        notch, rot, binary = isNotched(binary)
        if notch is True and binary[5][6] == 1:
            return True, rotation + rot + 1, binary
    return False, False, binary

def isAMarker(binary):
    # Check Permimeter Bits
    barrier = isBoxed(binary)

    # Check for Notch
    if barrier is True:
        notch, rot, binary = isNotched(binary)
    else:
        return False, False, binary
    
    # Check Parity Bit
    if notch is True:
        parity, rot, binary = hasParity(binary, rot)
        if parity is True:
            return True, rot, binary

    return False, False, binary

def findPattern(grayChannel, redChannel, greenChannel, blueChannel, rot):
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
    markerIDs = []
    markers = findMarkers(imagePath)
    for marker in markers:
        markerIDs.append(identifyMarker(marker))
    return markerIDs

def getMarkerColor(marker):
    colorStr = marker[0]
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
    img = cv2.imread(imagePath)
    for marker in markers:
        if marker is not None:
            corners = np.array([marker[3][0], marker[3][1], marker[3][2], marker[3][3]], np.int32)
            cv2.polylines(img, [corners], True, getMarkerColor(marker), 10)
            cv2.putText(img, "{}".format(marker[1]), (int(marker[2][0]), int(marker[2][1])), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 0), 10)
            cv2.putText(img, "{}".format(marker[1]), (int(marker[2][0]), int(marker[2][1])), cv2.FONT_HERSHEY_SIMPLEX, 2, getMarkerColor(marker), 4)
    return img

## DEV CODE ##

# Pattern Debug
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
