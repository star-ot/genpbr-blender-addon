#!/bin/bash
# Bash script to create a release zip for GitHub
# Usage: ./create_release.sh [version]

VERSION=${1:-"1.0.0"}
ADDON_NAME="genpbr_blender_addon"
ZIP_NAME="${ADDON_NAME}_v${VERSION}.zip"

echo "Creating release zip: $ZIP_NAME"

# Remove old zip if exists
if [ -f "$ZIP_NAME" ]; then
    rm "$ZIP_NAME"
    echo "Removed existing zip file"
fi

# Create zip file with all addon files
zip -r "$ZIP_NAME" \
    __init__.py \
    preferences.py \
    properties.py \
    operators.py \
    ui.py \
    utils.py \
    README.md \
    -x "*.git*" "*.DS_Store" "*__pycache__*"

echo ""
echo "Release zip created successfully: $ZIP_NAME"
echo "File size: $(du -h "$ZIP_NAME" | cut -f1)"

