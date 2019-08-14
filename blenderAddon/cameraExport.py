import math
import bpy



class CameraExporter(bpy.types.Operator):
    bl_idname = "mocapmath.camera_export"
    bl_label = "Export Camera"
    bl_description = "Exports the selected camera position/rotation data for later calculation."

    @classmethod
    def poll(cls, context):
        return context.object.type == 'CAMERA' and len(context.selected_objects) is 1

    def execute(self, context):
        C = context
        D = bpy.data
        # identify camera in blender data blocks
        CAMERA = D.cameras[0]
        CAMERA_OBJ = D.objects[C.object.name]

        # bake camera solve data to keyframes
        bpy.ops.clip.constraint_to_fcurve()

        # identify scene in blender data blocks
        SCENE = C.scene
        CLIP = D.movieclips[0]

        # recalculate values blender records incorrectly
        ASPECT_RATIO = CLIP.size[1] / CLIP.size[0]
        SENSOR_Y = CAMERA.sensor_width * ASPECT_RATIO
        ANGLE_Y = 2 * (math.atan(SENSOR_Y / (2 * CAMERA.lens)))

        # create export file
        filepath = C.blend_data.filepath
        filepath = filepath[:-6] # strip '.blend'
        filepath = filepath.split("\\\\")
        filePath = ""
        for x in filepath:
            filePath = filePath + x + "\\"
        EXPORT = open(filePath[:-1] + "_CAMERAexport.txt", "x")

        # write header to export file
        EXPORT.write("CAMERA DATA EXPORT for {}\n\n".format(CLIP.name))
        EXPORT.write("RANGE {} to {}\n\n".format(SCENE.frame_start, SCENE.frame_end))
        EXPORT.write("RESOLUTION {} x {}\n\n".format(CLIP.size[0], CLIP.size[1]))
        EXPORT.write("SENSOR(mm) {} x {}\n\n".format(CAMERA.sensor_width, SENSOR_Y))
        EXPORT.write("LENS(mm) {}\n\n".format(CAMERA.lens))
        EXPORT.write("ANGLE OF VIEW(radians) {} x {}\n\n\n".format(CAMERA.angle_x, ANGLE_Y))

        # keyframe export
        frame = SCENE.frame_start
        while frame <= SCENE.frame_end:
            SCENE.frame_set(frame)
            EXPORT.write("{:05d} ".format(frame))
            EXPORT.write("{:6f} ".format(CAMERA_OBJ.location[0])) # position X
            EXPORT.write("{:6f} ".format(CAMERA_OBJ.location[1])) # position Y
            EXPORT.write("{:6f} ".format(CAMERA_OBJ.location[2])) # position Z
            EXPORT.write("{:6f} ".format(CAMERA_OBJ.rotation_euler[0])) # rotation X (radians)
            EXPORT.write("{:6f} ".format(CAMERA_OBJ.rotation_euler[1])) # rotation Y (radians)
            EXPORT.write("{:6f}\n".format(CAMERA_OBJ.rotation_euler[2])) # rotation Z (radians)
            frame = frame + 1

        EXPORT.close() # close export file

        return {"FINISHED"}
