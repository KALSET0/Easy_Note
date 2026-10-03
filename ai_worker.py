"""Worker IA detached: `python ai_worker.py <filename>`.

Sobrevive al cierre de la app (lanzado con DETACHED_PROCESS).
Si Ollama no está corriendo -> sale en silencio, el crudo queda pendiente.
"""
import json
import re
import subprocess
import sys
import threading
from pathlib import Path

import config
import storage


def _extract_json(text: str) -> dict | None:
    """Extrae el primer objeto JSON válido, tolerando fences ```json."""
    if not text:
        return None
    cleaned = re.sub(r"```(?:json)?", "", text).strip()
    # Intento directo
    try:
        obj = json.loads(cleaned)
        if isinstance(obj, dict):
            return obj
    except Exception:
        pass
    # Primer {...} balanceado simple: buscar el bloque más grande
    start = cleaned.find("{")
    end = cleaned.rfind("}")
    if start != -1 and end != -1 and end > start:
        try:
            obj = json.loads(cleaned[start:end + 1])
            if isinstance(obj, dict):
                return obj
        except Exception:
            return None
    return None


def _call_ollama_lib(prompt_text: str) -> str:
    import ollama
    resp = ollama.chat(
        model=config.MODEL,
        format="json",
        options={"temperature": config.TEMPERATURE, "num_predict": config.NUM_PREDICT},
        messages=[
            {"role": "system", "content": config.SYSTEM_PROMPT},
            {"role": "user", "content": prompt_text},
        ],
    )
    msg = resp.get("message", {}) if isinstance(resp, dict) else {}
    content = msg.get("content", "") if isinstance(msg, dict) else ""
    if not content and hasattr(resp, "message"):
        content = getattr(resp.message, "content", "") or ""
    return content


def _call_ollama_http(prompt_text: str) -> str:
    import requests
    payload = {
        "model": config.MODEL,
        "prompt": f"{config.SYSTEM_PROMPT}\n\nNOTA DEL USUARIO:\n{prompt_text}\n\nResponde SOLO el JSON.",
        "stream": False,
        "format": "json",
        "options": {"temperature": config.TEMPERATURE, "num_predict": config.NUM_PREDICT},
    }
    r = requests.post(config.OLLAMA_URL, json=payload, timeout=300)
    r.raise_for_status()
    return r.json().get("response", "")


def _short_title(title: str, filename: str) -> str:
    words = (title or "").strip().split()
    if not words:
        return filename
    return " ".join(words[:6])


def process_note_file(filename: str) -> bool:
    """Procesa un crudo con Ollama y actualiza el índice. False si pendiente."""
    raw = storage.read_raw_content(filename)
    if not raw.strip():
        return False
    try:
        try:
            content = _call_ollama_lib(raw)
        except Exception:
            content = _call_ollama_http(raw)
    except Exception:
        return False  # Ollama caído -> el crudo se conserva, queda pendiente
    data = _extract_json(content)
    if not data:
        return False
    cleaned = data.get("cleaned_text", data.get("cleaned_content", "")) or ""
    title = _short_title(str(data.get("title", "")), filename)
    if not cleaned.strip():
        return False
    storage.upsert_entry(filename, title, cleaned.strip())
    return True


def ping_ollama(timeout: float = 1.5) -> bool:
    try:
        import requests
        r = requests.get(config.OLLAMA_TAGS_URL, timeout=timeout)
        return r.status_code == 200
    except Exception:
        return False


def launch_ai_background(filename: str) -> None:
    """Lanza el worker detached que sobrevive al cierre. Fallback a hilo daemon."""
    worker = str(Path(__file__).resolve())
    try:
        kwargs: dict = {
            "stdout": subprocess.DEVNULL,
            "stderr": subprocess.DEVNULL,
            "stdin": subprocess.DEVNULL,
            "close_fds": True,
        }
        if sys.platform == "win32":
            # DETACHED_PROCESS | CREATE_NEW_PROCESS_GROUP
            kwargs["creationflags"] = 0x00000008 | 0x00000200
        else:
            kwargs["start_new_session"] = True
        subprocess.Popen([sys.executable, worker, filename], **kwargs)
    except Exception:
        t = threading.Thread(target=process_note_file, args=(filename,), daemon=True)
        t.start()


def main(argv: list[str]) -> int:
    if len(argv) < 2 or not argv[1]:
        print("Uso: python ai_worker.py <filename>", file=sys.stderr)
        return 2
    ok = process_note_file(argv[1])
    return 0 if ok else 0  # 0 siempre: pendiente no es error fatal


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
