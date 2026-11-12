# Builds BeedoTrade.exe (PyInstaller) and the Windows installer (Inno Setup).
# Usage, from the app folder:  powershell -ExecutionPolicy Bypass -File packaging\build.ps1
# Needs: uv, Inno Setup 6 (winget install JRSoftware.InnoSetup), and packaging\guide\Beedo-Trade User Guide.pdf
$ErrorActionPreference = "Stop"
$App = Split-Path $PSScriptRoot -Parent
# Build in a short folder: deep paths break Windows DLL loading and PyInstaller.
$Short = Join-Path $env:TEMP "bt"
$env:UV_PROJECT_ENVIRONMENT = Join-Path $Short "venv"
Set-Location $App

$Version = ([regex]'__version__ = "([\d.]+)"').Match((Get-Content "$App\beedo_app\__init__.py" -Raw)).Groups[1].Value
if (-not $Version) { throw "No __version__ in beedo_app\__init__.py" }
$Guide = "$App\packaging\guide\Beedo-Trade User Guide.pdf"
if (-not (Test-Path $Guide)) { throw "Missing ${Guide}. Build the user guide first." }
Write-Host "Building Beedo-Trade $Version"

uv sync --quiet
uv run pytest -q
if ($LASTEXITCODE) { throw "Tests failed" }

# Windows file properties (right-click > Properties > Details)
$v = ($Version.Split(".") + @("0", "0", "0"))[0..3] -join ", "
New-Item -ItemType Directory -Force $Short | Out-Null
@"
VSVersionInfo(ffi=FixedFileInfo(filevers=($v), prodvers=($v)), kids=[
  StringFileInfo([StringTable('040904B0', [
    StringStruct('CompanyName', 'Beedo'), StringStruct('FileDescription', 'Beedo-Trade'),
    StringStruct('FileVersion', '$Version'), StringStruct('InternalName', 'BeedoTrade'),
    StringStruct('LegalCopyright', 'Copyright (c) 2026 Beedo. MIT License.'),
    StringStruct('OriginalFilename', 'BeedoTrade.exe'), StringStruct('ProductName', 'Beedo-Trade'),
    StringStruct('ProductVersion', '$Version')])]),
  VarFileInfo([VarStruct('Translation', [1033, 1200])])])
"@ | Set-Content (Join-Path $Short "version_info.txt") -Encoding utf8

# Absolute paths: PyInstaller resolves relative ones against --specpath.
uv run pyinstaller --noconfirm --clean --windowed --name BeedoTrade `
  --icon "$App\packaging\beedo.ico" --version-file (Join-Path $Short "version_info.txt") --splash "$App\packaging\splash.png" `
  --add-data "$App\beedo_app\web;web" `
  --paths "$App\..\skills\beedo-trade\scripts" --paths "$App" --hidden-import analyze `
  --exclude-module setuptools --exclude-module pkg_resources `
  --workpath (Join-Path $Short "work") --distpath (Join-Path $Short "dist") --specpath (Join-Path $Short "spec") `
  "$App\beedo_app\main.py"
if ($LASTEXITCODE) { throw "PyInstaller failed" }

$iscc = @("$env:LOCALAPPDATA\Programs\Inno Setup 6\ISCC.exe", "${env:ProgramFiles(x86)}\Inno Setup 6\ISCC.exe") | Where-Object { Test-Path $_ } | Select-Object -First 1
if (-not $iscc) { Write-Host "Inno Setup not found: install it with  winget install JRSoftware.InnoSetup  then re-run."; exit 1 }
& $iscc /Q "/DAppVersion=$Version" "/DSourceDir=$(Join-Path $Short 'dist\BeedoTrade')" "/DOutDir=$(Join-Path $Short 'out')" `
  "/DIconFile=$App\packaging\beedo.ico" "/DLicenseFile=$App\packaging\license.txt" "/DGuideFile=$Guide" packaging\installer.iss
if ($LASTEXITCODE) { throw "Inno Setup failed" }
New-Item -ItemType Directory -Force (Join-Path $App "dist") | Out-Null
Copy-Item (Join-Path $Short "out\Beedo-Trade-Setup-$Version.exe") (Join-Path $App "dist") -Force
Get-ChildItem (Join-Path $App "dist") | Select-Object Name, @{n = "MB"; e = { [math]::Round($_.Length / 1MB, 1) } }
