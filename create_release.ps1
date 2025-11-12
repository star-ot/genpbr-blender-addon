# PowerShell script to create a release zip for GitHub
# Usage: .\create_release.ps1 [version]

param(
    [string]$Version = "1.0.0"
)

$AddonName = "genpbr_blender_addon"
$ZipName = "${AddonName}_v${Version}.zip"

Write-Host "Creating release zip: $ZipName" -ForegroundColor Green

# Remove old zip if exists
if (Test-Path $ZipName) {
    Remove-Item $ZipName
    Write-Host "Removed existing zip file" -ForegroundColor Yellow
}

# Files to include in the zip
$FilesToInclude = @(
    "__init__.py",
    "preferences.py",
    "properties.py",
    "operators.py",
    "ui.py",
    "utils.py",
    "README.md"
)

# Verify all files exist
$MissingFiles = @()
foreach ($file in $FilesToInclude) {
    if (-not (Test-Path $file)) {
        $MissingFiles += $file
    } else {
        Write-Host "Found: $file" -ForegroundColor Cyan
    }
}

if ($MissingFiles.Count -gt 0) {
    Write-Host "Warning: Missing files:" -ForegroundColor Yellow
    $MissingFiles | ForEach-Object { Write-Host "  - $_" -ForegroundColor Yellow }
}

# Create zip using Compress-Archive (PowerShell 5.0+)
try {
    Compress-Archive -Path $FilesToInclude -DestinationPath $ZipName -Force
    Write-Host "`nRelease zip created successfully: $ZipName" -ForegroundColor Green
    
    $FileInfo = Get-Item $ZipName
    $SizeKB = [math]::Round($FileInfo.Length / 1KB, 2)
    Write-Host "File size: $SizeKB KB" -ForegroundColor Green
} catch {
    Write-Host "Error creating zip: $_" -ForegroundColor Red
    exit 1
}

