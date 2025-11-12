import bpy


class GenPBRPreferences(bpy.types.AddonPreferences):
    # Get the root package name (addon name)
    bl_idname = __name__.split('.')[0] if '.' in __name__ else __name__

    api_key: bpy.props.StringProperty(
        name="API Key",
        description="Your GenPBR API key",
        default="",
        subtype='PASSWORD'
    )

    def draw(self, context):
        layout = self.layout
        layout.label(text="Enter your GenPBR API key:")
        layout.prop(self, "api_key")

