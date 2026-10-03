# Construye dist\Easy Note.exe (onefile, sin consola, con icono).
# Requiere: pip install -r requirements.txt pyinstaller
$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot
python -m PyInstaller `
  --noconfirm `
  --clean `
  --noconsole `
  --onefile `
  --name "Easy Note" `
  --icon "assets\icon.ico" `
  --version-file "version_info.txt" `
  --add-data "assets\icon.ico;assets" `
  --collect-all "customtkinter" `
  main.py
Write-Host "OK: dist\Easy Note.exe"
