#!/usr/bin/env python3

# imports solved mocap data into Blender and animated cubes for later rigging use

# Configure Workspace
import bpy
D = bpy.data
C = bpy.context

# find solver file
filepath = C.blend_data.filepath
filepath = filepath.split("\\")
filePath = ""
for x in range(0, len(filepath) - 1):
    filePath = filePath + filepath[x] + "\\"
SOLVER = open(filePath + "mocapSolved.txt")

# read solver file
SOLVE = {}
for l, line in enumerate(SOLVER):
    if l == 2:
        split = line[:-1].split(" ")
        SOLVE['frame_range'] = (int(split[1]), int(split[3]))
    elif l > 4:
        split = line[:-1].split(" ")
        if split[0] == "#####":
            currentMarker = split[1]
            SOLVE[currentMarker] = {}
        else:
            try:
                SOLVE[currentMarker][int(split[0])] = (float(split[1]), float(split[2]),
                                                       float(split[3]))
            except IndexError:
                pass

# set Blender frame range
C.scene.frame_start = SOLVE['frame_range'][0]
C.scene.frame_end = SOLVE['frame_range'][1]

def makeCube(name):

    '''Creates cube and returns blender data object.'''

    bpy.ops.mesh.primitive_cube_add(size=0.1)
    C.object.name = name
    return D.objects[name]

def addKey(obj, frame, transform):

    '''Add location keyframe'''

    obj.location = transform
    obj.keyframe_insert(data_path="location", frame=frame)

for marker in SOLVE:
    if marker != "frame_range":
        joint = makeCube(marker)
        for frame in SOLVE[marker]:
            addKey(joint, frame, SOLVE[marker][frame])
