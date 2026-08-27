#ifndef MyAppVersion
  #define MyAppVersion "0.1.0"
#endif

#define MyAppName "MarketDEX OS"
#define MyAppPublisher "MarketDEX"
#define MyAppExeName "MarketDEX.exe"

[Setup]
AppId={{9B1B7256-5B57-46A2-9B79-670842A341EF}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL=https://github.com/markperezne8-spec/MarketDEX
AppSupportURL=https://github.com/markperezne8-spec/MarketDEX/issues
AppUpdatesURL=https://github.com/markperezne8-spec/MarketDEX/releases
AppComments=Offline-first collectibles business operating system
AppVersionInfoDescription=MarketDEX OS
AppVersionInfoProductName=MarketDEX OS
AppVersionInfoCompany=MarketDEX
AppVersionInfoCopyright=Copyright (C) MarketDEX
VersionInfoVersion=0.1.0.0
VersionInfoProductVersion=0.1.0
DefaultDirName={localappdata}\Programs\MarketDEX
DefaultGroupName=MarketDEX
DisableProgramGroupPage=yes
OutputDir=..\dist
OutputBaseFilename=MarketDEX_Setup
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=lowest
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
UninstallDisplayIcon={app}\{#MyAppExeName}
CloseApplications=yes
RestartApplications=no
UsePreviousAppDir=yes

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
Source: "..\dist\MarketDEX.exe"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\MarketDEX OS"; Filename: "{app}\{#MyAppExeName}"
Name: "{autodesktop}\MarketDEX OS"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,MarketDEX OS}"; Flags: nowait postinstall skipifsilent
