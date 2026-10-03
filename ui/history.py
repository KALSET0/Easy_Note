"""Ventana B — Almacenamiento / Historial (Ctrl+Q, singleton)."""
import customtkinter as ctk

import storage
from ui.window_style import DARK_BG, HINT_COLOR, TEXT_COLOR, apply_rounded_corners

_history_window = None


def open_or_focus_history(parent=None):
    global _history_window
    try:
        if _history_window is not None and _history_window.winfo_exists():
            _history_window.lift()
            _history_window.focus_force()
            _history_window.refresh()
            return _history_window
    except Exception:
        pass
    _history_window = HistoryWindow(parent)
    return _history_window


class HistoryWindow(ctk.CTkToplevel):
    def __init__(self, parent=None) -> None:
        super().__init__(master=parent)
        self.title("Easy_Note — Historial")
        self.geometry("680x520")
        self.minsize(480, 360)
        self.configure(fg_color=DARK_BG)
        try:
            self.after(100, lambda: apply_rounded_corners(self))
        except Exception:
            pass

        self.search = ctk.CTkEntry(
            self,
            corner_radius=12,
            placeholder_text="Buscar por título o fecha/hora…",
            font=("Segoe UI", 13),
        )
        self.search.pack(fill="x", padx=14, pady=(14, 8))
        self.search.bind("<KeyRelease>", lambda e: self.refresh())

        self.list_frame = ctk.CTkScrollableFrame(self, corner_radius=8, fg_color="#212121")
        self.list_frame.pack(fill="both", expand=True, padx=14, pady=(0, 6))

        self.status = ctk.CTkLabel(self, text="", text_color=HINT_COLOR, font=("Segoe UI", 11))
        self.status.pack(pady=(0, 10))

        # Atajos también en esta ventana (Ctrl+S no se toca: solo el editor guarda)
        self.bind_all("<Control-q>", lambda e: (self.lift(), self.focus_force(), "break")[2])
        self.bind_all("<Control-Q>", lambda e: (self.lift(), self.focus_force(), "break")[2])
        try:
            from ui.editor import open_notes_folder

            self.bind_all("<Control-o>", lambda e: (open_notes_folder(), "break")[1])
            self.bind_all("<Control-O>", lambda e: (open_notes_folder(), "break")[1])
        except Exception:
            pass
        self.bind("<FocusIn>", lambda e: self.refresh())

        self.after(50, lambda: self.search.focus_set())
        self.refresh()
        self.protocol("WM_DELETE_WINDOW", self._on_close)

    def _on_close(self):
        global _history_window
        _history_window = None
        self.destroy()

    def refresh(self) -> None:
        query = ""
        try:
            query = self.search.get().strip().lower()
        except Exception:
            pass
        notes = storage.get_all_notes_sorted()
        if query:
            notes = [n for n in notes if query in n.get("title", "").lower()
                     or query in n.get("timestamp", "").lower()
                     or query in n.get("filename", "").lower()]
        for w in self.list_frame.winfo_children():
            w.destroy()

        if not notes:
            lbl = ctk.CTkLabel(self.list_frame, text="Sin notas todavía.", text_color=HINT_COLOR)
            lbl.pack(pady=20)
        for note in notes:
            self._add_row(note)

        total = len(storage.get_all_notes_sorted())
        self.status.configure(text=f"{len(notes)}/{total} notas • doble clic para leer")

    def _add_row(self, note: dict) -> None:
        row = ctk.CTkFrame(self.list_frame, corner_radius=10, fg_color="#2b2b2b")
        row.pack(fill="x", padx=6, pady=4)

        title = note.get("title", note.get("filename", ""))
        ts = note.get("timestamp", "")
        if note.get("is_pending"):
            title = f"○ {title}"

        lbl_title = ctk.CTkLabel(
            row, text=title, anchor="w", text_color=TEXT_COLOR,
            font=("Segoe UI", 13, "bold"), wraplength=380, justify="left",
        )
        lbl_title.pack(side="left", fill="x", expand=True, padx=(12, 6), pady=10)

        lbl_ts = ctk.CTkLabel(row, text=ts, anchor="e", text_color=HINT_COLOR, font=("Segoe UI", 12))
        lbl_ts.pack(side="right", padx=(6, 12), pady=10)

        for w in (row, lbl_title, lbl_ts):
            w.bind("<Double-Button-1>", lambda e, n=note: self._open_viewer(n))

    def _open_viewer(self, note: dict) -> None:
        from ui.viewer import open_viewer

        open_viewer(self, note)
