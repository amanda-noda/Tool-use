#!/usr/bin/env python3
"""
Assistente Pessoal - Interface Web (estilo ChatGPT)
Execute: python app.py
"""
import sys
import html
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

import gradio as gr
from assistant import PersonalAssistant


def chat_fn(message, history, assistant):
    """Processa mensagem e retorna resposta do assistente."""
    try:
        response = assistant.chat(message)
        return response
    except Exception as e:
        return f"Erro: {str(e)}"


def main():
    assistant = None
    try:
        assistant = PersonalAssistant()
    except RuntimeError as e:
        print(f"Aviso: {e}")
        print("Iniciando em modo demo - configure .env para usar o assistente.")
        class DemoAssistant:
            def chat(self, msg): return "Configure OPENAI_API_KEY no arquivo .env para usar o assistente."
            def get_status(self): return {"llm": "Nao configurado", "calendario": "-", "e-mail": "-", "pesquisa web": "-"}
        assistant = DemoAssistant()

    status = assistant.get_status()
    status_items = "".join(
        f'<span class="status-item">{html.escape(k)}: <strong>{html.escape(str(v))}</strong></span>'
        for k, v in status.items()
    )

    custom_css = """
    /* === Interface criativa e fluida === */
    @keyframes gradient-flow {
        0%, 100% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
    }

    @keyframes float-slow {
        0%, 100% { transform: translate(0, 0) scale(1); }
        33% { transform: translate(10px, -20px) scale(1.02); }
        66% { transform: translate(-5px, 10px) scale(0.98); }
    }

    @keyframes fade-slide {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }

    @keyframes pulse-glow {
        0%, 100% { box-shadow: 0 0 20px rgba(0, 188, 212, 0.2); }
        50% { box-shadow: 0 0 40px rgba(0, 188, 212, 0.35); }
    }

    @keyframes shimmer {
        0% { background-position: -200% 0; }
        100% { background-position: 200% 0; }
    }

    .gradio-container {
        background: linear-gradient(135deg, #0a0e1a 0%, #0d1525 25%, #0f1a2e 50%, #0a1628 75%, #0c1328 100%) !important;
        background-size: 400% 400% !important;
        animation: gradient-flow 20s ease infinite !important;
        min-height: 100vh;
        padding: 0 !important;
    }

    /* Sidebar - glassmorphism */
    .sidebar {
        background: linear-gradient(180deg,
            rgba(13, 71, 161, 0.12) 0%,
            rgba(0, 96, 100, 0.08) 50%,
            rgba(0, 150, 136, 0.05) 100%) !important;
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        border-right: 1px solid rgba(0, 188, 212, 0.2) !important;
        padding: 1.5rem 0 !important;
        min-height: 100vh;
        animation: fade-slide 0.8s ease-out;
    }

    .sidebar .logo {
        display: flex;
        align-items: center;
        gap: 0.75rem;
        padding: 1rem 1.5rem;
        color: #e0f7fa;
        font-size: 1.2rem;
        font-weight: 700;
        letter-spacing: -0.02em;
    }

    .sidebar .logo-icon {
        width: 36px;
        height: 36px;
        background: linear-gradient(135deg, #00e5ff 0%, #00bcd4 50%, #0097a7 100%);
        border-radius: 12px;
        box-shadow: 0 4px 24px rgba(0, 188, 212, 0.4);
        animation: pulse-glow 3s ease-in-out infinite;
    }

    .sidebar .nav-item {
        display: flex;
        align-items: center;
        gap: 0.75rem;
        padding: 0.85rem 1.5rem;
        margin: 0.25rem 0.75rem;
        color: #b2ebf2;
        font-size: 0.95rem;
        border-radius: 12px;
        border-left: 3px solid transparent;
        transition: all 0.35s cubic-bezier(0.4, 0, 0.2, 1);
    }

    .sidebar .nav-item:hover {
        background: linear-gradient(90deg, rgba(0, 188, 212, 0.15), transparent);
        border-left-color: #00e5ff;
        color: #e0f7fa;
        transform: translateX(4px);
    }

    .sidebar .nav-divider {
        height: 1px;
        background: linear-gradient(90deg, transparent, rgba(0, 188, 212, 0.3), transparent);
        margin: 1rem 1.5rem;
    }

    .sidebar .status-box {
        margin: 1rem 1rem;
        padding: 1.25rem;
        background: linear-gradient(135deg, rgba(0, 151, 167, 0.2), rgba(0, 96, 100, 0.15));
        border: 1px solid rgba(0, 229, 255, 0.25);
        border-radius: 16px;
        box-shadow: 0 4px 24px rgba(0, 0, 0, 0.15);
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }

    .sidebar .status-box:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 32px rgba(0, 188, 212, 0.2);
    }

    .sidebar .status-box .status-title {
        color: #80deea;
        font-size: 0.75rem;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        margin-bottom: 0.75rem;
    }

    .sidebar .status-box .status-item {
        display: block;
        color: #b2ebf2;
        font-size: 0.85rem;
        margin: 0.4rem 0;
        padding: 0.2rem 0;
    }

    /* Area principal */
    #main-content {
        animation: fade-slide 0.6s ease-out 0.2s both;
    }

    #welcome-title h3 {
        background: linear-gradient(135deg, #e0f7fa 0%, #80deea 50%, #4dd0e1 100%) !important;
        -webkit-background-clip: text !important;
        -webkit-text-fill-color: transparent !important;
        background-clip: text !important;
        font-size: 2rem !important;
        font-weight: 700 !important;
        letter-spacing: -0.03em !important;
        margin-bottom: 0.5rem !important;
    }

    /* Input - fluido */
    #main-content textarea {
        background: linear-gradient(135deg, rgba(0, 96, 100, 0.2) 0%, rgba(13, 71, 161, 0.15) 100%) !important;
        border: 1px solid rgba(0, 188, 212, 0.35) !important;
        border-radius: 28px !important;
        color: #e0f7fa !important;
        padding: 1rem 1.5rem !important;
        font-size: 1rem !important;
        min-height: 56px !important;
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1) !important;
    }

    #main-content textarea:focus {
        border-color: rgba(0, 229, 255, 0.6) !important;
        box-shadow: 0 0 0 3px rgba(0, 188, 212, 0.25), 0 8px 32px rgba(0, 0, 0, 0.2) !important;
        transform: translateY(-1px);
    }

    #main-content textarea::placeholder {
        color: #80deea !important;
        opacity: 0.8;
    }

    /* Chatbot - mensagens fluidas */
    .chatbot .message {
        border-radius: 20px !important;
        transition: all 0.3s ease !important;
    }

    .chatbot .message:hover {
        transform: scale(1.01);
    }

    .chatbot .message.user {
        background: linear-gradient(135deg, rgba(0, 150, 136, 0.3) 0%, rgba(0, 188, 212, 0.25) 0%, rgba(3, 169, 244, 0.2) 100%) !important;
        border: 1px solid rgba(0, 229, 255, 0.3) !important;
        box-shadow: 0 4px 20px rgba(0, 188, 212, 0.15) !important;
    }

    .chatbot .message.bot {
        background: linear-gradient(135deg, rgba(22, 27, 34, 0.9) 0%, rgba(13, 71, 161, 0.1) 100%) !important;
        border: 1px solid rgba(0, 188, 212, 0.2) !important;
        box-shadow: 0 4px 24px rgba(0, 0, 0, 0.2) !important;
    }

    /* Footer */
    .app-footer {
        padding: 1rem 2rem;
        text-align: center;
        color: #8b949e;
        font-size: 0.8rem;
        background: linear-gradient(180deg, transparent, rgba(0, 0, 0, 0.2));
        border-top: 1px solid rgba(0, 188, 212, 0.1);
    }

    /* Botao */
    .gradio-container button.primary {
        background: linear-gradient(135deg, #00bcd4 0%, #0097a7 50%, #00838f 100%) !important;
        border: none !important;
        color: #fff !important;
        border-radius: 16px !important;
        font-weight: 600 !important;
        transition: all 0.35s cubic-bezier(0.4, 0, 0.2, 1) !important;
        box-shadow: 0 4px 20px rgba(0, 188, 212, 0.3) !important;
    }

    .gradio-container button.primary:hover {
        background: linear-gradient(135deg, #00e5ff 0%, #00bcd4 50%, #0097a7 100%) !important;
        transform: translateY(-2px);
        box-shadow: 0 8px 32px rgba(0, 188, 212, 0.4) !important;
    }

    .gradio-container footer,
    footer[class*="footer"],
    .gradio-container [class*="footer"] {
        display: none !important;
    }
    """

    sidebar_html = f"""
    <div class="sidebar">
        <div class="logo">
            <div class="logo-icon"></div>
            <span>Assistente Pessoal</span>
        </div>
        <div class="nav-divider"></div>
        <div class="nav-item">&#9998; Novo chat</div>
        <div class="nav-item">&#128269; Buscar em chats</div>
        <div class="nav-item">&#128197; Calendario</div>
        <div class="nav-item">&#128231; E-mail</div>
        <div class="nav-item">&#128269; Pesquisa web</div>
        <div class="nav-divider"></div>
        <div class="status-box">
            <div class="status-title">Status do sistema</div>
            {status_items}
        </div>
    </div>
    """

    footer_html = """
    <div class="app-footer">
        Ao usar o Assistente Pessoal, voce concorda com os termos de uso. 
        Suas conversas sao processadas localmente.
    </div>
    """

    welcome_html = """
    <div style="text-align:center; margin-bottom:2rem;">
        <p style="color:#80deea; font-size:0.95rem; opacity:0.9; margin-top:0.5rem;">
            Calendario • E-mail • Pesquisa • Resumos
        </p>
    </div>
    """

    with gr.Blocks(title="Assistente Pessoal") as demo:
        with gr.Row(elem_id="main-row"):
            # Sidebar
            with gr.Column(scale=1, min_width=240):
                gr.HTML(sidebar_html)

            # Area principal
            with gr.Column(scale=4):
                with gr.Group(elem_id="main-content"):
                    gr.Markdown("### Como posso ajudar?", elem_id="welcome-title")
                    gr.HTML(welcome_html)
                    chatbot = gr.Chatbot(
                        label="",
                        height=450,
                        show_label=False,
                    )
                    with gr.Row():
                        msg = gr.Textbox(
                            placeholder="Digite sua mensagem... calendario, e-mail, pesquisa ou resumos",
                            show_label=False,
                            scale=9,
                            container=False,
                        )
                        submit_btn = gr.Button("Enviar", scale=1, elem_classes=["primary"])

        gr.HTML(footer_html)

        def respond(message, chat_history):
            if not message.strip():
                return chat_history
            chat_history = chat_history or []
            chat_history.append([message, ""])
            response = chat_fn(message, chat_history, assistant)
            chat_history[-1][1] = response
            return chat_history

        msg.submit(respond, [msg, chatbot], [chatbot]).then(
            lambda: "", None, [msg]
        )
        submit_btn.click(respond, [msg, chatbot], [chatbot]).then(
            lambda: "", None, [msg]
        )

    demo.launch(
        server_name="127.0.0.1",
        server_port=8766,
        share=False,
        css=custom_css,
    )


if __name__ == "__main__":
    main()
