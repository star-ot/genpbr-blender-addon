bl_info = {
    "name": "GenPBR Map Generator",
    "author": "North Star Global LLC DBA GenPBR",
    "version": (1, 0, 6),
    "blender": (3, 6, 0),
    "location": "Shader Editor > Sidebar > GenPBR",
    "description": "Generate PBR maps from a base texture using GenPBR API. Connects to GenPBR API service to generate normal, metallic, roughness, and ambient occlusion maps from a single base texture image.",
    "category": "Material",
    "doc_url": "https://genpbr.com",
    "tracker_url": "",
    "support": "COMMUNITY",
    "license": "GPL-3.0-or-later",
}

import bpy

# Import addon modules
from . import preferences
from . import properties
from . import operators
from . import ui


# Register all classes
classes = [
    properties.GenPBRProperties,
    preferences.GenPBRPreferences,
    operators.PBRAutoLoadTextureOperator,
    operators.PBRSelectFileOperator,
    operators.PBRGenerateOperator,
    ui.PBRGeneratorPanel
]


def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    # Register scene properties
    bpy.types.Scene.genpbr_props = bpy.props.PointerProperty(type=properties.GenPBRProperties)


def unregister():
    # Unregister scene properties
    del bpy.types.Scene.genpbr_props

    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)


if __name__ == "__main__":
    register()
