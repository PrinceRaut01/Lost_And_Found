#define MyAppName "Lost & Found Desk"
#define MyAppVersion "1.0.0"
#define MyAppPublisher "TEAM DOBERMAN"
#define MyAppExeName "LostAndFoundDesk.exe"

[Setup]
AppId={{3C35C44A-1D29-4F99-9A8E-8F1B2E1A2E8A}}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={autopf}\Lost And Found Desk
DefaultGroupName={#MyAppName}
OutputDir=..\release
OutputBaseFilename=LostAndFoundDesk_Setup
SetupIconFile=..\assets\icon.ico
Compression=lzma2/ultra
SolidCompression=yes
WizardStyle=modern
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64os
PrivilegesRequired=lowest
DisableProgramGroupPage=no
UninstallDisplayIcon={app}\{#MyAppExeName}
CloseApplications=yes
AllowNoIcons=no

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "Create a &desktop shortcut"; GroupDescription: "Additional icons:"; Flags: unchecked

[Files]
Source: "..\dist\{#MyAppExeName}"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{autoprograms}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "Launch {#MyAppName}"; Flags: nowait postinstall skipifsilent
