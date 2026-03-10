"""Provedor Ollama (Llama local)."""
from .base import LLMProvider
import config


class OllamaProvider(LLMProvider):
    def __init__(self):
        self.client = None
        try:
            from ollama import Client
            self.client = Client(host=config.OLLAMA_BASE_URL)
        except ImportError:
            pass

    def is_available(self):
        if not self.client:
            return False
        try:
            self.client.list()
            return True
        except Exception:
            return False

    def chat(self, messages, model=None):
        if not self.client:
            raise RuntimeError("Ollama nao instalado. Instale: pip install ollama")

        model = model or "llama3.2"
        if model not in config.MODELS["ollama"]:
            model = config.MODELS["ollama"][0]

        response = self.client.chat(model=model, messages=messages)
        return response["message"]["content"]
