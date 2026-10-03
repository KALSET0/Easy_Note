"""Easy Note — punto de entrada principal. `python main.py`.

En el ejecutable PyInstaller el worker IA va integrado:
`Easy Note.exe --worker <filename>` procesa una nota y sale.
"""
import sys
import threading

from ai_worker import launch_ai_background, ping_ollama
import storage
from ui.window_style import apply_theme, set_app_id


def reconcile_pendings_async() -> None:
    """Re-procesa en fondo los crudos sin entrada IA (cubre Ollama caído)."""
    def _job():
        try:
            notes = storage.get_all_notes_sorted()
            pendings = [n for n in notes if n.get("is_pending")]
            if not pendings:
                return
            if not ping_ollama():
                return
            for n in pendings:
                launch_ai_background(n["filename"])
        except Exception:
            pass
    threading.Thread(target=_job, daemon=True).start()


def main() -> None:
    if len(sys.argv) >= 2 and sys.argv[1] == "--worker":
        from ai_worker import main as worker_main

        filename = sys.argv[2] if len(sys.argv) >= 3 else ""
        raise SystemExit(worker_main(["worker", filename]))
    set_app_id("EasyNote.App")
    apply_theme()
    storage.ensure_dirs()
    reconcile_pendings_async()
    from ui.editor import EditorApp

    app = EditorApp()
    app.mainloop()


if __name__ == "__main__":
    main()
