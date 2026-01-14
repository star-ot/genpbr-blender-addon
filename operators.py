import bpy
import requests
import os
import base64
import tempfile

try:
    from . import utils
except ImportError:
    # Handle case when running as standalone module
    import utils


class PBRAutoLoadTextureOperator(bpy.types.Operator):
    bl_idname = "pbr.auto_load_texture"
    bl_label = "Auto-load Texture"
    bl_description = "Automatically load texture from material"
    bl_options = {'INTERNAL'}

    texture_path: bpy.props.StringProperty()

    def execute(self, context):
        props = context.scene.genpbr_props
        if self.texture_path and os.path.isfile(self.texture_path):
            props.base_texture_path = self.texture_path
        return {'FINISHED'}


class PBRSelectFileOperator(bpy.types.Operator):
    bl_idname = "pbr.select_file"
    bl_label = "Select Base Texture"
    bl_description = "Choose a base texture image file"

    filepath: bpy.props.StringProperty(subtype="FILE_PATH")
    filter_image: bpy.props.BoolProperty(default=True, options={'HIDDEN'})
    filter_folder: bpy.props.BoolProperty(default=True, options={'HIDDEN'})

    def execute(self, context):
        props = context.scene.genpbr_props
        props.base_texture_path = self.filepath
        self.report({'INFO'}, f"Selected: {os.path.basename(self.filepath)}")
        return {'FINISHED'}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}


class PBRGenerateOperator(bpy.types.Operator):
    bl_idname = "pbr.generate_maps"
    bl_label = "Generate PBR Maps"
    bl_description = "Generate PBR maps from selected base texture using GenPBR API"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        props = context.scene.genpbr_props
        addon_name = __name__.split('.')[0]
        prefs = bpy.context.preferences.addons[addon_name].preferences
        api_key = prefs.api_key.strip() if prefs.api_key else ""

        # Initialize progress indicator
        wm = context.window_manager
        wm.progress_begin(0, 100)

        try:
            # Check if object is selected
            if not context.object:
                self.report({'ERROR'}, "Please select an object first")
                wm.progress_end()
                return {'CANCELLED'}

            # Auto-load base texture from material if not already set
            if not props.base_texture_path and context.object.active_material:
                texture_path = utils.get_base_texture_from_material(context.object)
                if texture_path and os.path.isfile(texture_path):
                    props.base_texture_path = texture_path

            # Debug: Print API key info (first 10 and last 4 chars for security)
            print(f"[GenPBR Debug] API Key length: {len(api_key)}")
            if api_key:
                print(f"[GenPBR Debug] API Key preview: {api_key[:10]}...{api_key[-4:]}")
            else:
                print("[GenPBR Debug] API Key is empty!")

            if not api_key:
                self.report({'ERROR'}, "Please enter your API key in the Add-on preferences")
                wm.progress_end()
                return {'CANCELLED'}

            if not props.base_texture_path or not os.path.isfile(props.base_texture_path):
                self.report({'ERROR'}, "Please select a valid base texture file first, or assign a material with a texture to the selected object")
                wm.progress_end()
                return {'CANCELLED'}

            # Build texture types list based on toggles
            texture_types = []
            if props.generate_normal:
                texture_types.append("normal")
            if props.generate_metallic:
                texture_types.append("metallic")
            if props.generate_roughness:
                texture_types.append("roughness")
            if props.generate_ao:
                texture_types.append("ao")

            if not texture_types:
                self.report({'ERROR'}, "Please select at least one texture type to generate")
                wm.progress_end()
                return {'CANCELLED'}

            wm.progress_update(5)

            # Read and encode image to base64
            try:
                image_data, mime_type = utils.compress_image_if_needed(props.base_texture_path)
                base64_image = base64.b64encode(image_data).decode('utf-8')

            except Exception as e:
                self.report({'ERROR'}, f"Failed to read image file: {e}")
                wm.progress_end()
                return {'CANCELLED'}

            wm.progress_update(10)

            # Prepare API request
            url = "https://genpbr.com/api/v1/generate-texture"

            # Try lowercase header name first (some servers are case-sensitive)
            headers = {
                "x-api-key": api_key.strip(),
                "Content-Type": "application/json"
            }

            # Debug: Print request details
            print(f"[GenPBR Debug] URL: {url}")
            print(f"[GenPBR Debug] Headers: {list(headers.keys())}")
            print(f"[GenPBR Debug] Header 'x-api-key' value length: {len(headers['x-api-key'])}")
            print(f"[GenPBR Debug] Image size: {len(image_data)} bytes")
            print(f"[GenPBR Debug] Base64 length: {len(base64_image)} chars")
            print(f"[GenPBR Debug] Texture types: {texture_types}")

            # Use user-configured options
            payload = {
                "baseImage": f"data:{mime_type};base64,{base64_image}",
                "textureTypes": texture_types,
                "options": {
                    "normalStrength": props.normal_strength,
                    "metallicIntensity": props.metallic_intensity,
                    "roughnessIntensity": props.roughness_intensity,
                    "aoIntensity": props.ao_intensity,
                    "aoRadius": props.ao_radius
                }
            }

            wm.progress_update(15)

            try:
                print("[GenPBR Debug] Sending API request...")
                response = requests.post(url, json=payload, headers=headers, timeout=120)

                # Debug: Print response details
                print(f"[GenPBR Debug] Response status: {response.status_code}")
                print(f"[GenPBR Debug] Response headers: {dict(response.headers)}")

                response.raise_for_status()

            except requests.exceptions.HTTPError as e:
                error_msg = f"API request failed: {e}"
                print(f"[GenPBR Debug] HTTP Error: {e}")
                print(f"[GenPBR Debug] Response status code: {response.status_code}")

                try:
                    error_data = response.json()
                    print(f"[GenPBR Debug] Full error response: {error_data}")

                    # Build detailed error message
                    if "message" in error_data:
                        error_msg = f"API error: {error_data['message']}"
                    if "error" in error_data:
                        error_msg = f"{error_data.get('error', 'Unknown error')}: {error_data.get('message', '')}"
                    if "debug" in error_data:
                        print(f"[GenPBR Debug] Server debug info: {error_data['debug']}")

                except Exception as json_error:
                    print(f"[GenPBR Debug] Failed to parse error JSON: {json_error}")
                    print(f"[GenPBR Debug] Raw response text: {response.text[:500]}")

                self.report({'ERROR'}, error_msg)
                wm.progress_end()
                return {'CANCELLED'}
            except requests.exceptions.RequestException as e:
                print(f"[GenPBR Debug] Request exception: {e}")
                self.report({'ERROR'}, f"API request failed: {e}")
                wm.progress_end()
                return {'CANCELLED'}
            except Exception as e:
                print(f"[GenPBR Debug] Unexpected error: {type(e).__name__}: {e}")
                import traceback
                print(f"[GenPBR Debug] Traceback: {traceback.format_exc()}")
                self.report({'ERROR'}, f"API request failed: {e}")
                wm.progress_end()
                return {'CANCELLED'}

            wm.progress_update(30)

            # Parse response
            try:
                print("[GenPBR Debug] Parsing response...")
                data = response.json()
                print(f"[GenPBR Debug] Response keys: {list(data.keys())}")

                if not data.get("success", False):
                    error_msg = data.get("message", "Unknown error")
                    print(f"[GenPBR Debug] API returned error: {error_msg}")
                    print(f"[GenPBR Debug] Full response data: {data}")
                    self.report({'ERROR'}, f"API returned error: {error_msg}")
                    wm.progress_end()
                    return {'CANCELLED'}

                textures = data.get("textures", {})
                print(f"[GenPBR Debug] Received texture types: {list(textures.keys())}")

                if "metadata" in data:
                    print(f"[GenPBR Debug] Metadata: {data['metadata']}")
                if "usage" in data:
                    print(f"[GenPBR Debug] Usage info: {data['usage']}")

            except Exception as e:
                print(f"[GenPBR Debug] Failed to parse response: {e}")
                print(f"[GenPBR Debug] Response text: {response.text[:500]}")
                self.report({'ERROR'}, f"Failed to parse API response: {e}")
                wm.progress_end()
                return {'CANCELLED'}

            wm.progress_update(40)

            # Batch decode all textures to temp files first (faster I/O)
            temp_dir = tempfile.gettempdir()
            temp_files = {}

            try:
                for tex_type, data_url in textures.items():
                    # Extract and decode base64 data
                    if data_url.startswith('data:'):
                        base64_data = data_url.split(',', 1)[1]
                    else:
                        base64_data = data_url

                    image_bytes = base64.b64decode(base64_data)
                    temp_path = os.path.join(temp_dir, f"genpbr_{tex_type}.png")

                    # Write all files in batch
                    with open(temp_path, "wb") as f:
                        f.write(image_bytes)

                    temp_files[tex_type] = temp_path

            except Exception as e:
                self.report({'WARNING'}, f"Failed to decode textures: {e}")

            wm.progress_update(60)

            # Download maps and apply to active material
            mat = context.object.active_material
            if not mat:
                mat = bpy.data.materials.new(name="GenPBR_Material")
                context.object.active_material = mat
            mat.use_nodes = True
            nodes = mat.node_tree.nodes
            links = mat.node_tree.links

            # Clear existing nodes
            nodes.clear()

            # Create Principled BSDF
            output_node = nodes.new(type='ShaderNodeOutputMaterial')
            output_node.location = (400, 0)
            bsdf_node = nodes.new(type='ShaderNodeBsdfPrincipled')
            bsdf_node.location = (0, 0)
            links.new(bsdf_node.outputs['BSDF'], output_node.inputs['Surface'])

            # Load base image as albedo (since API doesn't return albedo separately)
            albedo_node = None
            try:
                base_img = bpy.data.images.load(props.base_texture_path)
                base_img.name = "Albedo"
                base_img.colorspace_settings.name = 'sRGB'
                # Pack image into blend file for undo safety
                base_img.pack()
                albedo_node = nodes.new('ShaderNodeTexImage')
                albedo_node.image = base_img
                albedo_node.label = "Albedo"
                albedo_node.location = (-400, 0)
                links.new(albedo_node.outputs['Color'], bsdf_node.inputs['Base Color'])
            except Exception as e:
                self.report({'WARNING'}, f"Failed to load base image as albedo: {e}")

            # Track y position for node placement (200 units spacing)
            y = -200

            # Load AO map and connect it to multiply with base color
            if "ao" in temp_files:
                try:
                    img = bpy.data.images.load(temp_files["ao"])
                    img.name = "Ambient Occlusion"
                    img.colorspace_settings.name = 'Non-Color'
                    # Pack image into blend file for undo safety
                    img.pack()

                    ao_node = nodes.new('ShaderNodeTexImage')
                    ao_node.image = img
                    ao_node.label = "Ambient Occlusion"
                    ao_node.location = (-400, y)

                    # Create a MixRGB node to multiply AO with the base color
                    mix_node = nodes.new(type='ShaderNodeMixRGB')
                    mix_node.blend_type = 'MULTIPLY'
                    mix_node.location = (-200, y)
                    mix_node.inputs['Fac'].default_value = 1.0

                    # Reconnect albedo through the mix node if albedo exists
                    if albedo_node:
                        # Remove existing albedo to BSDF link
                        for link in list(links):
                            if link.to_socket == bsdf_node.inputs['Base Color']:
                                links.remove(link)
                                break

                        # Connect albedo and AO through mix node
                        links.new(albedo_node.outputs['Color'], mix_node.inputs['Color1'])
                        links.new(ao_node.outputs['Color'], mix_node.inputs['Color2'])
                        links.new(mix_node.outputs['Color'], bsdf_node.inputs['Base Color'])
                    else:
                        # If no albedo, just connect AO directly (though this is unusual)
                        links.new(ao_node.outputs['Color'], bsdf_node.inputs['Base Color'])

                    y -= 200
                except Exception as e:
                    self.report({'WARNING'}, f"Failed to load AO map: {e}")

            # Load metallic map
            if "metallic" in temp_files:
                try:
                    img = bpy.data.images.load(temp_files["metallic"])
                    img.name = "Metallic"
                    img.colorspace_settings.name = 'Non-Color'
                    # Pack image into blend file for undo safety
                    img.pack()

                    node = nodes.new('ShaderNodeTexImage')
                    node.image = img
                    node.label = "Metallic"
                    node.location = (-400, y)
                    links.new(node.outputs['Color'], bsdf_node.inputs['Metallic'])
                    y -= 200
                except Exception as e:
                    self.report({'WARNING'}, f"Failed to load metallic map: {e}")

            # Load roughness map
            if "roughness" in temp_files:
                try:
                    img = bpy.data.images.load(temp_files["roughness"])
                    img.name = "Roughness"
                    img.colorspace_settings.name = 'Non-Color'
                    # Pack image into blend file for undo safety
                    img.pack()

                    node = nodes.new('ShaderNodeTexImage')
                    node.image = img
                    node.label = "Roughness"
                    node.location = (-400, y)
                    links.new(node.outputs['Color'], bsdf_node.inputs['Roughness'])
                    y -= 200
                except Exception as e:
                    self.report({'WARNING'}, f"Failed to load roughness map: {e}")

            # Load normal map
            if "normal" in temp_files:
                try:
                    img = bpy.data.images.load(temp_files["normal"])
                    img.name = "Normal Map"
                    img.colorspace_settings.name = 'Non-Color'
                    # Pack image into blend file for undo safety
                    img.pack()

                    node = nodes.new('ShaderNodeTexImage')
                    node.image = img
                    node.label = "Normal Map"
                    node.location = (-400, y)

                    normal_node = nodes.new(type='ShaderNodeNormalMap')
                    normal_node.location = (-200, y)
                    links.new(node.outputs['Color'], normal_node.inputs['Color'])
                    links.new(normal_node.outputs['Normal'], bsdf_node.inputs['Normal'])
                    y -= 200
                except Exception as e:
                    self.report({'WARNING'}, f"Failed to load normal map: {e}")

            wm.progress_update(100)
            self.report({'INFO'}, "PBR maps generated successfully!")
            wm.progress_end()
            return {'FINISHED'}

        except Exception as e:
            # Catch any unexpected errors and ensure progress bar is closed
            print(f"[GenPBR Debug] Unexpected error in execute: {type(e).__name__}: {e}")
            import traceback
            print(f"[GenPBR Debug] Traceback: {traceback.format_exc()}")
            self.report({'ERROR'}, f"Unexpected error: {e}")
            wm.progress_end()
            return {'CANCELLED'}

