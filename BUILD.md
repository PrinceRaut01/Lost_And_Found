# Windows Build Guide

## Detected Project Type
Python desktop application using Tkinter and SQLite.

## Entry Point
`main.py`

## Build Commands

### Build the executable and installer
```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\build.ps1 -Package
```

### Build only the executable
```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\build.ps1
```

### Package an existing build into the installer
```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\package.ps1
```

### One-click batch build
```bat
build.bat
```

## Build System
- `PyInstaller` for the application EXE
- `Inno Setup` for the Windows installer

## Icon Configuration
- Source icon: `assets/icon.ico`
- Embedded in the EXE through PyInstaller `--icon`
- Bundled as app data so Tkinter can load the same icon at runtime
- Used by the installer via `SetupIconFile`

## Output Paths
- EXE: `dist\LostAndFoundDesk.exe`
- Release copy: `release\LostAndFoundDesk.exe`
- Installer: `release\LostAndFoundDesk_Setup.exe`

## Current Artifact Sizes
- EXE: 10.73 MB
- Installer: 12.44 MB

## Required Files
- `main.py`
- `admin_page.py`
- `user_page.py`
- `db_connection.py`
- `assets/icon.ico`
- `build.ps1`
- `package.ps1`
- `build.bat`
- `installer/LostAndFoundDesk.iss`

## Runtime Notes
- The database is stored in the user profile under `%LOCALAPPDATA%\Lost_and_Found_Desk_App\lost_and_found.db` when the app is frozen.
- The login launcher uses frozen-aware arguments so admin and user pages work from the packaged EXE.
