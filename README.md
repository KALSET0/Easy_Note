# Easy Note

Notepad minimalista en modo oscuro para notas de estudio nocturnas. Escribes, guardas con `Ctrl+S` y la app se cierra al instante; una IA local (Ollama) corrige la nota en segundo plano y le pone título.

> Solo Windows 10/11.

## Requisitos

- Python 3.13 (cualquiera sirve para usar la app; para compilar el `.exe` debe ser de [python.org](https://www.python.org/downloads/), **no** Microsoft Store).
- [Ollama](https://ollama.com) corriendo (opcional: sin Ollama las notas quedan pendientes y se procesan al siguiente inicio).

## Arranque rápido

```bat
git clone https://github.com/KALSET0/Easy_Note.git
cd Easy_Note
pip install -r requirements.txt
ollama pull qwen2.5:7b-instruct-q4_K_M
ollama serve
python main.py
```

## Uso

| Atajo | Acción |
|---|---|
| `Ctrl+S` | Guarda la nota cruda, lanza la IA en fondo y cierra (solo editor) |
| `Ctrl+Q` | Abre/enfoca el historial (funciona en cualquier ventana) |
| `Ctrl+O` | Abre la carpeta `/notas` en el Explorador |

En el historial: busca por título o fecha, doble clic para leer (solo lectura) y botón `✕` por fila para eliminar (pide confirmación y borra el crudo + la versión IA).

## Dónde van las notas

- Crudas: `/notas/YYYY-MM-DD_HH-MM-SS.txt` (texto tal cual, nunca se modifican).
- Índice IA: `notes_index.json` (`filename`, `timestamp`, `title`, `cleaned_content`).
- Ambos son datos locales e ignorados por git. Si Ollama está apagado, la nota queda pendiente (título = nombre de archivo) y se procesa al siguiente inicio.

## Ejecutable `.exe` (opcional)

```powershell
powershell -ExecutionPolicy Bypass -File build_exe.ps1
powershell -ExecutionPolicy Bypass -File make_shortcut.ps1
```

Genera `dist\Easy Note\Easy Note.exe` (onedir, sin consola, con icono) y crea el acceso directo en el escritorio: icono propio en la barra de tareas y proceso "Easy Note" en el Administrador de tareas. El Python que compile **debe ser de python.org**, o el `.exe` fallará con `DLL load failed while importing _tkinter`.

## Estructura

```
main.py  ui/editor.py  ui/history.py  ui/viewer.py  ui/window_style.py
storage.py  ai_worker.py  config.py  assets/icon.ico
requirements.txt  version_info.txt  build_exe.ps1  make_shortcut.ps1
```

`Easy_Note.bat` (launcher local sin consola) no se versiona: cada equipo usa el suyo.

## Problemas conocidos

- **`.exe` muestra `DLL load failed _tkinter`**: se compiló con Python de Microsoft Store. Recompila con python.org (`build_exe.ps1` lo valida y avisa).
- **La barra muestra el icono viejo**: es caché de Windows; reinicia el Explorador o cambia el tamaño de los iconos.
- **Antivirus marca el `.exe`**: falso positivo típico de PyInstaller; compílalo tú mismo con `build_exe.ps1`.
- **Nota pendiente sin título**: Ollama estaba apagado al guardar; enciéndelo y reinicia la app para procesarla.
