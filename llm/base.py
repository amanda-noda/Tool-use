"""Interface base para provedores de LLM."""
from abc import ABC, abstractmethod


class LLMProvider(ABC):
    @abstractmethod
    def chat(self, messages, model=None):
        pass

    @abstractmethod
    def is_available(self):
        pass
