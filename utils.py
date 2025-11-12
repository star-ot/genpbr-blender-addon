import os
import tempfile
from io import BytesIO

# Try to import PIL for faster image processing
try:
    from PIL import Image
    HAS_PIL = True
except ImportError:
    HAS_PIL = False
    print("[GenPBR] PIL not available, using Blender for image compression (slower)")


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

