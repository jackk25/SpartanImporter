import bpy
from .authentication import authenticate
from .halo_connection import get_current_core, get_spartan_setup

class ImportSpartan(bpy.types.Operator):
    """Import your Spartan from Halo: Infinite"""

    bl_idname = "spartan.import"
    bl_label = "Import"
    bl_context = "VIEW_3D"
    
    def execute(self, context):
        spartan_token, xuid, clearance, headers = authenticate()
        inventory = get_current_core(headers, xuid, clearance)
        spartanSetup = get_spartan_setup(spartan_token, inventory)

        print(spartanSetup)

        return {"FINISHED"}