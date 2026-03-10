"""Factory para provedores de LLM."""
import config
from .openai_provider import OpenAIProvider
from .anthropic_provider import AnthropicProvider
from .ollama_provider import OllamaProvider


def get_llm_provider(model_hint=None):
    providers = [
        OpenAIProvider(),
        AnthropicProvider(),
        OllamaProvider(),
    ]

    if model_hint:
        for p in providers:
            if model_hint in config.MODELS.get("openai", []) and isinstance(p, OpenAIProvider):
                if p.is_available():
                    return p
            if model_hint in config.MODELS.get("anthropic", []) and isinstance(p, AnthropicProvider):
                if p.is_available():
                    return p
            if model_hint in config.MODELS.get("ollama", []) and isinstance(p, OllamaProvider):
                if p.is_available():
                    return p

    for p in providers:
        if p.is_available():
            return p

    raise RuntimeError(
        "Nenhum provedor de LLM disponivel. Configure OPENAI_API_KEY, ANTHROPIC_API_KEY "
        "ou execute Ollama localmente."
    )
