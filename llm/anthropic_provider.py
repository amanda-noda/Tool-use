"""Provedor Anthropic (Claude)."""
from .base import LLMProvider
import config


class AnthropicProvider(LLMProvider):
    def __init__(self):
        self.client = None
        if config.ANTHROPIC_API_KEY:
            from anthropic import Anthropic
            self.client = Anthropic(api_key=config.ANTHROPIC_API_KEY)

    def is_available(self):
        return self.client is not None

    def chat(self, messages, model=None):
        if not self.is_available():
            raise RuntimeError("Anthropic API key nao configurada. Defina ANTHROPIC_API_KEY no .env")

        model = model or config.DEFAULT_MODEL
        if model not in config.MODELS["anthropic"]:
            model = config.MODELS["anthropic"][0]

        system = ""
        anthropic_messages = []
        for msg in messages:
            if msg["role"] == "system":
                system = msg["content"]
            else:
                anthropic_messages.append({"role": msg["role"], "content": msg["content"]})

        kwargs = {"model": model, "max_tokens": 4096, "messages": anthropic_messages}
        if system:
            kwargs["system"] = system

        response = self.client.messages.create(**kwargs)
        return response.content[0].text
