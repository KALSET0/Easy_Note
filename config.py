# Easy_Note — configuración central
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
NOTAS_DIR = BASE_DIR / "notas"
INDEX_PATH = BASE_DIR / "notes_index.json"

# IA local (Ollama)
MODEL = "qwen2.5:7b-instruct-q4_K_M"
OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_CHAT_URL = "http://localhost:11434/api/chat"
OLLAMA_TAGS_URL = "http://localhost:11434/api/tags"
TEMPERATURE = 0.2
NUM_PREDICT = 700  # consumo reducido de tokens

SYSTEM_PROMPT = """Tu tarea es revisar la nota recibida.
REGLAS STRICTAS:
1. NO cambies el significado, el vocabulario, las palabras del usuario ni la información.
2. Corrige únicamente errores ortográficos, typos y saltos de línea para que se vea limpio y legible.
3. Genera un Título muy corto y preciso (máximo 6 palabras) basado en el contenido.
Responde ÚNICAMENTE con este JSON exacto, sin markdown ni texto extra:
{
  "title": "Título sugerido aquí",
  "cleaned_text": "Texto corregido y ordenado aquí"
}"""
