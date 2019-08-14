import bpy

class TrackerExporter(bpy.types.Operator):
    bl_idname = "mocapmath.track_export"
    bl_label = "Export Trackers"
    bl_description = "Exports all tracked markers for later calculation."

    def execute(self, context):
        # identify scene and tracks in blender data blocks
        C = context
        D = bpy.data
        SCENE = C.scene
        CLIP = D.movieclips[0]
        TRACKER = CLIP.tracking.tracks

        # create export file
        filepath = C.blend_data.filepath
        filepath = filepath[:-6] # strip '.blend'
        filepath = filepath.split("\\\\")
        filePath = ""
        for x in filepath:
            filePath = filePath + x + "\\"
        EXPORT = open(filePath[:-1] + "_TRACKERexport.txt", "x")

        # write header to export file
        EXPORT.write("TRACKER DATA EXPORT for {}\n\n".format(CLIP.name))
        EXPORT.write("RANGE {} to {}\n\n".format(SCENE.frame_start, SCENE.frame_end))
        EXPORT.write("RESOLUTION {} x {}\n\n".format(CLIP.size[0], CLIP.size[1]))
        EXPORT.write("NUMBER OF TRACKS {}\n\n".format(len(TRACKER)))

        # export tracker coordinates
        cTrack = 0
        cMarker = 0
        while cTrack < len(TRACKER):
            EXPORT.write("\n##### {}\n".format(TRACKER[cTrack].name))
            cMarker = 0
            while cMarker < len(TRACKER[cTrack].markers):
                if TRACKER[cTrack].markers[cMarker].mute is not True: # check for valid track
                    EXPORT.write("{:05d} ".format(TRACKER[cTrack].markers[cMarker].frame))
                    EXPORT.write("{:6f} ".format(TRACKER[cTrack].markers[cMarker].co[0]))
                    EXPORT.write("{:6f}\n".format(TRACKER[cTrack].markers[cMarker].co[1]))
                cMarker = cMarker + 1
            cTrack = cTrack + 1

        # close export file
        EXPORT.close()

        return {"FINISHED"}
