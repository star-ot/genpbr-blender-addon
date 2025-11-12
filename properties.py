import bpy


class GenPBRProperties(bpy.types.PropertyGroup):
    # File selection
    base_texture_path: bpy.props.StringProperty(
        name="Base Texture",
        description="Path to the base texture image",
        default="",
        subtype='FILE_PATH'
    )
    
    # Texture type toggles
    generate_normal: bpy.props.BoolProperty(
        name="Normal Map",
        description="Generate normal map for surface details",
        default=True
    )
    
    generate_metallic: bpy.props.BoolProperty(
        name="Metallic Map",
        description="Generate metallic map for metal/non-metal areas",
        default=True
    )
    
    generate_roughness: bpy.props.BoolProperty(
        name="Roughness Map",
        description="Generate roughness map for surface smoothness",
        default=True
    )
    
    generate_ao: bpy.props.BoolProperty(
        name="Ambient Occlusion (AO)",
        description="Generate AO map for shadowed crevices",
        default=True
    )
    
    # Intensity/strength sliders
    normal_strength: bpy.props.FloatProperty(
        name="Normal Strength",
        description="Strength of the normal map effect",
        default=5.0,
        min=0.0,
        max=10.0,
        step=10,
        precision=1
    )
    
    metallic_intensity: bpy.props.FloatProperty(
        name="Metallic Intensity",
        description="Intensity of metallic surface detection",
        default=0.8,
        min=0.0,
        max=2.0,
        step=1,
        precision=2
    )
    
    roughness_intensity: bpy.props.FloatProperty(
        name="Roughness Intensity",
        description="Intensity of roughness variation",
        default=2.0,
        min=0.0,
        max=5.0,
        step=10,
        precision=1
    )
    
    ao_intensity: bpy.props.FloatProperty(
        name="AO Intensity",
        description="Intensity of ambient occlusion shadows",
        default=2.0,
        min=0.0,
        max=5.0,
        step=10,
        precision=1
    )
    
    ao_radius: bpy.props.FloatProperty(
        name="AO Radius",
        description="Radius for AO calculation (larger = wider shadows)",
        default=12.0,
        min=1.0,
        max=30.0,
        step=10,
        precision=1
    )

