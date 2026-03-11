"""Ferramenta de pesquisa web e resumo."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))


def _get_demo_results(query: str) -> str:
    """Retorna resultados de demonstracao quando a pesquisa nao esta disponivel."""
    demo = [
        ("Wikipedia - " + query, "https://pt.wikipedia.org/wiki/" + query.replace(" ", "_"), "Artigo sobre o tema na enciclopedia livre."),
        ("Google - " + query, "https://www.google.com/search?q=" + query.replace(" ", "+"), "Resultados de busca no Google."),
        ("Noticias - " + query, "https://news.google.com/search?q=" + query.replace(" ", "+"), "Ultimas noticias relacionadas ao termo."),
    ]
    lines = [f"- {t}\n  {u}\n  {b}" for t, u, b in demo]
    return f"Resultados para '{query}' (modo demonstracao):\n\n" + "\n\n".join(lines)


class WebTool:
    def __init__(self):
        self._ddg_available = None

    def _check_ddg(self):
        if self._ddg_available is None:
            try:
                from duckduckgo_search import DDGS
                with DDGS() as _:
                    pass
                self._ddg_available = True
            except Exception:
                self._ddg_available = False
        return self._ddg_available

    def search(self, query, max_results=5):
        if not self._check_ddg():
            return _get_demo_results(query)
        try:
            from duckduckgo_search import DDGS
            results = []
            with DDGS() as ddgs:
                for r in ddgs.text(query, max_results=max_results):
                    results.append(f"- {r['title']}\n  {r['href']}\n  {r.get('body', '')[:200]}...")
            return "\n\n".join(results) if results else _get_demo_results(query)
        except Exception:
            return _get_demo_results(query)

    def _extract_text_from_url(self, url):
        """Extrai texto de uma URL."""
        import requests
        from bs4 import BeautifulSoup
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
        resp = requests.get(url, headers=headers, timeout=10)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")
        for tag in soup(["script", "style", "nav", "footer"]):
            tag.decompose()
        return soup.get_text(separator="\n", strip=True)[:8000]

    def _demo_summary(self, text, source="texto"):
        """Resumo simplificado para modo demonstracao (sem LLM)."""
        text = (text or "").strip()
        if not text:
            return "Nenhum conteudo para resumir."
        preview = text[:500].rstrip()
        if len(text) > 500:
            preview += "..."
        return f"**Resumo do {source} (modo demonstracao):**\n\n{preview}\n\n_Configure OPENAI_API_KEY no .env para resumos com IA._"

    def summarize_text(self, text, llm_chat_func=None):
        """Resume um texto. Usa LLM se disponivel, senao modo demo."""
        text = (text or "").strip()
        if not text:
            return "Nenhum texto para resumir."
        if llm_chat_func:
            try:
                summary = llm_chat_func([
                    {"role": "system", "content": "Resuma o conteudo de forma clara e concisa em portugues."},
                    {"role": "user", "content": f"Resuma:\n\n{text[:6000]}"},
                ])
                return f"**Resumo:**\n\n{summary}"
            except Exception:
                pass
        return self._demo_summary(text, "texto")

    def fetch_and_summarize(self, url, llm_chat_func=None):
        """Busca e resume o conteudo de uma URL."""
        try:
            text = self._extract_text_from_url(url)
            if not text:
                return "Nao foi possivel extrair texto da pagina."
            if llm_chat_func:
                try:
                    summary = llm_chat_func([
                        {"role": "system", "content": "Resuma o conteudo de forma clara e concisa em portugues."},
                        {"role": "user", "content": f"Resuma:\n\n{text[:6000]}"},
                    ])
                    return f"**Resumo de {url}:**\n\n{summary}"
                except Exception:
                    pass
            return self._demo_summary(text, f"pagina {url}")
        except Exception as e:
            return f"Erro: {e}"
