; ===========================================================================
; GitGrind - Inno Setup installer script
;
; Build the app first, then compile this:
;
;     python tools\build_exe.py --clean --onedir
;     iscc installer\gitgrind.iss
;
; Output: installer\Output\GitGrind-Setup-1.0.exe
;
; Design notes, because a few of these are deliberate:
;
; * PrivilegesRequired=lowest and an install into {localappdata}\Programs.
;   No UAC prompt, no admin rights needed, and - importantly - the install
;   folder stays writable, so the app's data/ and content/ folders work exactly
;   as they do when run from source. Installing into Program Files would make
;   the app fall back to LocalAppData for its database, which works but splits
;   the app and its data across two places.
;
; * There is nothing to detect or download. The executable already contains the
;   Python runtime and the whole UI, and the app itself needs no packages. The
;   only optional component is a Chromium browser for the app-window mode, and
;   Windows 10/11 always ship Edge, so it is checked and reported rather than
;   installed.
;
; * The uninstaller deliberately does NOT delete your database. Losing a year of
;   study history to an uninstall would be unforgivable. It is left behind and
;   the user is told where it is.
; ===========================================================================

#define MyAppName "GitGrind"
#define MyAppVersion "1.0"
#define MyAppPublisher "GitGrind"
#define MyAppExeName "GitGrind.exe"
#define MyAppDescription "A local operating system for a GATE CSE attempt"

[Setup]
; Keep this GUID stable forever. It is how Windows recognises an upgrade rather
; than a second parallel installation.
AppId={{8E4C1A72-3F9D-4B6E-9C21-7A5D0E8B4F13}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppVerName={#MyAppName} {#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppComments={#MyAppDescription}
VersionInfoVersion={#MyAppVersion}.0
VersionInfoDescription={#MyAppDescription}

; Per-user install: no admin, no UAC, and the folder stays writable.
PrivilegesRequired=lowest
PrivilegesRequiredOverridesAllowed=dialog
DefaultDirName={localappdata}\Programs\{#MyAppName}
DefaultGroupName={#MyAppName}
DisableProgramGroupPage=yes
DisableDirPage=no
AllowNoIcons=yes

; 64-bit only, matching the PyInstaller build.
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
MinVersion=6.3

OutputDir=Output
OutputBaseFilename=GitGrind-Setup-{#MyAppVersion}
SetupIconFile=..\static\icon.ico
UninstallDisplayIcon={app}\{#MyAppExeName}
UninstallDisplayName={#MyAppName} {#MyAppVersion}

Compression=lzma2/max
SolidCompression=yes
WizardStyle=modern
LicenseFile=..\LICENSE.txt
InfoAfterFile=..\installer\after-install.txt

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "Create a &desktop shortcut"; \
    GroupDescription: "Shortcuts:"; Flags: unchecked
Name: "startmenu"; Description: "Create a &Start Menu entry"; \
    GroupDescription: "Shortcuts:"

[Files]
; The whole --onedir build. recursesubdirs picks up _internal\, static\ and
; content\ automatically.
Source: "..\dist\{#MyAppName}\*"; DestDir: "{app}"; \
    Flags: ignoreversion recursesubdirs createallsubdirs

; Documentation the user may actually want to read later.
Source: "..\README.md"; DestDir: "{app}"; Flags: ignoreversion isreadme

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; \
    IconFilename: "{app}\{#MyAppExeName}"; Tasks: startmenu
Name: "{group}\{#MyAppName} README"; Filename: "{app}\README.md"; Tasks: startmenu
Name: "{group}\Uninstall {#MyAppName}"; Filename: "{uninstallexe}"; Tasks: startmenu
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; \
    IconFilename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "Start {#MyAppName} now"; \
    Flags: nowait postinstall skipifsilent

[UninstallDelete]
; Remove only what the app generated that is genuinely disposable. The browser
; profile used by window mode is a cache and can go.
Type: filesandordirs; Name: "{app}\data\uiprofile"
Type: filesandordirs; Name: "{app}\__pycache__"

[Code]
{ ---------------------------------------------------------------------------
  Pre-install check: is a Chromium browser available for app-window mode?
  Nothing is installed if it is missing - the app falls back to the default
  browser - but saying so up front stops it looking like a bug later.
  --------------------------------------------------------------------------- }
function ChromiumFound(): Boolean;
var
  Paths: array[0..5] of String;
  I: Integer;
begin
  Paths[0] := ExpandConstant('{commonpf32}\Microsoft\Edge\Application\msedge.exe');
  Paths[1] := ExpandConstant('{commonpf}\Microsoft\Edge\Application\msedge.exe');
  Paths[2] := ExpandConstant('{localappdata}\Microsoft\Edge\Application\msedge.exe');
  Paths[3] := ExpandConstant('{commonpf}\Google\Chrome\Application\chrome.exe');
  Paths[4] := ExpandConstant('{commonpf32}\Google\Chrome\Application\chrome.exe');
  Paths[5] := ExpandConstant('{localappdata}\Google\Chrome\Application\chrome.exe');

  Result := False;
  for I := 0 to 5 do
  begin
    if FileExists(Paths[I]) then
    begin
      Result := True;
      Exit;
    end;
  end;
end;

function InitializeSetup(): Boolean;
begin
  Result := True;
  if not ChromiumFound() then
  begin
    MsgBox('GitGrind could not find Microsoft Edge or Google Chrome on this PC.' + #13#10 + #13#10 +
           'It will still work: instead of its own window, it will open in whatever ' +
           'browser you have set as default. Nothing else changes and nothing needs ' +
           'to be installed.' + #13#10 + #13#10 +
           'Installing Edge or Chrome later gives you the app-window mode automatically.',
           mbInformation, MB_OK);
  end;
end;

{ On uninstall, keep the study history and say where it is. }
procedure CurUninstallStepChanged(CurUninstallStep: TUninstallStep);
var
  DataPath: String;
begin
  if CurUninstallStep = usPostUninstall then
  begin
    DataPath := ExpandConstant('{app}\data');
    if DirExists(DataPath) then
      MsgBox('GitGrind has been removed.' + #13#10 + #13#10 +
             'Your study history has been left behind on purpose:' + #13#10 +
             DataPath + '\gitgrind.db' + #13#10 + #13#10 +
             'Keep that file to carry your streak into a future install. Delete the ' +
             'folder by hand if you are certain you are done with it.',
             mbInformation, MB_OK);
  end;
end;
