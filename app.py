#!/usr/bin/env python3
"""
Assistente Pessoal - Interface Web (estilo ChatGPT)
Execute: python app.py
"""
import sys
import html
import base64
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

import gradio as gr
from assistant import PersonalAssistant
from tools.calendar_tool import CalendarTool


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

    calendar_tool = CalendarTool()

    base = Path(__file__).resolve().parent
    logo_path = base / "assets" / "logo.png"
    if not logo_path.exists():
        logo_path = base / "frontend" / "public" / "logo.png"
    logo_b64 = ""
    if logo_path.exists():
        try:
            with open(logo_path, "rb") as f:
                logo_b64 = base64.b64encode(f.read()).decode()
        except Exception:
            pass

    logo_svg = '''<svg class="logo-img" viewBox="0 0 48 48" xmlns="http://www.w3.org/2000/svg">
        <path d="M24 4 L44 44 L4 44 Z" fill="none" stroke="#e0f7fa" stroke-width="2.5"/>
        <path d="M24 16 L24 36 M18 28 L24 36 L30 28" fill="none" stroke="#e0f7fa" stroke-width="2"/>
    </svg>'''

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
        border-right: 0.5px solid rgba(0, 188, 212, 0.15) !important;
        padding: 1.5rem 0 !important;
        min-height: 100vh;
        animation: fade-slide 0.8s ease-out;
    }

    .sidebar .logo {
        display: flex;
        align-items: center;
        gap: 0.6rem;
        padding: 0.9rem 1.25rem;
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

    .sidebar .logo-img {
        width: 38px;
        height: 38px;
        object-fit: contain;
        flex-shrink: 0;
    }

    .sidebar .logo img.logo-img {
        border-radius: 8px;
        border: 1px solid rgba(0, 188, 212, 0.3);
    }

    .sidebar .logo svg.logo-img {
        color: #e0f7fa;
    }

    .sidebar .logo .logo-fallback {
        width: 38px;
        height: 38px;
        background: linear-gradient(135deg, #00e5ff, #0097a7);
        border-radius: 10px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: 800;
        font-size: 1.2rem;
        color: white;
    }

    .sidebar .nav-item {
        display: flex;
        align-items: center;
        gap: 0.6rem;
        padding: 0.7rem 1.25rem;
        margin: 0.2rem 0.6rem;
        color: #b2ebf2;
        font-size: 0.9rem;
        border-radius: 10px;
        border-left: 2px solid transparent;
        transition: all 0.35s cubic-bezier(0.4, 0, 0.2, 1);
    }

    .sidebar .nav-item:hover {
        background: linear-gradient(90deg, rgba(0, 188, 212, 0.15), transparent);
        border-left-color: #00e5ff;
        color: #e0f7fa;
        transform: translateX(4px);
    }

    .sidebar .nav-icon {
        width: 18px;
        height: 18px;
        flex-shrink: 0;
        opacity: 0.9;
    }

    .sidebar .nav-item:hover .nav-icon {
        opacity: 1;
    }

    .sidebar .nav-divider {
        height: 0.5px;
        background: linear-gradient(90deg, transparent, rgba(0, 188, 212, 0.2), transparent);
        margin: 1rem 1.5rem;
    }

    .sidebar .status-box {
        margin: 0.8rem 0.8rem;
        padding: 1rem;
        background: linear-gradient(135deg, rgba(0, 151, 167, 0.2), rgba(0, 96, 100, 0.15));
        border: 0.5px solid rgba(0, 229, 255, 0.2);
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

    /* Area principal - padronizacao */
    #main-row {
        gap: 0 !important;
        margin: 0 !important;
    }

    #main-content {
        animation: fade-slide 0.6s ease-out 0.2s both;
        padding: 1.5rem 2rem !important;
        max-width: 100%;
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

    /* Input - fluido, linhas delicadas */
    #main-content textarea {
        background: linear-gradient(135deg, rgba(0, 96, 100, 0.15) 0%, rgba(13, 71, 161, 0.1) 100%) !important;
        border: 0.5px solid rgba(0, 188, 212, 0.25) !important;
        border-radius: 24px !important;
        color: #e0f7fa !important;
        padding: 0.9rem 1.25rem !important;
        font-size: 0.95rem !important;
        min-height: 52px !important;
        transition: all 0.35s cubic-bezier(0.4, 0, 0.2, 1) !important;
    }

    #main-content textarea:focus {
        border: 0.5px solid rgba(0, 229, 255, 0.5) !important;
        box-shadow: 0 0 0 1.5px rgba(0, 188, 212, 0.2) !important;
        transform: translateY(-1px);
    }

    #main-content textarea::placeholder {
        color: #80deea !important;
        opacity: 0.8;
    }

    /* Chatbot - linhas finas e delicadas, visual limpo */
    .chatbot {
        border: 0.5px solid rgba(0, 188, 212, 0.12) !important;
        border-radius: 16px !important;
        padding: 1rem !important;
    }

    .chatbot .message {
        border-radius: 14px !important;
        transition: all 0.25s ease !important;
        border: 0.5px solid transparent !important;
    }

    .chatbot .message:hover {
        transform: scale(1.005);
    }

    .chatbot .message.user {
        background: linear-gradient(135deg, rgba(0, 150, 136, 0.2) 0%, rgba(0, 188, 212, 0.18) 100%) !important;
        border-color: rgba(0, 229, 255, 0.15) !important;
        box-shadow: none !important;
    }

    .chatbot .message.bot {
        background: linear-gradient(135deg, rgba(22, 27, 34, 0.85) 0%, rgba(13, 71, 161, 0.08) 100%) !important;
        border-color: rgba(0, 188, 212, 0.1) !important;
        box-shadow: none !important;
    }

    /* Footer - linha delicada */
    .app-footer {
        padding: 0.85rem 2rem;
        text-align: center;
        color: #8b949e;
        font-size: 0.78rem;
        background: linear-gradient(180deg, transparent, rgba(0, 0, 0, 0.15));
        border-top: 0.5px solid rgba(0, 188, 212, 0.08);
    }

    /* Botao Enviar - icone criativo */
    .gradio-container button.primary {
        background: linear-gradient(135deg, #00bcd4 0%, #0097a7 50%, #00838f 100%) !important;
        border: none !important;
        color: #fff !important;
        border-radius: 14px !important;
        font-weight: 600 !important;
        padding: 0.7rem 1.2rem !important;
        transition: all 0.35s cubic-bezier(0.4, 0, 0.2, 1) !important;
        box-shadow: 0 2px 12px rgba(0, 188, 212, 0.25) !important;
    }

    .gradio-container button.primary:hover {
        background: linear-gradient(135deg, #00e5ff 0%, #00bcd4 50%, #0097a7 100%) !important;
        transform: translateY(-2px);
        box-shadow: 0 4px 20px rgba(0, 188, 212, 0.35) !important;
    }

    .nav-btn {
        width: 100% !important;
        text-align: left !important;
        padding: 0.7rem 1.25rem !important;
        margin: 0.2rem 0.6rem !important;
        background: transparent !important;
        border: none !important;
        border-left: 2px solid transparent !important;
        border-radius: 10px !important;
        color: #b2ebf2 !important;
        font-size: 0.9rem !important;
    }

    .nav-btn:hover {
        background: linear-gradient(90deg, rgba(0, 188, 212, 0.15), transparent) !important;
        border-left-color: #00e5ff !important;
        color: #e0f7fa !important;
    }

    .sidebar-wrap .nav-btn {
        margin-left: 0.6rem;
        margin-right: 0.6rem;
    }

    .gradio-container footer,
    footer[class*="footer"],
    .gradio-container [class*="footer"] {
        display: none !important;
    }
    """

    # Icones SVG criativos e chamativos
    icon_sparkles = '<svg class="nav-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 3l1.5 4.5L18 9l-4.5 1.5L12 15l-1.5-4.5L6 9l4.5-1.5L12 3z"/><path d="M5 19l1.5-4.5L9 13l-2.5.5L5 19z"/><path d="M19 5l-1.5 4.5L15 10l2.5-.5L19 5z"/></svg>'
    icon_search = '<svg class="nav-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="8"/><path d="m21 21-4.35-4.35"/></svg>'
    icon_calendar = '<svg class="nav-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="4" width="18" height="18" rx="2"/><path d="M16 2v4M8 2v4M3 10h18"/></svg>'
    icon_mail = '<svg class="nav-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"/><path d="m22 6-10 7L2 6"/></svg>'
    icon_globe = '<svg class="nav-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><path d="M2 12h20M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"/></svg>'

    if logo_b64:
        logo_img = f'<img src="data:image/png;base64,{logo_b64}" class="logo-img" alt="Logo"/>'
    else:
        logo_img = '<div class="logo-fallback">A</div>'

    sidebar_html_top = f"""
    <div class="sidebar">
        <div class="logo">
            {logo_img}
            <span>Assistente Pessoal</span>
        </div>
        <div class="nav-divider"></div>
        <div class="nav-item">{icon_sparkles} Novo chat</div>
        <div class="nav-item">{icon_search} Buscar em chats</div>
        <div class="nav-divider"></div>
    """
    sidebar_html_bottom = f"""
        <div class="nav-divider"></div>
        <div class="nav-item">{icon_mail} E-mail</div>
        <div class="nav-item">{icon_globe} Pesquisa web</div>
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
    <div style="text-align:center; margin-bottom:1.5rem;">
        <p style="color:#80deea; font-size:0.9rem; opacity:0.85; margin-top:0.25rem; letter-spacing:0.02em;">
            Calendario • E-mail • Pesquisa • Resumos
        </p>
    </div>
    """

    with gr.Blocks(title="Assistente Pessoal") as demo:
        with gr.Row(elem_id="main-row"):
            # Sidebar
            with gr.Column(scale=1, min_width=240):
                with gr.Group(elem_classes=["sidebar-wrap"]):
                    gr.HTML(sidebar_html_top)
                    btn_calendar = gr.Button("📅 Calendario", variant="secondary", elem_classes=["nav-btn"])
                    gr.HTML(sidebar_html_bottom)

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
                        submit_btn = gr.Button("➤ Enviar", scale=1, elem_classes=["primary"])

        gr.HTML(footer_html)

        def respond(message, chat_history):
            if not message.strip():
                return chat_history
            chat_history = chat_history or []
            chat_history.append([message, ""])
            response = chat_fn(message, chat_history, assistant)
            chat_history[-1][1] = response
            return chat_history

        def show_calendar(chat_history):
            chat_history = chat_history or []
            events = calendar_tool.get_events(days_ahead=7)
            chat_history.append(["Ver calendario", events])
            return chat_history

        msg.submit(respond, [msg, chatbot], [chatbot]).then(
            lambda: "", None, [msg]
        )
        submit_btn.click(respond, [msg, chatbot], [chatbot]).then(
            lambda: "", None, [msg]
        )
        btn_calendar.click(show_calendar, [chatbot], [chatbot])

    demo.launch(
        server_name="127.0.0.1",
        server_port=8767,
        share=False,
        css=custom_css,
    )


if __name__ == "__main__":
    main()
