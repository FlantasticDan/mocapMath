from .cameraExport import CameraExporter
from .trackExport import TrackerExporter
from .solverImport import SolverImporter

import bpy

bl_info = {
    "name": "mocapMath Utility",
    "author": "Daniel Flanagan",
    "version": (0, 0, 1),
    "blender": (2, 80, 0),
    "description": "Utility to bridge Blender to mocapMath.",
    "warning": "BETA: Don't be suprised if it doesn't work.",
    "wiki_url": "https://github.com/FlantasticDan/mocapMath",
    "category": "Import-Export",
}

class mocapMathPanel(bpy.types.Panel):
    bl_idname = "UTILITY_PT_mocapMath"
    bl_label = "mocapMath Tools"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"

    def draw(self, context):
        layout = self.layout
        layout.operator("mocapmath.camera_export")
        layout.operator("mocapmath.track_export")
        layout.operator("mocapmath.solve_import")

# Registration
classes = (mocapMathPanel, CameraExporter, TrackerExporter, SolverImporter)
register, unregister = bpy.utils.register_classes_factory(classes)
