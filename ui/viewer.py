"""Ventana C — Visor Read-Only (doble clic en historial).

No registra atajos: Ctrl+Q / Ctrl+O viven solo en la raíz (ver ui/history.py).
"""
import customtkinter as ctk

import storage
from ui.window_style import DARK_BG, HINT_COLOR, TEXT_COLOR, apply_rounded_corners, set_window_icon

_open_viewers: dict[str, list] = {}


def close_viewers_for(filename: str) -> None:
    """Cierra los visores abiertos de una nota (usado al eliminarla)."""
    for win in list(_open_viewers.get(filename or "", [])):
        try:
            win.destroy()
        except Exception:
            pass


def _register(filename: str, win) -> None:
    _open_viewers.setdefault(filename or "", []).append(win)

    def _on_destroy(event):
        if event.widget is win:
            lst = _open_viewers.get(filename or "", [])
            try:
                lst.remove(win)
            except ValueError:
                pass
            if not lst:
                _open_viewers.pop(filename or "", None)

    win.bind("<Destroy>", _on_destroy, add="+")


def open_viewer(parent, note: dict):
    win = ctk.CTkToplevel(master=parent)
    win.title(note.get("title", "Nota"))
    win.geometry("680x520")
    win.minsize(480, 360)
    win.configure(fg_color=DARK_BG)
    set_window_icon(win)
    try:
        win.after(100, lambda: apply_rounded_corners(win))
    except Exception:
        pass

    title_text = note.get("title", note.get("filename", ""))
    ctk.CTkLabel(
        win, text=title_text, anchor="w", text_color=TEXT_COLOR,
        font=("Segoe UI", 16, "bold"), wraplength=620, justify="left",
    ).pack(fill="x", padx=16, pady=(14, 2))
    ctk.CTkLabel(
        win, text=note.get("timestamp", ""), anchor="w",
        text_color=HINT_COLOR, font=("Segoe UI", 12),
    ).pack(fill="x", padx=16, pady=(0, 8))

    if note.get("is_pending") or not note.get("cleaned_content"):
        ctk.CTkLabel(
            win, text="⏳ Pendiente de IA — mostrando texto crudo.",
            text_color=HINT_COLOR, font=("Segoe UI", 11),
        ).pack(fill="x", padx=16, pady=(0, 6))

    box = ctk.CTkTextbox(
        win, corner_radius=8, fg_color="#212121",
        text_color=TEXT_COLOR, font=("Segoe UI", 14), wrap="word",
    )
    box.pack(fill="both", expand=True, padx=14, pady=(0, 14))
    box.insert("1.0", storage.get_display_content(note))
    box.configure(state="disabled")  # RESTRICCIÓN: solo lectura, sin edición

    _register(note.get("filename", ""), win)

    win.lift()
    win.focus_force()
    return win
