bl_info = {
    "name": "Spartan Importer",
    "author": "jackk25",
    "version": (1, 0, 0),
    "blender": (4, 0, 0),
    "category": "3D View",
    "location": "3D View > Sidebar > Spartan Importer",
    "description": "Import your currently equipped Spartan into Halo Infinite",
}

import bpy
from .src.operators import *
from .src.ui_panels import *

classes = [
    ImportSpartan,
    SPRTN_PT_Import,
]

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.Scene.spartan_core_source = bpy.props.PointerProperty(type=bpy.types.Collection)


def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)

    del bpy.types.Scene.spartan_core_source

if __name__ == "__main__":
    register()
