; Beedo-Trade Windows installer (Inno Setup 6). Built by packaging\build.ps1, which passes
; AppVersion, SourceDir, OutDir, IconFile, LicenseFile and GuideFile.
#define AppName "Beedo-Trade"
#define AppExe "BeedoTrade.exe"
#define AppUrl "https://github.com/BeedoElOmda/Beedo-Trade"

[Setup]
AppId={{6B0E3B1E-7A4C-4E7B-9C3D-BEED0742ADE1}
AppName={#AppName}
AppVersion={#AppVersion}
AppVerName={#AppName} {#AppVersion}
AppPublisher=Beedo
AppPublisherURL={#AppUrl}
AppSupportURL={#AppUrl}/issues
AppUpdatesURL={#AppUrl}/releases
AppCopyright=Copyright (c) 2026 Beedo. MIT License.
VersionInfoVersion={#AppVersion}
VersionInfoDescription={#AppName} Setup
; "Only for me" needs no admin rights; "All users" asks for admin approval. {autopf} follows the choice:
; %LOCALAPPDATA%\Programs for one user, C:\Program Files for all users.
PrivilegesRequired=lowest
PrivilegesRequiredOverridesAllowed=dialog commandline
DefaultDirName={autopf}\{#AppName}
DefaultGroupName={#AppName}
DisableProgramGroupPage=yes
UsePreviousAppDir=yes
LicenseFile={#LicenseFile}
OutputDir={#OutDir}
OutputBaseFilename=Beedo-Trade-Setup-{#AppVersion}
SetupIconFile={#IconFile}
UninstallDisplayIcon={app}\{#AppExe}
UninstallDisplayName={#AppName}
WizardStyle=modern
Compression=lzma2/max
SolidCompression=yes
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
MinVersion=10.0
; Close a running Beedo-Trade before updating or uninstalling
CloseApplications=force
RestartApplications=no

[Tasks]
Name: "desktopicon"; Description: "Create a &desktop shortcut"; GroupDescription: "Shortcuts:"

; Older guides. A guide left open in a PDF viewer is locked: it is skipped here instead of aborting the upgrade.
[InstallDelete]
Type: files; Name: "{app}\docs\Beedo-Trade User Guide*.pdf"

[UninstallDelete]
Type: files; Name: "{app}\docs\Beedo-Trade User Guide*.pdf"

[Files]
Source: "{#SourceDir}\*"; DestDir: "{app}"; Flags: recursesubdirs ignoreversion
Source: "{#GuideFile}"; DestDir: "{app}\docs"; DestName: "Beedo-Trade User Guide {#AppVersion}.pdf"; Flags: ignoreversion

[Icons]
Name: "{group}\{#AppName}"; Filename: "{app}\{#AppExe}"; Comment: "EGX technical analysis with the Beedo course method"
Name: "{group}\{#AppName} User Guide"; Filename: "{app}\docs\Beedo-Trade User Guide {#AppVersion}.pdf"
Name: "{group}\Uninstall {#AppName}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#AppName}"; Filename: "{app}\{#AppExe}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#AppExe}"; Description: "Start {#AppName} now"; Flags: nowait postinstall skipifsilent
Filename: "{app}\docs\Beedo-Trade User Guide {#AppVersion}.pdf"; Description: "Open the user guide"; Flags: shellexec nowait postinstall skipifsilent unchecked

[Code]
const WebView2Key = 'SOFTWARE\WOW6432Node\Microsoft\EdgeUpdate\Clients\{F3017226-FE2A-4295-8BDF-00C3A9A7E4C5}';

function HasWebView2(): Boolean;
var V: String;
begin
  Result := (RegQueryStringValue(HKLM, WebView2Key, 'pv', V) and (V <> '') and (V <> '0.0.0.0')) or
            (RegQueryStringValue(HKCU, 'Software\Microsoft\EdgeUpdate\Clients\{F3017226-FE2A-4295-8BDF-00C3A9A7E4C5}', 'pv', V) and (V <> ''));
end;

function InitializeSetup(): Boolean;
begin
  Result := True;
  if not HasWebView2() then
    SuppressibleMsgBox('Beedo-Trade uses Microsoft Edge WebView2, which this PC does not seem to have.' + #13#10#13#10 +
      'Setup will continue. If the app window stays blank, install WebView2 free from Microsoft:' + #13#10 +
      'https://go.microsoft.com/fwlink/p/?LinkId=2124703', mbInformation, MB_OK, IDOK);
end;

// "Only for me" installs can't write to Program Files or Windows folders: say so before failing.
function IsProtected(Dir: String): Boolean;
var D: String;
begin
  D := Lowercase(AddBackslash(Dir));
  Result := (Pos(Lowercase(AddBackslash(ExpandConstant('{commonpf64}'))), D) = 1) or
            (Pos(Lowercase(AddBackslash(ExpandConstant('{commonpf32}'))), D) = 1) or
            (Pos(Lowercase(AddBackslash(ExpandConstant('{win}'))), D) = 1);
end;

function NextButtonClick(CurPageID: Integer): Boolean;
begin
  Result := True;
  if (CurPageID = wpSelectDir) and (not IsAdminInstallMode) and IsProtected(WizardDirValue) then begin
    MsgBox('You chose "Install for me only", which can''t write to ' + WizardDirValue + '.' + #13#10#13#10 +
      'Pick a folder in your user profile (the suggested one is fine), or go back to the start of Setup ' +
      'and choose "Install for all users" to install into Program Files.', mbError, MB_OK);
    Result := False;
  end;
end;

// Uninstall: offer to remove the watchlist and settings too
procedure CurUninstallStepChanged(CurUninstallStep: TUninstallStep);
var Data: String;
begin
  if CurUninstallStep = usPostUninstall then begin
    Data := ExpandConstant('{userappdata}\BeedoTrade');
    if DirExists(Data) then
      if SuppressibleMsgBox('Also delete your Beedo-Trade settings and watchlist?' + #13#10 + '(' + Data + ')' + #13#10#13#10 +
         'Choose No to keep them for a future install.', mbConfirmation, MB_YESNO, IDNO) = IDYES then
        DelTree(Data, True, True, True);
  end;
end;
