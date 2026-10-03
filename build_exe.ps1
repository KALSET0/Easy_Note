# Construye dist\Easy Note\Easy Note.exe (onedir, sin consola, con icono).
# Uso: powershell -ExecutionPolicy Bypass -File build_exe.ps1 [-BuildPy <python>] [-Force]
# Crea .venv-build con el Python indicado e instala requirements.txt ahi.
# Para compilar, ese Python debe ser de python.org (NO Microsoft Store):
# con Store el .exe falla con "DLL load failed while importing _tkinter".
# Onedir = arranque y worker instantaneos (sin extraer 28MB en cada guardado).
param(
  [string]$BuildPy = "python",
  [switch]$Force
)
$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

$cmd = Get-Command $BuildPy -ErrorAction SilentlyContinue
if (-not $cmd) {
  throw "No se encontro '$BuildPy'. Instala Python 3.13 de python.org y reintenta (p. ej. -BuildPy 'C:\Python313\python.exe')."
}
if ($cmd.Source -match "WindowsApps" -and -not $Force) {
  throw "El Python detectado es de Microsoft Store ($($cmd.Source)): el .exe fallara con 'DLL load failed _tkinter'. Usa uno de python.org o pasa -Force bajo tu responsabilidad."
}

$VenvDir = Join-Path $PSScriptRoot ".venv-build"
$VenvPy = Join-Path $VenvDir "Scripts\python.exe"
if (-not (Test-Path $VenvPy)) {
  Write-Host "Creando venv en $VenvDir ..."
  & $cmd.Source -m venv $VenvDir
}
& $VenvPy -m pip install -r (Join-Path $PSScriptRoot "requirements.txt")
& $VenvPy -m PyInstaller `
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
