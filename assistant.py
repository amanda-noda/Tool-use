"""Assistente Pessoal - Orquestrador principal."""
import re
import config
from llm.factory import get_llm_provider
from tools.calendar_tool import CalendarTool
from tools.email_tool import EmailTool
from tools.web_tool import WebTool


SYSTEM_PROMPT = """Voce e um assistente pessoal util que pode realizar tarefas reais.

Voce tem acesso as seguintes ferramentas (use os comandos exatamente como mostrado):

1. CALENDARIO [dias] - Consulta eventos do calendario. Ex: CALENDARIO 7
2. PESQUISAR [query] - Pesquisa na web. Ex: PESQUISAR noticias sobre IA
3. RESUMIR [url] - Busca e resume o conteudo de uma URL. Ex: RESUMIR https://exemplo.com
4. EMAIL [destinatario] [assunto] [corpo] - Envia e-mail. Use | para separar: EMAIL joao@email.com | Assunto | Corpo da mensagem

Quando o usuario pedir algo que envolva essas acoes, use o comando apropriado.
Se nao precisar de ferramenta, responda diretamente.
Seja conciso e util. Responda em portugues."""


class PersonalAssistant:
    """Assistente pessoal com acesso a ferramentas."""

    def __init__(self, model=None):
        self.llm = get_llm_provider(model)
        self.calendar = CalendarTool()
        self.email = EmailTool()
        self.web = WebTool()
        self.history = []

    def _extract_tool_call(self, response):
        tool = None
        args = []

        if re.search(r"CALENDARIO\s+(\d+)", response, re.I):
            m = re.search(r"CALENDARIO\s+(\d+)", response, re.I)
            tool = "calendar"
            args = [int(m.group(1))] if m else [7]
        elif re.search(r"PESQUISAR\s+", response, re.I):
            m = re.search(r"PESQUISAR\s+(.+?)(?:\n|$)", response, re.I | re.DOTALL)
            tool = "search"
            args = [m.group(1).strip()[:200]] if m and m.group(1).strip() else []
        elif re.search(r"RESUMIR\s+https?://", response, re.I):
            m = re.search(r"RESUMIR\s+(https?://\S+)", response, re.I)
            tool = "summarize"
            args = [m.group(1)] if m else []
        elif re.search(r"EMAIL\s+[\w.@-]+", response, re.I):
            m = re.search(r"EMAIL\s+([\w.@-]+)\s*\|\s*(.+?)\s*\|\s*(.+)", response, re.I | re.DOTALL)
            if m:
                tool = "email"
                args = [m.group(1).strip(), m.group(2).strip(), m.group(3).strip()]

        return tool, args

    def _run_tool(self, tool, args):
        if tool == "calendar":
            days = args[0] if args else 7
            return self.calendar.get_events(days_ahead=days)
        elif tool == "search":
            query = args[0] if args else ""
            return self.web.search(query)
        elif tool == "summarize":
            url = args[0] if args else ""
            return self.web.fetch_and_summarize(url, self.llm.chat)
        elif tool == "email":
            if len(args) >= 3:
                return self.email.send_email(args[0], args[1], args[2])
            return "Formato: EMAIL destinatario | assunto | corpo"
        return "Ferramenta desconhecida"

    def chat(self, user_message, max_tool_rounds=3):
        self.history.append({"role": "user", "content": user_message})

        messages = [{"role": "system", "content": SYSTEM_PROMPT}]
        tools_desc = []
        if self.calendar.is_available():
            tools_desc.append("- CALENDARIO: consultar eventos")
        if self.email.is_available():
            tools_desc.append("- EMAIL: enviar e-mails")
        tools_desc.append("- PESQUISAR: buscar na web")
        tools_desc.append("- RESUMIR: resumir pagina web")
        messages[0]["content"] += "\n\nFerramentas disponiveis:\n" + "\n".join(tools_desc)

        messages.extend(self.history)

        for _ in range(max_tool_rounds):
            response = self.llm.chat(messages)
            tool, args = self._extract_tool_call(response)

            if tool is None:
                self.history.append({"role": "assistant", "content": response})
                return response

            result = self._run_tool(tool, args)
            messages.append({"role": "assistant", "content": response})
            messages.append({
                "role": "user",
                "content": f"[Resultado da ferramenta {tool}]: {result}\n\nAgora responda ao usuario com base nisso.",
            })

        final = self.llm.chat(messages)
        self.history.append({"role": "assistant", "content": final})
        return final

    def get_status(self):
        return {
            "llm": "OK",
            "calendario": "OK" if self.calendar.is_available() else "Nao configurado",
            "e-mail": "OK" if self.email.is_available() else "Nao configurado",
            "pesquisa web": "OK",
        }
