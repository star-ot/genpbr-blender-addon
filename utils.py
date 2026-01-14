import os
import tempfile
from io import BytesIO
import bpy

# Try to import PIL for faster image processing
try:
    from PIL import Image
    HAS_PIL = True
except ImportError:
    HAS_PIL = False
    print("[GenPBR] PIL not available, using Blender for image compression (slower)")


def _extract_image_from_node(node):
    """
    Extract image filepath from an image texture node.

    Args:
        node: Blender image texture node

    Returns:
        str: File path to the image, or None if not found
    """
    if not node or node.type != 'TEX_IMAGE' or not node.image:
        return None

    image = node.image
    # Check if image has a filepath (not packed)
    if image.filepath and image.filepath != "":
        # Convert relative path to absolute
        if image.filepath.startswith("//"):
            # Relative path - convert to absolute
            blend_filepath = bpy.data.filepath
            if blend_filepath:
                blend_dir = os.path.dirname(blend_filepath)
                return os.path.abspath(os.path.join(blend_dir, image.filepath[2:]))
            else:
                # File not saved, can't resolve relative path
                return None
        else:
            # Already absolute path
            return os.path.abspath(bpy.path.abspath(image.filepath))
    elif image.packed_file:
        # Image is packed - save to temp file
        temp_path = os.path.join(tempfile.gettempdir(), f"genpbr_temp_{image.name}.png")
        try:
            # Use filepath_raw and save() for packed images
            original_path = image.filepath_raw
            image.filepath_raw = temp_path
            image.save()
            image.filepath_raw = original_path
            return temp_path
        except Exception as e:
            print(f"[GenPBR] Failed to save packed image: {e}")
            return None

    return None


def _find_image_texture_recursive(node, visited=None, max_depth=10, depth=0):
    """
    Recursively search for an image texture node in the node tree.

    Args:
        node: Starting node to search from
        visited: Set of visited nodes to avoid cycles
        max_depth: Maximum recursion depth
        depth: Current recursion depth

    Returns:
        str: File path to the image, or None if not found
    """
    if visited is None:
        visited = set()

    if max_depth <= 0 or node in visited:
        return None

    visited.add(node)

    indent = "  " * depth
    print(f"{indent}[GenPBR] Checking node: {node.type} - {node.name} (depth {depth})")

    # If this is an image texture node, extract the image
    if node.type == 'TEX_IMAGE':
        print(f"{indent}[GenPBR] Found TEX_IMAGE node!")
        return _extract_image_from_node(node)

    # Search through inputs of the node
    if not hasattr(node, 'inputs'):
        return None

    # For mix nodes, prioritize Color1 (usually the base texture)
    if node.type == 'MIX_RGB':
        color1_input = node.inputs.get('Color1')
        if color1_input and color1_input.is_linked:
            for link in color1_input.links:
                result = _find_image_texture_recursive(link.from_node, visited, max_depth - 1, depth + 1)
                if result:
                    return result
        # Also check Color2 as fallback
        color2_input = node.inputs.get('Color2')
        if color2_input and color2_input.is_linked:
            for link in color2_input.links:
                result = _find_image_texture_recursive(link.from_node, visited, max_depth - 1, depth + 1)
                if result:
                    return result
    else:
        # For other nodes, check all color/vector inputs
        # Prioritize common color input names
        priority_inputs = ['Color', 'Image', 'Base Color', 'Albedo', 'Diffuse']
        for input_name in priority_inputs:
            input_socket = node.inputs.get(input_name)
            if input_socket and input_socket.is_linked:
                for link in input_socket.links:
                    result = _find_image_texture_recursive(link.from_node, visited, max_depth - 1, depth + 1)
                    if result:
                        return result

        # Check all other color/vector inputs
        for input_socket in node.inputs:
            if input_socket.name in priority_inputs:
                continue  # Already checked
            if (input_socket.type == 'RGBA' or input_socket.type == 'VECTOR') and input_socket.is_linked:
                for link in input_socket.links:
                    result = _find_image_texture_recursive(link.from_node, visited, max_depth - 1, depth + 1)
                    if result:
                        return result

    return None


def get_base_texture_from_material(obj):
    """
    Extract the base texture (albedo/diffuse) from an object's active material.

    Args:
        obj: Blender object with a material

    Returns:
        str: File path to the base texture, or None if not found
    """
    if not obj or not obj.active_material:
        print("[GenPBR] No object or no active material")
        return None

    mat = obj.active_material
    if not mat.use_nodes:
        print("[GenPBR] Material does not use nodes")
        return None

    node_tree = mat.node_tree
    if not node_tree:
        print("[GenPBR] No node tree")
        return None

    # Find the Principled BSDF node (or similar output node)
    bsdf_node = None
    for node in node_tree.nodes:
        if node.type == 'BSDF_PRINCIPLED':
            bsdf_node = node
            break

    if not bsdf_node:
        print("[GenPBR] No Principled BSDF node found")
        return None

    # Try to find texture connected to Base Color input
    base_color_input = bsdf_node.inputs.get('Base Color')
    if not base_color_input:
        print("[GenPBR] No Base Color input found on BSDF")
        return None

    # Follow the connection to find the image texture
    if not base_color_input.is_linked:
        print("[GenPBR] Base Color input is not linked")
        return None

    link = base_color_input.links[0]
    from_node = link.from_node
    print(f"[GenPBR] Base Color connected to: {from_node.type} - {from_node.name}")

    # Recursively search for image texture node
    image_path = _find_image_texture_recursive(from_node)
    if image_path:
        print(f"[GenPBR] Found image texture: {image_path}")
        return image_path
    else:
        print("[GenPBR] No image texture found in node tree")
        return None


def compress_image_if_needed(filepath, max_size_bytes=5 * 1024 * 1024):
    """
    Compress an image if it exceeds the maximum size.

    Args:
        filepath: Path to the image file
        max_size_bytes: Maximum file size in bytes (default: 5MB)

    Returns:
        tuple: (image_data: bytes, mime_type: str)
    """
    import bpy

    # Read original file
    with open(filepath, "rb") as img_file:
        image_data = img_file.read()

    original_size = len(image_data)

    # If file is small enough, return as-is
    if original_size <= max_size_bytes:
        file_ext = os.path.splitext(filepath)[1].lower()
        mime_types = {
            '.png': 'image/png',
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.bmp': 'image/bmp',
            '.tiff': 'image/tiff',
            '.tif': 'image/tiff',
        }
        mime_type = mime_types.get(file_ext, 'image/png')
        return image_data, mime_type

    # File is too large, compress it
    print(f"[GenPBR Debug] Image too large ({original_size / 1024 / 1024:.2f}MB), compressing...")

    if HAS_PIL:
        # Fast compression using PIL
        img = Image.open(filepath)

        # Calculate new dimensions (maintain aspect ratio, max 2048x2048)
        width, height = img.size
        max_dimension = 2048

        if width > max_dimension or height > max_dimension:
            scale = max_dimension / max(width, height)
            new_width = int(width * scale)
            new_height = int(height * scale)
            img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
            print(f"[GenPBR Debug] Resized from {width}x{height} to {new_width}x{new_height}")

        # Convert to RGB if necessary
        if img.mode in ('RGBA', 'LA', 'P'):
            background = Image.new('RGB', img.size, (255, 255, 255))
            if img.mode == 'P':
                img = img.convert('RGBA')
            background.paste(img, mask=img.split()[-1] if img.mode in ('RGBA', 'LA') else None)
            img = background
        elif img.mode != 'RGB':
            img = img.convert('RGB')

        # Save to bytes (JPEG is faster and smaller)
        output = BytesIO()
        img.save(output, format='JPEG', quality=90, optimize=True)
        image_data = output.getvalue()
        output.close()

        mime_type = 'image/jpeg'

    else:
        # Fallback to Blender (slower)
        temp_img = bpy.data.images.load(filepath)

        width, height = temp_img.size
        max_dimension = 2048

        if width > max_dimension or height > max_dimension:
            scale = max_dimension / max(width, height)
            new_width = int(width * scale)
            new_height = int(height * scale)
            temp_img.scale(new_width, new_height)

        temp_path = os.path.join(tempfile.gettempdir(), "genpbr_temp_compressed.png")
        temp_img.filepath_raw = temp_path
        temp_img.file_format = 'PNG'
        temp_img.save()

        with open(temp_path, "rb") as f:
            image_data = f.read()

        bpy.data.images.remove(temp_img)
        try:
            os.remove(temp_path)
        except:
            pass

        mime_type = 'image/png'

    print(f"[GenPBR Debug] Compressed size: {len(image_data) / 1024 / 1024:.2f}MB")
    return image_data, mime_type

