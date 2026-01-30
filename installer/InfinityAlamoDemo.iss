[Setup]
AppName=InfinityAlamoDemo
AppVersion=0.1.0
AppPublisher=InfinityAlamo
DefaultDirName={autopf}\InfinityAlamoDemo
DefaultGroupName=InfinityAlamoDemo
OutputDir=Output
OutputBaseFilename=InfinityAlamoDemo-Setup
Compression=lzma
SolidCompression=yes
SetupIconFile=..\assets\infinity_alamo_demo.ico

[Files]
Source: "..\dist\InfinityAlamoDemo\*"; DestDir: "{app}"; Flags: recursesubdirs createallsubdirs

[Icons]
Name: "{group}\InfinityAlamoDemo"; Filename: "{app}\InfinityAlamoDemo.exe"; WorkingDir: "{app}"
Name: "{commondesktop}\InfinityAlamoDemo"; Filename: "{app}\InfinityAlamoDemo.exe"; WorkingDir: "{app}"

[Run]
Filename: "{app}\InfinityAlamoDemo.exe"; Description: "Launch InfinityAlamoDemo"; Flags: nowait postinstall skipifsilent
