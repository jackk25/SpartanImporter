import bpy
from bpy.types import Panel
from .operators import ImportSpartan

class SPRTN_Panel:
    bl_category = "Spartan Importer"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"

class SPRTN_PT_Import(SPRTN_Panel, Panel):
    bl_label = "Import"

    def draw(self, context):
        layout = self.layout
        
        row = layout.row()
        row.operator(ImportSpartan.bl_idname, icon="IMPORT", text="Import")

        row = layout.row()
        row.prop(context.scene, "spartan_core_source", text="Cores")