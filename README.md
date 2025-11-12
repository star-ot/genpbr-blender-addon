# GenPBR Map Generator - Blender Addon

A powerful Blender 3.6+ addon that generates high-quality PBR (Physically Based Rendering) texture maps from a single base texture using the GenPBR API. Create normal maps, metallic maps, roughness maps, and ambient occlusion maps with just a few clicks.

## Features

- **Generate Multiple PBR Maps**: Create normal, metallic, roughness, and ambient occlusion maps from a single base texture
- **Customizable Parameters**: Fine-tune generation settings for each map type
- **Automatic Material Setup**: Automatically creates and connects all texture maps to a Principled BSDF shader
- **Smart Image Compression**: Automatically compresses large images to meet API requirements
- **Progress Tracking**: Real-time progress indicator during generation
- **Easy-to-Use Interface**: Clean, intuitive UI in the Shader Editor sidebar

## Installation

1. Download the addon folder (`genpbr_addon`)
2. Open Blender (3.6 or later)
3. Go to `Edit > Preferences > Add-ons`
4. Click `Install...` and select the `genpbr_addon` folder
5. Enable the addon by checking the box next to "GenPBR Map Generator"

## Getting an API Key

### Option 1: Web Version (Recommended for Unlimited Use)

The **web version at [https://genpbr.com](https://genpbr.com) offers unlimited usage** without any restrictions. If you prefer unlimited access and don't need API integration, you can use the web interface directly.

### Option 2: API Key (For Blender Addon Integration)

To use this Blender addon, you'll need an API key:

1. Visit [https://genpbr.com](https://genpbr.com)
2. Sign up for an account
3. Navigate to your account settings or API section
4. Generate or copy your API key
5. In Blender, go to `Edit > Preferences > Add-ons > GenPBR Map Generator`
6. Paste your API key in the "API Key" field

**Note**: The free tier for API usage has usage limits. For unlimited API access, consider upgrading to a paid plan. The web version remains free and unlimited.

## Usage

### Basic Workflow

1. **Open the Shader Editor**: Switch to the Shader Editor workspace or open a Shader Editor window
2. **Open the GenPBR Panel**: Look for the "GenPBR" tab in the sidebar (press `N` if the sidebar isn't visible)
3. **Select a Base Texture**: 
   - Click "Select Base Texture"
   - Choose your base texture image file (PNG, JPG, etc.)
4. **Choose Texture Types**: Toggle which maps you want to generate:
   - Normal Map
   - Metallic Map
   - Roughness Map
   - Ambient Occlusion (AO)
5. **Adjust Parameters** (optional): Fine-tune the generation settings for each enabled map type
6. **Generate**: Click "Generate PBR Maps" and wait for the process to complete

### Parameter Settings

#### Normal Map
- **Normal Strength** (0.0 - 10.0): Controls the intensity of surface detail. Higher values create more pronounced normal map effects.

#### Metallic Map
- **Metallic Intensity** (0.0 - 2.0): Adjusts how strongly metallic surfaces are detected. Higher values make metal detection more aggressive.

#### Roughness Map
- **Roughness Intensity** (0.0 - 5.0): Controls the variation in surface smoothness. Higher values create more contrast between smooth and rough areas.

#### Ambient Occlusion
- **AO Intensity** (0.0 - 5.0): Controls the strength of shadowed areas in crevices and corners
- **AO Radius** (1.0 - 30.0): Determines the size of the shadow areas. Larger values create wider shadows.

### Material Setup

The addon automatically:
- Creates a new material if none exists on the active object
- Sets up a Principled BSDF shader
- Connects the base texture as the albedo/base color
- Connects all generated maps to their appropriate inputs
- Properly configures color space settings (sRGB for color maps, Non-Color for data maps)
- Connects AO to multiply with the base color for realistic shadowing

## Supported Image Formats

- PNG
- JPEG/JPG
- BMP
- TIFF/TIF

**Note**: Images larger than 5MB will be automatically compressed and resized to a maximum of 2048x2048 pixels to meet API requirements.

## Requirements

- **Blender**: 3.6 or later
- **Python Libraries**: 
  - `requests` (usually included with Blender)
  - `PIL/Pillow` (optional, for faster image compression - will fall back to Blender's built-in image processing if not available)

## Troubleshooting

### "Please enter your API key" Error
- Make sure you've entered your API key in the addon preferences
- Go to `Edit > Preferences > Add-ons > GenPBR Map Generator` and paste your API key

### "API request failed" Error
- Check your internet connection
- Verify your API key is correct and active
- Check if you've exceeded your API usage limits (free tier has limits)
- Try using the web version at [https://genpbr.com](https://genpbr.com) for unlimited usage

### Image Not Loading
- Ensure the file path is valid and the image file exists
- Check that the image format is supported
- Try using a different image file

### Material Not Created
- Make sure you have an object selected in the 3D viewport
- The addon will create a material if none exists, but requires an active object

## API Usage Limits

**Important**: The free tier for API usage has usage limits. For details on:
- Current usage limits
- Upgrade options for higher limits
- Unlimited API access plans

Please visit [https://genpbr.com](https://genpbr.com) and check your account settings or contact support.

**Alternative**: Use the web version at [https://genpbr.com](https://genpbr.com) for unlimited, free usage without any restrictions.

## Technical Details

### File Structure
```
genpbr_addon/
├── __init__.py      # Main entry point and registration
├── preferences.py   # Addon preferences (API key storage)
├── properties.py    # Scene properties (UI state)
├── operators.py     # Operators (file selection, generation)
├── ui.py            # UI panel
└── utils.py         # Utility functions (image compression)
```

### How It Works

1. The addon reads your selected base texture
2. Compresses/resizes if necessary to meet API requirements
3. Encodes the image to base64
4. Sends a request to the GenPBR API with your selected options
5. Receives generated texture maps as base64-encoded images
6. Decodes and saves maps to temporary files
7. Loads maps into Blender and sets up the material node tree
8. Connects all maps to the Principled BSDF shader

## License

Copyright © North Star Global LLC DBA GenPBR

## Support

For issues, questions, or feature requests:
- Visit [https://genpbr.com](https://genpbr.com)
- Check the web version for unlimited usage
- Contact GenPBR support through their website
- [GenPBR Changelog](https://genpbr.com/changelog)

---

**Made with ❤️ by North Star Global LLC DBA GenPBR**

