"""Ferramenta de pesquisa web e resumo."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))


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
            return "Pesquisa web nao disponivel."
        try:
            from duckduckgo_search import DDGS
            results = []
            with DDGS() as ddgs:
                for r in ddgs.text(query, max_results=max_results):
                    results.append(f"- {r['title']}\n  {r['href']}\n  {r.get('body', '')[:200]}...")
            return "\n\n".join(results) if results else "Nenhum resultado."
        except Exception as e:
            return f"Erro: {e}"

    def fetch_and_summarize(self, url, llm_chat_func):
        try:
            import requests
            from bs4 import BeautifulSoup
            headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
            resp = requests.get(url, headers=headers, timeout=10)
            resp.raise_for_status()
            soup = BeautifulSoup(resp.text, "html.parser")
            for tag in soup(["script", "style", "nav", "footer"]):
                tag.decompose()
            text = soup.get_text(separator="\n", strip=True)[:8000]
            if not text:
                return "Nao foi possivel extrair texto."
            summary = llm_chat_func([
                {"role": "system", "content": "Resuma o conteudo de forma clara e concisa em portugues."},
                {"role": "user", "content": f"Resuma:\n\n{text[:6000]}"},
            ])
            return f"**Resumo de {url}:**\n\n{summary}"
        except Exception as e:
            return f"Erro: {e}"
