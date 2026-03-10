"""Configuracao do assistente pessoal."""
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).parent
CREDENTIALS_DIR = BASE_DIR / "credentials"
CREDENTIALS_DIR.mkdir(exist_ok=True)

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
DEFAULT_MODEL = os.getenv("DEFAULT_MODEL", "gpt-4o-mini")

GOOGLE_CALENDAR_ENABLED = os.getenv("GOOGLE_CALENDAR_ENABLED", "false").lower() == "true"
GOOGLE_EMAIL_ENABLED = os.getenv("GOOGLE_EMAIL_ENABLED", "false").lower() == "true"
GOOGLE_CREDENTIALS_PATH = CREDENTIALS_DIR / "credentials.json"
GOOGLE_CALENDAR_TOKEN_PATH = CREDENTIALS_DIR / "token_calendar.json"
GOOGLE_EMAIL_TOKEN_PATH = CREDENTIALS_DIR / "token_email.json"

MODELS = {
    "openai": ["gpt-4o", "gpt-4o-mini", "gpt-4-turbo"],
    "anthropic": ["claude-3-5-sonnet-20241022", "claude-3-5-haiku-20241022", "claude-3-opus-20240229"],
    "ollama": ["llama3.2", "llama3.1", "mistral", "codellama"],
}
