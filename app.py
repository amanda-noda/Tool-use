#!/usr/bin/env python3
"""
Assistente Pessoal - Interface Web Interativa
Execute: python app.py
"""
import sys
import html
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

import gradio as gr
from assistant import PersonalAssistant


def create_chat_fn(assistant):
    """Cria uma funcao de chat que mantem o estado do assistente."""
    def chat(message, history):
        history = history or []
        try:
            response = assistant.chat(message)
            return response
        except Exception as e:
            return f"Erro: {str(e)}"
    return chat


def main():
    try:
        assistant = PersonalAssistant()
    except RuntimeError as e:
        print(f"Erro ao iniciar: {e}")
        print("Configure OPENAI_API_KEY, ANTHROPIC_API_KEY ou execute Ollama.")
        sys.exit(1)

    status = assistant.get_status()
    status_text = " | ".join(f"{k}: {v}" for k, v in status.items())

    custom_css = """
    /* Paleta azul-verde fluida - tons suaves e harmoniosos */
    @keyframes gradient-shift {
        0%, 100% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
    }

    @keyframes fade-in {
        from { opacity: 0; transform: translateY(-10px); }
        to { opacity: 1; transform: translateY(0); }
    }

    .gradio-container {
        background: linear-gradient(-45deg, #0c1929, #0d2137, #0f2847, #0a1628, #0e2439) !important;
        background-size: 400% 400% !important;
        animation: gradient-shift 15s ease infinite !important;
        min-height: 100vh;
        padding: 2rem !important;
    }

    .header-card {
        background: linear-gradient(135deg,
            rgba(13, 71, 161, 0.2) 0%,
            rgba(0, 150, 136, 0.25) 35%,
            rgba(0, 188, 212, 0.2) 70%,
            rgba(2, 119, 189, 0.15) 100%);
        border: 1px solid rgba(0, 229, 255, 0.25);
        border-radius: 24px;
        padding: 2.5rem;
        margin-bottom: 1.5rem;
        backdrop-filter: blur(16px);
        box-shadow: 0 12px 40px rgba(0, 0, 0, 0.25), inset 0 1px 0 rgba(255,255,255,0.05);
        animation: fade-in 0.6s ease-out;
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }

    .header-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 16px 48px rgba(0, 0, 0, 0.3), inset 0 1px 0 rgba(255,255,255,0.08);
    }

    .header-card h1 {
        background: linear-gradient(135deg, #4dd0e1 0%, #26c6da 25%, #00bcd4 50%, #00acc1 75%, #0097a7 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        font-size: 2.4rem !important;
        font-weight: 700 !important;
        margin-bottom: 0.6rem !important;
        letter-spacing: -0.02em;
    }

    .header-card p {
        color: #b2ebf2 !important;
        font-size: 1.05rem;
        opacity: 0.95;
        line-height: 1.6;
    }

    .status-badge {
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
        background: linear-gradient(135deg, rgba(0, 151, 167, 0.35), rgba(3, 169, 244, 0.25));
        border: 1px solid rgba(77, 208, 225, 0.4);
        border-radius: 14px;
        padding: 0.6rem 1.2rem;
        color: #e0f7fa;
        font-size: 0.9rem;
        margin-top: 1.2rem;
        font-weight: 500;
    }

    /* Area do chat - cards fluidos */
    .gradio-container [class*="block"] {
        background: linear-gradient(180deg, rgba(13, 71, 161, 0.08) 0%, rgba(0, 96, 100, 0.12) 100%) !important;
        border-radius: 20px !important;
        border: 1px solid rgba(0, 188, 212, 0.15) !important;
        padding: 1.5rem !important;
    }

    /* Input - estilo aqua/teal */
    .gradio-container textarea {
        background: rgba(0, 96, 100, 0.25) !important;
        border: 1px solid rgba(0, 188, 212, 0.35) !important;
        border-radius: 14px !important;
        color: #e0f7fa !important;
        transition: border-color 0.3s, box-shadow 0.3s !important;
    }

    .gradio-container textarea:focus {
        border-color: rgba(0, 229, 255, 0.6) !important;
        box-shadow: 0 0 0 3px rgba(0, 188, 212, 0.2) !important;
    }

    .gradio-container textarea::placeholder {
        color: #80deea !important;
        opacity: 0.8;
    }

    /* Botoes - gradiente azul-verde */
    .gradio-container button {
        background: linear-gradient(135deg, #00838f 0%, #006064 50%, #004d40 100%) !important;
        border: 1px solid rgba(0, 229, 255, 0.3) !important;
        border-radius: 12px !important;
        color: #e0f7fa !important;
        transition: all 0.3s ease !important;
    }

    .gradio-container button:hover {
        background: linear-gradient(135deg, #0097a7 0%, #00838f 50%, #00695c 100%) !important;
        border-color: rgba(0, 229, 255, 0.5) !important;
        transform: translateY(-1px);
    }

    footer { display: none !important; }
    """

    demo = gr.Blocks(
        title="Assistente Pessoal",
        css=custom_css,
    )

    with demo:
        gr.HTML("""
        <div class="header-card">
            <div style="width:60px;height:4px;background:linear-gradient(90deg,#4dd0e1,#00bcd4);border-radius:2px;margin-bottom:1rem;"></div>
            <h1>Assistente Pessoal</h1>
            <p>Converse ou peca tarefas: calendario, e-mails, pesquisa web, resumos.</p>
            <div class="status-badge">Status: """ + html.escape(status_text) + """</div>
        </div>
        """)

        gr.ChatInterface(
            fn=create_chat_fn(assistant),
            title="",
            description="",
            examples=[
                "O que tenho no calendario esta semana?",
                "Pesquise noticias sobre inteligencia artificial",
                "Resuma o conteudo de https://exemplo.com",
            ],
        )

    demo.launch(
        server_name="127.0.0.1",
        server_port=8765,
        share=False,
    )


if __name__ == "__main__":
    main()
