# GitHub Release Guide

This guide will help you publish the GenPBR Map Generator addon as a GitHub release with a downloadable zip file.

## Prerequisites

- GitHub account
- Git installed on your system
- GitHub CLI (`gh`) installed (optional, but recommended) OR access to GitHub web interface

## Step 1: Create the Release Zip

The release zip has already been created. You can recreate it anytime with:

**Windows (PowerShell):**
```powershell
.\create_release.ps1 [version]
```

**Linux/Mac:**
```bash
chmod +x create_release.sh
./create_release.sh [version]
```

**Example:**
```powershell
.\create_release.ps1 1.0.0
```

This creates: `genpbr_blender_addon_v1.0.0.zip`

## Step 2: Create GitHub Repository

### Option A: Using GitHub CLI (Recommended)

1. Install GitHub CLI if not already installed: https://cli.github.com/

2. Authenticate:
```bash
gh auth login
```

3. Create the repository and push:
```bash
# Create public repository
gh repo create genpbr-blender-addon --public --source=. --remote=origin --description "Blender 3.6+ addon for generating PBR maps using GenPBR API"

# Push code
git branch -M main
git push -u origin main
```

### Option B: Using GitHub Web Interface

1. Go to https://github.com/new
2. Repository name: `genpbr-blender-addon` (or your preferred name)
3. Description: "Blender 3.6+ addon for generating PBR maps using GenPBR API"
4. Set to **Public**
5. **DO NOT** initialize with README, .gitignore, or license (we already have these)
6. Click "Create repository"

7. Then run these commands:
```bash
git remote add origin https://github.com/YOUR_USERNAME/genpbr-blender-addon.git
git branch -M main
git push -u origin main
```

Replace `YOUR_USERNAME` with your GitHub username.

## Step 3: Create a GitHub Release

### Option A: Using GitHub CLI (Easiest)

```bash
# Create release with zip file
gh release create v1.0.0 genpbr_blender_addon_v1.0.0.zip --title "GenPBR Map Generator v1.0.0" --notes "Initial release of the GenPBR Map Generator Blender addon.

## Features
- Generate normal, metallic, roughness, and AO maps
- Customizable generation parameters
- Automatic material setup
- Smart image compression

## Installation
1. Download the zip file
2. In Blender: Edit > Preferences > Add-ons > Install...
3. Select the downloaded zip file
4. Enable the addon"
```

### Option B: Using GitHub Web Interface

1. Go to your repository on GitHub
2. Click "Releases" in the right sidebar (or go to `https://github.com/YOUR_USERNAME/genpbr-blender-addon/releases`)
3. Click "Create a new release"
4. Fill in:
   - **Tag version**: `v1.0.0`
   - **Release title**: `GenPBR Map Generator v1.0.0`
   - **Description**: 
     ```
     Initial release of the GenPBR Map Generator Blender addon.
     
     ## Features
     - Generate normal, metallic, roughness, and AO maps
     - Customizable generation parameters
     - Automatic material setup
     - Smart image compression
     
     ## Installation
     1. Download the zip file
     2. In Blender: Edit > Preferences > Add-ons > Install...
     3. Select the downloaded zip file
     4. Enable the addon
     ```
5. Click "Choose a file" under "Attach binaries" and select `genpbr_blender_addon_v1.0.0.zip`
6. Click "Publish release"

## Step 4: Verify the Release

1. Visit your repository's releases page
2. Verify the zip file is attached and downloadable
3. Test downloading and installing the addon

## Future Releases

For future versions:

1. Update version in `__init__.py`:
   ```python
   "version": (1, 1, 0),  # Update version number
   ```

2. Create new release zip:
   ```powershell
   .\create_release.ps1 1.1.0
   ```

3. Commit changes:
   ```bash
   git add .
   git commit -m "Release v1.1.0"
   git tag v1.1.0
   git push origin main --tags
   ```

4. Create new release (same as Step 3)

## Quick Command Reference

```bash
# Create release zip
.\create_release.ps1 1.0.0

# Create and push to GitHub (first time)
gh repo create genpbr-blender-addon --public --source=. --remote=origin
git push -u origin main

# Create release with zip
gh release create v1.0.0 genpbr_blender_addon_v1.0.0.zip --title "GenPBR Map Generator v1.0.0" --notes "Release notes here"
```

## Troubleshooting

### "Repository already exists"
- If the repo exists, just add it as remote:
  ```bash
  git remote add origin https://github.com/YOUR_USERNAME/genpbr-blender-addon.git
  git push -u origin main
  ```

### "Authentication failed"
- Run `gh auth login` to authenticate
- Or use HTTPS with personal access token

### "Permission denied"
- Make sure you have write access to the repository
- Check your GitHub authentication

## Notes

- The zip file should contain only the addon files (no `.git`, `.gitignore`, or scripts)
- Always test the zip file installation before publishing
- Consider adding release notes with changelog for each version
- Tag releases with semantic versioning (v1.0.0, v1.1.0, etc.)

