# Construye dist\Easy Note\Easy Note.exe (onedir, sin consola, con icono).
# Usa el venv de build con Python python.org (no Store): C:\Users\jjcp1\.venvs\easynote-build
# Onedir = arranque y worker instantáneos (sin extraer 28MB en cada guardado).
$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot
$BuildPy = "C:\Users\jjcp1\.venvs\easynote-build\Scripts\python.exe"
& $BuildPy -m PyInstaller `
  --noconfirm `
  --clean `
  --noconsole `
  --onedir `
  --name "Easy Note" `
  --icon "assets\icon.ico" `
  --version-file "version_info.txt" `
  --add-data "assets\icon.ico;assets" `
  --collect-all "customtkinter" `
  main.py
Write-Host "OK: dist\Easy Note\Easy Note.exe"
