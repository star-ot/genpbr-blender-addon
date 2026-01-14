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

            # Error Display Section
            if props.last_error_code > 0 or props.last_error_type:
                layout.separator()
                error_box = layout.box()
                error_box.label(text="Last Error:", icon='ERROR')

                # Display error code and type
                if props.last_error_type:
                    error_type_display = props.last_error_type
                    if error_type_display == "401":
                        error_box.label(text="401 Unauthorized", icon='LOCKED')
                        error_box.label(text="Invalid or missing API key", icon='INFO')
                        error_box.separator()
                        error_box.label(text="Solution:", icon='QUESTION')
                        error_box.label(text="Check your API key in:")
                        error_box.label(text="Edit > Preferences > Add-ons")
                        error_box.label(text="Find 'GenPBR Map Generator'")
                    elif error_type_display == "400":
                        error_box.label(text="400 Bad Request", icon='ERROR')
                        error_box.label(text="Invalid request or missing fields", icon='INFO')
                        error_box.separator()
                        error_box.label(text="Solution:", icon='QUESTION')
                        error_box.label(text="• Ensure a valid texture is selected")
                        error_box.label(text="• Check that at least one map type")
                        error_box.label(text="  is selected to generate")
                        if props.last_error_message:
                            error_box.separator()
                            error_box.label(text=f"Details: {props.last_error_message[:60]}...", icon='DOT')
                    elif error_type_display == "429":
                        error_box.label(text="429 Rate Limit Exceeded", icon='TIME')
                        error_box.label(text="Too many requests", icon='INFO')
                        error_box.separator()
                        error_box.label(text="Solution:", icon='QUESTION')
                        error_box.label(text="• Wait a moment before retrying")
                        error_box.label(text="• Check your rate limit above")
                        error_box.label(text="• Consider upgrading your plan")
                    elif error_type_display == "402":
                        error_box.label(text="402 Quota Exceeded", icon='CANCEL')
                        error_box.label(text="Monthly request limit reached", icon='INFO')
                        error_box.separator()
                        error_box.label(text="Solution:", icon='QUESTION')
                        error_box.label(text="• Upgrade your plan for more quota")
                        error_box.label(text="• Wait for next billing cycle")
                        error_box.label(text="• Check usage stats above")
                    elif error_type_display == "Network":
                        error_box.label(text="Network Error", icon='WORLD')
                        if props.last_error_message:
                            error_box.label(text=props.last_error_message[:60] + "...", icon='INFO')
                        error_box.separator()
                        error_box.label(text="Solution:", icon='QUESTION')
                        error_box.label(text="• Check your internet connection")
                        error_box.label(text="• Verify API endpoint is accessible")
                    elif error_type_display == "Unexpected":
                        error_box.label(text="Unexpected Error", icon='ERROR')
                        if props.last_error_message:
                            error_box.label(text=props.last_error_message[:60] + "...", icon='INFO')
                    else:
                        # Generic error display
                        if props.last_error_code > 0:
                            error_box.label(text=f"Error {props.last_error_code}", icon='ERROR')
                        if props.last_error_message:
                            error_box.label(text=props.last_error_message[:80], icon='INFO')

                # Show error message if available
                if props.last_error_message and props.last_error_type not in ["401", "400", "429", "402"]:
                    error_box.separator()
                    error_box.label(text="Details:", icon='DOT')
                    # Split long messages into multiple lines
                    msg_lines = props.last_error_message.split('\n')
                    for line in msg_lines[:3]:  # Show first 3 lines
                        if line.strip():
                            error_box.label(text=line.strip()[:70], icon='BLANK1')

            # Usage Stats Section
            if props.usage_monthly_quota > 0 or props.usage_tier or props.is_free_regeneration:
                layout.separator()
                usage_box = layout.box()
                usage_box.label(text="Usage Statistics:", icon='INFO')

                # Free regeneration status (show prominently)
                if props.is_free_regeneration:
                    usage_box.label(text="✓ Free Generation", icon='FREEZE')

                # Tier info
                if props.usage_tier:
                    tier_display = props.usage_tier.capitalize()
                    usage_box.label(text=f"Tier: {tier_display}", icon='USER')

                # Quota information
                if props.usage_monthly_quota > 0:
                    col = usage_box.column(align=True)
                    used = props.usage_monthly_quota - props.usage_remaining_quota
                    percentage = (used / props.usage_monthly_quota * 100) if props.usage_monthly_quota > 0 else 0

                    # Determine icon based on usage percentage
                    if percentage > 90:
                        quota_icon = 'ERROR'
                    elif percentage > 70:
                        quota_icon = 'QUESTION'
                    else:
                        quota_icon = 'CHECKMARK'

                    col.label(text=f"Quota: {used:,} / {props.usage_monthly_quota:,} ({percentage:.1f}%)", icon=quota_icon)
                    col.label(text=f"Remaining: {props.usage_remaining_quota:,}")

                # Rate limit
                if props.usage_rate_limit > 0:
                    usage_box.label(text=f"Rate Limit: {props.usage_rate_limit}/min", icon='TIME')

            # Info text
            layout.separator()
            info_box = layout.box()
            info_box.label(text="API Key: Configure in Add-on Preferences", icon='INFO')
            info_box.label(text="Location: Edit > Preferences > Add-ons", icon='PREFERENCES')
        except Exception as e:
            layout.label(text=f"Error drawing UI: {e}", icon='ERROR')
            import traceback
            traceback.print_exc()

