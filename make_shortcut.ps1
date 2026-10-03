# Crea "Easy Note.lnk" en el escritorio apuntando al .exe onedir, con el icono.
# Uso: powershell -ExecutionPolicy Bypass -File make_shortcut.ps1
# Requiere haber compilado antes con build_exe.ps1.
$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

$exe = Join-Path $PSScriptRoot "dist\Easy Note\Easy Note.exe"
if (-not (Test-Path $exe)) {
  throw "No existe $exe. Compila primero con build_exe.ps1."
}
$desktop = [Environment]::GetFolderPath("Desktop")
$ws = New-Object -ComObject WScript.Shell
$lnk = $ws.CreateShortcut((Join-Path $desktop "Easy Note.lnk"))
$lnk.TargetPath = $exe
$lnk.WorkingDirectory = Split-Path $exe
$lnk.IconLocation = (Join-Path $PSScriptRoot "assets\icon.ico")
$lnk.Description = "Easy Note - notas de estudio nocturnas"
$lnk.Save()
Write-Host "OK: $desktop\Easy Note.lnk"
