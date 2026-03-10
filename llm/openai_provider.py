"""Provedor OpenAI (GPT)."""
from .base import LLMProvider
import config


class OpenAIProvider(LLMProvider):
    def __init__(self):
        self.client = None
        if config.OPENAI_API_KEY:
            from openai import OpenAI
            self.client = OpenAI(api_key=config.OPENAI_API_KEY)

    def is_available(self):
        return self.client is not None

    def chat(self, messages, model=None):
        if not self.is_available():
            raise RuntimeError("OpenAI API key nao configurada. Defina OPENAI_API_KEY no .env")

        model = model or config.DEFAULT_MODEL
        if model not in config.MODELS["openai"]:
            model = config.MODELS["openai"][0]

        response = self.client.chat.completions.create(
            model=model,
            messages=messages,
        )
        return response.choices[0].message.content
