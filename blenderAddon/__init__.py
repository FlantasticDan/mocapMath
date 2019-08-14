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
    "warning": "[BETA] Dependent on external application, Windows 10 only.",
    "wiki_url": "https://github.com/FlantasticDan/mocapMath",
    "tracker_url": "https://github.com/FlantasticDan/mocapMath/issues",
    "category": "Import-Export",
}

class MocapSolver(bpy.types.Operator):
    bl_idname = "mocapmath.solver"
    bl_label = "Launch mocapMath Solver"
    bl_description = "This is an external application not contained within Blender."

    @classmethod
    def poll(cls, context):
        return False

    def execute(self, context):
        return {'FINISHED'}

class mocapMathPanel(bpy.types.Panel):
    bl_idname = "UTILITY_PT_mocapMath"
    bl_label = "mocapMath Utility"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"

    def draw(self, context):
        layout = self.layout

        layout.label(text="1) Export Data")
        layout.operator("mocapmath.camera_export")
        layout.operator("mocapmath.track_export")

        layout.label(text="2) Process Data")
        layout.operator("mocapmath.solver")

        layout.label(text="3) Import Solved Data")
        layout.operator("mocapmath.solve_import")

# Registration
classes = (mocapMathPanel, CameraExporter, TrackerExporter, SolverImporter, MocapSolver)
register, unregister = bpy.utils.register_classes_factory(classes)
