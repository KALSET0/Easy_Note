# Easy Note

Notepad minimalista en modo oscuro para notas de estudio nocturnas. Escribes, guardas con `Ctrl+S` y la app se cierra al instante; una IA local (Ollama) corrige la nota en segundo plano y le pone título.

## Requisitos

- Python 3.13
- [Ollama](https://ollama.com) corriendo con el modelo `qwen2.5:7b-instruct-q4_K_M` (`ollama pull qwen2.5:7b-instruct-q4_K_M`)

## Instalación y ejecución

```bat
pip install -r requirements.txt
python main.py
```

O usa el ejecutable `dist\Easy Note\Easy Note.exe` (ver `build_exe.ps1`, compilado con Python python.org en modo onedir) con su acceso directo del escritorio: icono propio en la barra de tareas y proceso "Easy Note" en el Administrador de tareas.

## Atajos

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

## Estructura

```
main.py  ui/editor.py  ui/history.py  ui/viewer.py  ui/window_style.py
storage.py  ai_worker.py  config.py  assets/icon.ico  build_exe.ps1
```
