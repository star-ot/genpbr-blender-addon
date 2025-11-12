# Quick Publish Guide

## One-Command Setup (Using GitHub CLI)

If you have GitHub CLI installed, run this single command to create the repo and push:

```bash
gh repo create genpbr-blender-addon --public --source=. --remote=origin --description "Blender 3.6+ addon for generating PBR maps using GenPBR API" && git branch -M main && git push -u origin main
```

Then create the release:

```bash
gh release create v1.0.0 genpbr_addon_v1.0.0.zip --title "GenPBR Map Generator v1.0.0" --notes "Initial release - See README.md for details"
```

## Manual Steps

1. **Create release zip** (already done):
   ```powershell
   .\create_release.ps1 1.0.0
   ```

2. **Create GitHub repo** (if not exists):
   - Go to https://github.com/new
   - Name: `genpbr-blender-addon`
   - Public
   - Don't initialize with files

3. **Push code**:
   ```bash
   git remote add origin https://github.com/YOUR_USERNAME/genpbr-blender-addon.git
   git branch -M main
   git push -u origin main
   ```

4. **Create release**:
   - Go to Releases > Create new release
   - Tag: `v1.0.0`
   - Upload: `genpbr_addon_v1.0.0.zip`
   - Publish

See `GITHUB_RELEASE.md` for detailed instructions.

