import bpy
import os


class PBRGeneratorPanel(bpy.types.Panel):
    bl_label = "GenPBR Map Generator"
    bl_idname = "MATERIAL_PT_genpbr"
    bl_space_type = "NODE_EDITOR"
    bl_region_type = "UI"
    bl_category = "GenPBR"

    def draw(self, context):
        layout = self.layout
        props = context.scene.genpbr_props
        
        # File Selection Section
        box = layout.box()
        box.label(text="Base Texture:", icon='TEXTURE')
        
        # Show selected file name or prompt
        if props.base_texture_path:
            file_name = os.path.basename(props.base_texture_path)
            if len(file_name) > 30:
                file_name = file_name[:27] + "..."
            box.label(text=f"  {file_name}", icon='FILE_IMAGE')
        else:
            box.label(text="  No file selected", icon='ERROR')
        
        # File select button
        box.operator("pbr.select_file", text="Select Base Texture", icon='FILEBROWSER')
        
        # Separator
        layout.separator()
        
        # Texture Types Section
        box = layout.box()
        box.label(text="Texture Maps to Generate:", icon='NODE_TEXTURE')
        
        col = box.column(align=True)
        col.prop(props, "generate_normal", text="Normal Map", toggle=True)
        col.prop(props, "generate_metallic", text="Metallic Map", toggle=True)
        col.prop(props, "generate_roughness", text="Roughness Map", toggle=True)
        col.prop(props, "generate_ao", text="Ambient Occlusion (AO)", toggle=True)
        
        # Separator
        layout.separator()
        
        # Parameters Section
        box = layout.box()
        box.label(text="Generation Parameters:", icon='SETTINGS')
        
        # Normal strength slider
        if props.generate_normal:
            col = box.column(align=True)
            col.label(text="Normal Map:")
            col.prop(props, "normal_strength", slider=True)
            col.separator(factor=0.5)
        
        # Metallic intensity slider
        if props.generate_metallic:
            col = box.column(align=True)
            col.label(text="Metallic Map:")
            col.prop(props, "metallic_intensity", slider=True)
            col.separator(factor=0.5)
        
        # Roughness intensity slider
        if props.generate_roughness:
            col = box.column(align=True)
            col.label(text="Roughness Map:")
            col.prop(props, "roughness_intensity", slider=True)
            col.separator(factor=0.5)
        
        # AO parameters sliders
        if props.generate_ao:
            col = box.column(align=True)
            col.label(text="Ambient Occlusion:")
            col.prop(props, "ao_intensity", slider=True)
            col.prop(props, "ao_radius", slider=True)
        
        # Separator
        layout.separator()
        
        # Generate Button (big and prominent)
        col = layout.column()
        col.scale_y = 1.5
        
        # Disable button if no file is selected
        if not props.base_texture_path:
            col.enabled = False
            col.operator("pbr.generate_maps", text="Select a File First", icon='ERROR')
        else:
            col.operator("pbr.generate_maps", text="Generate PBR Maps", icon='PLAY')
        
        # Info text
        layout.separator()
        info_box = layout.box()
        info_box.label(text="API Key: Configure in Add-on Preferences", icon='INFO')
        info_box.label(text="Location: Edit > Preferences > Add-ons", icon='PREFERENCES')

