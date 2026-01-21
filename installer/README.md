# InfinityAlamoDemo Installer

This folder contains scripts and configuration to build a Windows installer
(`InfinityAlamoDemo-Setup.exe`) with a desktop shortcut.

## Requirements
- Python 3.11+
- `pip install pyinstaller`
- Inno Setup 6 (ISCC.exe on PATH)

## Build Steps
1. Build the executable:
   - `powershell -ExecutionPolicy Bypass -File .\installer\build_exe.ps1`
2. Build the installer:
   - `powershell -ExecutionPolicy Bypass -File .\installer\build_installer.ps1`

## Outputs
- Executable: `dist/InfinityAlamoDemo/InfinityAlamoDemo.exe`
- Installer: `installer/Output/InfinityAlamoDemo-Setup.exe`

## Runtime data location
When installed, the app writes reports/logs to:
- `%LOCALAPPDATA%\\InfinityAlamoDemo\\output`
- `%LOCALAPPDATA%\\InfinityAlamoDemo\\data`
