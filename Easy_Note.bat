@echo off
rem Easy_Note launcher — abre la app sin ventana de consola.
cd /d "%~dp0"
start "" /B pythonw main.py
exit
