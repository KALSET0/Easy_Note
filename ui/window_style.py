"""Tema oscuro + esquinas redondeadas (CustomTkinter)."""
import customtkinter as ctk

DARK_BG = "#1a1a1a"
DARK_FG = "#212121"
TEXT_COLOR = "#e8e8e8"
HINT_COLOR = "#8a8a8a"


def apply_theme() -> None:
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("dark-blue")


def set_app_id(app_id: str = "EasyNote.App") -> None:
    """Fija el AppUserModelID para agrupar bien el icono en la barra de tareas."""
    try:
        import ctypes

        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(app_id)
    except Exception:
        pass


def set_window_icon(window) -> None:
    """Aplica assets/icon.ico a la ventana (botón de barra de tareas)."""
    try:
        from config import resource_path

        ico = resource_path("assets", "icon.ico")
        if ico.exists():
            window.iconbitmap(str(ico))
    except Exception:
        pass


def apply_rounded_corners(window, round_level: int = 2) -> None:
    """Fuerza esquinas redondeadas en Windows 11 vía DWM. Degrada en silencio.

    round_level: 0=rect, 1=ligero, 2=redondo (DWMWCP_ROUND).
    """
    try:
        import ctypes

        hwnd = window.winfo_id()
        DWMWA_WINDOW_CORNER_PREFERENCE = 33
        value = ctypes.c_int(round_level)
        ctypes.windll.dwmapi.DwmSetWindowAttribute(
            hwnd, DWMWA_WINDOW_CORNER_PREFERENCE,
            ctypes.byref(value), ctypes.sizeof(value),
        )
    except Exception:
        pass
