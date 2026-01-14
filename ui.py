import bpy
import os

try:
    from . import utils
except ImportError:
    import utils

# Module-level variable to track scheduled auto-loads
_auto_load_scheduled = set()


class PBRGeneratorPanel(bpy.types.Panel):
    bl_label = "GenPBR Map Generator"
    bl_idname = "MATERIAL_PT_genpbr"
    bl_space_type = "NODE_EDITOR"
    bl_region_type = "UI"
    bl_category = "GenPBR"

    def draw(self, context):
        layout = self.layout

        try:
            props = context.scene.genpbr_props
        except Exception as e:
            layout.label(text=f"Error: Properties not initialized: {e}", icon='ERROR')
            import traceback
            traceback.print_exc()
            return

        # Check if object is selected
        obj = context.object
        if not obj:
            box = layout.box()
            box.label(text="Please select an object first", icon='ERROR')
            box.label(text="Select an object to auto-load texture from material", icon='INFO')
        else:
            # Auto-load base texture from material if not already set
            # Use timer to defer property update (can't modify properties in draw())
            if not props.base_texture_path and obj.active_material:
                # Check if we've already scheduled an auto-load for this object/material combo
                obj_id = f"{obj.name}_{obj.active_material.name if obj.active_material else 'none'}"

                if obj_id not in _auto_load_scheduled:
                    # Get texture path now (safe to do in draw)
                    texture_path = utils.get_base_texture_from_material(obj)

                    if texture_path and os.path.isfile(texture_path):
                        # Store scene name for safe access in timer
                        scene_name = context.scene.name

                        def update_texture_path():
                            try:
                                # Access scene by name to avoid context issues
                                scene = bpy.data.scenes.get(scene_name)
                                if scene and hasattr(scene, 'genpbr_props'):
                                    scene_props = scene.genpbr_props
                                    # Only set if still empty (user might have set it manually)
                                    if not scene_props.base_texture_path:
                                        scene_props.base_texture_path = texture_path
                            except Exception as e:
                                print(f"[GenPBR] Error in auto-load timer: {e}")
                            finally:
                                # Remove from scheduled set
                                _auto_load_scheduled.discard(obj_id)
                            return None  # Timer only runs once

                        # Schedule the update for next frame
                        _auto_load_scheduled.add(obj_id)
                        bpy.app.timers.register(update_texture_path, first_interval=0.01)

        # File Selection Section
        try:
            box = layout.box()
            box.label(text="Base Texture:", icon='TEXTURE')

            # Show selected file name or prompt
            if props.base_texture_path:
                file_name = os.path.basename(props.base_texture_path)
                if len(file_name) > 30:
                    file_name = file_name[:27] + "..."
                box.label(text=f"  {file_name}", icon='FILE_IMAGE')
            else:
                if obj and obj.active_material:
                    box.label(text="  No texture found in material", icon='ERROR')
                elif obj:
                    box.label(text="  No material assigned", icon='ERROR')
                else:
                    box.label(text="  Select an object first", icon='ERROR')

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

            # Disable button if no object, no material, or no file is selected
            if not obj:
                col.enabled = False
                col.operator("pbr.generate_maps", text="Select an Object First", icon='ERROR')
            elif not obj.active_material:
                col.enabled = False
                col.operator("pbr.generate_maps", text="Assign a Material First", icon='ERROR')
            elif not props.base_texture_path:
                col.enabled = False
                col.operator("pbr.generate_maps", text="No Texture Found", icon='ERROR')
            else:
                col.operator("pbr.generate_maps", text="Generate PBR Maps", icon='PLAY')

            # Info text
            layout.separator()
            info_box = layout.box()
            info_box.label(text="API Key: Configure in Add-on Preferences", icon='INFO')
            info_box.label(text="Location: Edit > Preferences > Add-ons", icon='PREFERENCES')
        except Exception as e:
            layout.label(text=f"Error drawing UI: {e}", icon='ERROR')
            import traceback
            traceback.print_exc()

