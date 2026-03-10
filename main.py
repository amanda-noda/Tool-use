#!/usr/bin/env python3
"""Assistente Pessoal - Ponto de entrada."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown

from assistant import PersonalAssistant


def main():
    console = Console()

    console.print(Panel.fit(
        "[bold cyan]Assistente Pessoal[/]\n"
        "Converse ou peca tarefas: calendario, e-mails, pesquisa web, resumos.",
        border_style="cyan",
    ))

    try:
        assistant = PersonalAssistant()
    except RuntimeError as e:
        console.print(f"[red]Erro: {e}[/]")
        console.print("\nConfigure pelo menos um provedor no .env:")
        console.print("  - OPENAI_API_KEY para GPT")
        console.print("  - ANTHROPIC_API_KEY para Claude")
        console.print("  - Ou execute ollama run llama3.2 para Llama local")
        return 1

    status = assistant.get_status()
    console.print("\n[dim]Status: " + " | ".join(f"{k}: {v}" for k, v in status.items()) + "[/]\n")

    console.print("[dim]Digite 'sair' para encerrar. Exemplos:[/]")
    console.print("  - O que tenho no calendario esta semana?")
    console.print("  - Pesquise noticias sobre inteligencia artificial")
    console.print("  - Resuma o conteudo de https://exemplo.com")
    console.print("  - Envie um e-mail para joao@email.com com assunto Teste\n")

    while True:
        try:
            user_input = console.input("[bold green]Voce:[/] ").strip()
        except (KeyboardInterrupt, EOFError):
            break

        if not user_input:
            continue
        if user_input.lower() in ("sair", "exit", "quit"):
            console.print("[cyan]Ate logo![/]")
            break

        try:
            response = assistant.chat(user_input)
            console.print(Panel(Markdown(response), title="Assistente", border_style="blue"))
        except Exception as e:
            console.print(f"[red]Erro: {e}[/]")

    return 0


if __name__ == "__main__":
    sys.exit(main())
