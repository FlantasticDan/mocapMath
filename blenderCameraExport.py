#!/usr/bin/env python3

# exports solved camera data: focal length, angle of view, sensor size, transform

# Configure Workspace
import bpy
D = bpy.data
C = bpy.context

# Check script is running on a camera
if (C.object.type != 'CAMERA' or len(C.selected_objects) > 1):
    raise Exception("Select exactly one camera!")

# identify camera in blender data blocks
CAMERA = D.cameras[0]
CAMERA_OBJ = D.objects[C.object.name]

# bake camera solve data to keyframes
bpy.ops.clip.constraint_to_fcurve()

# identify scene in blender data blocks
SCENE = C.scene

# create export file
filepath = C.blend_data.filepath
filepath = filepath[:-6] # strip '.blend'
filepath = filepath.split("\\\\")
filePath = ""
for x in filepath:
    filePath = filePath + x + "\\"
EXPORT = open(filePath[:-1] + "_CAMERAexport.txt", "x")

# write header to export file
EXPORT.write("CAMERA DATA EXPORT for {}\n\n".format(D.movieclips[0].name))
EXPORT.write("RANGE {} to {}\n\n".format(SCENE.frame_start, SCENE.frame_end))
EXPORT.write("SENSOR(mm) {} x {}\n\n".format(CAMERA.sensor_width, CAMERA.sensor_height))
EXPORT.write("LENS(mm) {}\n\n".format(CAMERA.lens))
EXPORT.write("ANGLE OF VIEW(radians) {} x {}\n\n\n".format(CAMERA.angle_x, CAMERA.angle_y))
