; ============================================================
;  Lost and Found Desk  –  Inno Setup installer script
;  Built by TEAM DOBERMAN
; ============================================================

#define MyAppName        "Lost and Found Desk"
#define MyAppVersion     "2.0.0"
#define MyAppPublisher   "TEAM DOBERMAN"
#define MyAppURL         "https://github.com/PrinceRaut01"
#define MyAppExeName     "LostAndFoundDesk.exe"
#define MyAppCopyright   "Copyright (C) 2025 TEAM DOBERMAN. All rights reserved."
#define MyAppDescription "Lost and Found Item Management System"

; ── Unique application GUID (never change this after first release) ──────────
[Setup]
AppId={{3C35C44A-1D29-4F99-9A8E-8F1B2E1A2E8A}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppVerName={#MyAppName} {#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}
AppCopyright={#MyAppCopyright}
AppComments={#MyAppDescription}

; ── Version resource embedded in the Setup EXE ───────────────────────────────
VersionInfoVersion={#MyAppVersion}.0
VersionInfoCompany={#MyAppPublisher}
VersionInfoDescription={#MyAppDescription} Setup
VersionInfoCopyright={#MyAppCopyright}
VersionInfoProductName={#MyAppName}
VersionInfoProductVersion={#MyAppVersion}.0
VersionInfoOriginalFileName=LostAndFoundDesk_Setup.exe

; ── Install location – Program Files (requires admin) ────────────────────────
DefaultDirName={autopf}\Lost and Found Desk
DefaultGroupName={#MyAppName}
PrivilegesRequired=admin
PrivilegesRequiredOverridesAllowed=commandline

; ── Output ───────────────────────────────────────────────────────────────────
OutputDir=..\release
OutputBaseFilename=LostAndFoundDesk_Setup
SetupIconFile=..\assets\icon.ico
UninstallDisplayIcon={app}\{#MyAppExeName}
UninstallDisplayName={#MyAppName}

; ── Compression ──────────────────────────────────────────────────────────────
Compression=lzma2/ultra
SolidCompression=yes
LZMAUseSeparateProcess=yes

; ── Wizard UI ────────────────────────────────────────────────────────────────
WizardStyle=modern
DisableProgramGroupPage=no
AllowNoIcons=no
CloseApplications=yes
ShowLanguageDialog=no

; ── Architecture ─────────────────────────────────────────────────────────────
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64os

; ── Languages ────────────────────────────────────────────────────────────────
[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

; ── Optional tasks ───────────────────────────────────────────────────────────
[Tasks]
Name: "desktopicon"; \
  Description: "Create a &desktop shortcut"; \
  GroupDescription: "Additional icons:"; \
  Flags: checkedonce

; ── Files ─────────────────────────────────────────────────────────────────────
[Files]
; Always ships the fixed EXE from release\ (not dist\)
Source: "..\release\{#MyAppExeName}"; \
  DestDir: "{app}"; \
  Flags: ignoreversion

; ── Registry – app path for "Open with" and other Windows associations ────────
[Registry]
Root: HKLM; Subkey: "Software\TEAM DOBERMAN\Lost and Found Desk"; \
  ValueType: string; ValueName: "InstallDir"; ValueData: "{app}"; \
  Flags: uninsdeletekey
Root: HKLM; Subkey: "Software\TEAM DOBERMAN\Lost and Found Desk"; \
  ValueType: string; ValueName: "Version"; ValueData: "{#MyAppVersion}"; \
  Flags: uninsdeletekey

; ── Shortcuts ────────────────────────────────────────────────────────────────
[Icons]
; Start Menu
Name: "{group}\{#MyAppName}"; \
  Filename: "{app}\{#MyAppExeName}"; \
  IconFilename: "{app}\{#MyAppExeName}"; \
  Comment: "{#MyAppDescription}"
Name: "{group}\Uninstall {#MyAppName}"; \
  Filename: "{uninstallexe}"

; Desktop (only if task selected)
Name: "{autodesktop}\{#MyAppName}"; \
  Filename: "{app}\{#MyAppExeName}"; \
  IconFilename: "{app}\{#MyAppExeName}"; \
  Comment: "{#MyAppDescription}"; \
  Tasks: desktopicon

; ── Post-install run ─────────────────────────────────────────────────────────
[Run]
Filename: "{app}\{#MyAppExeName}"; \
  Description: "Launch {#MyAppName} now"; \
  Flags: nowait postinstall skipifsilent
