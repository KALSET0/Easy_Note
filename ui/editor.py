"""Ventana A — Editor principal minimalista (inicia por defecto)."""
import os
import subprocess
import sys

import customtkinter as ctk

import storage
from ai_worker import launch_ai_background
from ui.window_style import DARK_BG, HINT_COLOR, TEXT_COLOR, apply_rounded_corners


def open_notes_folder() -> None:
    path = str(storage.ensure_dirs().resolve())
    try:
        if sys.platform == "win32":
            os.startfile(path)  # noqa: S606
        elif sys.platform == "darwin":
            subprocess.Popen(["open", path])
        else:
            subprocess.Popen(["xdg-open", path])
    except Exception:
        try:
            if sys.platform == "win32":
                subprocess.Popen(["explorer", path])
        except Exception:
            pass


def open_history_from(widget) -> None:
    from ui.history import open_or_focus_history

    root = widget.winfo_toplevel()
    open_or_focus_history(root)


class EditorApp(ctk.CTk):
    def __init__(self) -> None:
        super().__init__()
        self.title("Easy_Note")
        self.geometry("800x600")
        self.minsize(480, 360)
        self.configure(fg_color=DARK_BG)
        try:
            self.after(100, lambda: apply_rounded_corners(self))
        except Exception:
            pass

        self.textbox = ctk.CTkTextbox(
            self,
            corner_radius=8,
            fg_color="#212121",
            text_color=TEXT_COLOR,
            font=("Segoe UI", 15),
            wrap="word",
        )
        self.textbox.pack(fill="both", expand=True, padx=14, pady=(14, 6))
        # Auto-enfoque al iniciar
        self.after(50, lambda: self.textbox.focus_set())

        self.hint = ctk.CTkLabel(
            self,
            text="Ctrl+S guardar y cerrar  •  Ctrl+Q historial  •  Ctrl+O carpeta",
            text_color=HINT_COLOR,
            font=("Segoe UI", 11),
        )
        self.hint.pack(pady=(0, 10))

        # Ctrl+S solo en el editor (bind de ventana, no global): evita
        # guardar duplicados al pulsar Ctrl+S en historial/visor.
        # Ctrl+Q / Ctrl+O sí son globales (bind_all).
        for seq in ("<Control-s>", "<Control-S>"):
            self.bind(seq, self._on_save)
        for seq in ("<Control-q>", "<Control-Q>"):
            self.bind_all(seq, self._on_history)
        for seq in ("<Control-o>", "<Control-O>"):
            self.bind_all(seq, self._on_open_folder)

        self.protocol("WM_DELETE_WINDOW", self._on_close_without_saving)

    # --- callbacks ---
    def _on_save(self, event=None):
        self.save_and_close()
        return "break"

    def _on_history(self, event=None):
        open_history_from(self)
        return "break"

    def _on_open_folder(self, event=None):
        open_notes_folder()
        return "break"

    def _on_close_without_saving(self):
        self.destroy()

    def save_and_close(self) -> None:
        text = self.textbox.get("1.0", "end")
        if text and text.strip():
            filename = storage.save_raw_note(text)
            if filename:
                # Proceso IA detached: la app se cierra al instante sin esperar a Ollama.
                launch_ai_background(filename)
        self.destroy()
