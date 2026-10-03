"""Persistencia: archivos crudos en /notas + índice JSON."""
import json
import os
import time
from datetime import datetime
from pathlib import Path

import config


def ensure_dirs() -> Path:
    config.NOTAS_DIR.mkdir(parents=True, exist_ok=True)
    return config.NOTAS_DIR


def generate_filename(now: datetime | None = None) -> str:
    """Nombre ÚNICAMENTE con fecha y hora exacta: YYYY-MM-DD_HH-MM-SS.txt"""
    now = now or datetime.now()
    return now.strftime("%Y-%m-%d_%H-%M-%S.txt")


def save_raw_note(text: str) -> str | None:
    """Guarda el texto crudo tal cual. Devuelve filename o None si vacío."""
    if not text or not text.strip():
        return None
    ensure_dirs()
    filename = generate_filename()
    path = config.NOTAS_DIR / filename
    # Colisión mismo segundo (raro): sufijo _1, _2 para no perder datos.
    if path.exists():
        base = filename[:-4]
        i = 1
        while (config.NOTAS_DIR / f"{base}_{i}.txt").exists():
            i += 1
        filename = f"{base}_{i}.txt"
        path = config.NOTAS_DIR / filename
    path.write_text(text, encoding="utf-8")
    return filename


def parse_timestamp_from_filename(filename: str) -> str:
    """'2026-10-03_01-15-00.txt' -> '2026-10-03 01:15:00' (legible)."""
    try:
        stem = filename[:-4] if filename.endswith(".txt") else filename
        # quitar sufijo de colisión "_1"
        core = stem.rsplit("_", 1)[0] if stem.count("_") > 1 and stem.rsplit("_", 1)[1].isdigit() and len(stem.rsplit("_", 1)[0]) == 16 else stem
        # formato esperado: YYYY-MM-DD_HH-MM-SS
        dt = datetime.strptime(core, "%Y-%m-%d_%H-%M-%S")
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    except Exception:
        return filename


def load_index() -> list[dict]:
    path = config.INDEX_PATH
    if not path.exists():
        return []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return data if isinstance(data, list) else []
    except Exception:
        return []


def _save_index_atomic(entries: list[dict]) -> None:
    path = config.INDEX_PATH
    tmp = path.with_suffix(".tmp")
    tmp.write_text(json.dumps(entries, ensure_ascii=False, indent=2), encoding="utf-8")
    os.replace(tmp, path)


def _acquire_lock(timeout: float = 5.0) -> Path:
    """Lock simple por archivo para escrituras concurrentes de workers detached."""
    lock = config.INDEX_PATH.with_suffix(".lock")
    start = time.time()
    while True:
        try:
            fd = os.open(str(lock), os.O_CREAT | os.O_EXCL | os.O_WRONLY)
            os.close(fd)
            return lock
        except FileExistsError:
            if time.time() - start > timeout:
                # lock rancio: lo rompemos
                try:
                    lock.unlink()
                except OSError:
                    pass
            time.sleep(0.05)


def _release_lock(lock: Path) -> None:
    try:
        lock.unlink()
    except OSError:
        pass


def upsert_entry(filename: str, title: str, cleaned_content: str, timestamp: str | None = None) -> None:
    timestamp = timestamp or parse_timestamp_from_filename(filename)
    lock = _acquire_lock()
    try:
        entries = load_index()
        updated = False
        for e in entries:
            if e.get("filename") == filename:
                e["timestamp"] = timestamp
                e["title"] = title
                e["cleaned_content"] = cleaned_content
                updated = True
                break
        if not updated:
            entries.append({
                "filename": filename,
                "timestamp": timestamp,
                "title": title,
                "cleaned_content": cleaned_content,
            })
        _save_index_atomic(entries)
    finally:
        _release_lock(lock)


def get_all_notes_sorted() -> list[dict]:
    """Fusiona índice IA + crudos pendientes. Orden: más RECIENTE primero.

    Pendiente (sin entrada IA): title = filename (temporal), cleaned_content = None.
    """
    ensure_dirs()
    entries = {e.get("filename"): e for e in load_index() if e.get("filename")}
    raws = sorted(
        (p for p in config.NOTAS_DIR.glob("*.txt") if p.is_file()),
        key=lambda p: p.name,
        reverse=True,
    )
    result: list[dict] = []
    for p in raws:
        fn = p.name
        if fn in entries:
            e = entries[fn]
            result.append({
                "filename": fn,
                "timestamp": e.get("timestamp") or parse_timestamp_from_filename(fn),
                "title": e.get("title") or fn,
                "cleaned_content": e.get("cleaned_content"),
                "is_pending": False,
            })
        else:
            result.append({
                "filename": fn,
                "timestamp": parse_timestamp_from_filename(fn),
                "title": fn,  # título temporal hasta que Ollama procese
                "cleaned_content": None,
                "is_pending": True,
            })
    # Por si el índice tiene entradas cuyo .txt fue borrado: se omiten (no hay crudo).
    return result


def read_raw_content(filename: str) -> str:
    try:
        return (config.NOTAS_DIR / filename).read_text(encoding="utf-8")
    except Exception:
        return ""


def get_display_content(note: dict) -> str:
    """Contenido para el visor: versión IA si existe, si no el crudo."""
    if note.get("cleaned_content"):
        return note["cleaned_content"]
    return read_raw_content(note.get("filename", ""))
