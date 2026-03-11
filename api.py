#!/usr/bin/env python3
"""API REST do Assistente Pessoal."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from assistant import PersonalAssistant
from tools.calendar_tool import CalendarTool
from tools.email_tool import EmailTool
from tools.web_tool import WebTool
from tools.simple_questions import answer_simple_question

app = FastAPI(title="Assistente Pessoal API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

assistant = None
calendar_tool = None
email_tool = None
web_tool = None


@app.on_event("startup")
async def startup():
    global assistant, calendar_tool, email_tool, web_tool
    try:
        assistant = PersonalAssistant()
    except RuntimeError:
        assistant = None
    calendar_tool = CalendarTool()
    email_tool = EmailTool()
    web_tool = WebTool()


class ChatRequest(BaseModel):
    message: str


class ChatResponse(BaseModel):
    response: str


@app.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):
    msg = (req.message or "").strip()
    if not msg:
        return ChatResponse(response="Digite uma mensagem.")

    # Perguntas simples (data, hora, clima, notícias) - funciona sem LLM
    simple = answer_simple_question(msg, web_tool=web_tool)
    if simple is not None:
        return ChatResponse(response=simple)

    # Perguntas complexas - usa o assistente com LLM
    if not assistant:
        return ChatResponse(
            response="Para perguntas mais complexas, configure OPENAI_API_KEY no .env. "
            "Você pode perguntar: que dia é hoje, temperatura, previsão do tempo, notícias."
        )
    try:
        response = assistant.chat(msg)
        return ChatResponse(response=response)
    except Exception as e:
        return ChatResponse(response=f"Erro: {str(e)}")


@app.get("/calendar")
async def get_calendar(days: int = 7):
    events = calendar_tool.get_events(days_ahead=days) if calendar_tool else "Calendario nao configurado."
    return {"events": events}


class EmailRequest(BaseModel):
    to: str
    subject: str
    body: str


class EmailResponse(BaseModel):
    result: str


@app.post("/email", response_model=EmailResponse)
async def send_email(req: EmailRequest):
    if not email_tool:
        return EmailResponse(result="E-mail nao configurado.")
    result = email_tool.send_email(to=req.to, subject=req.subject, body=req.body)
    return EmailResponse(result=result)


@app.get("/search")
async def search(q: str = "", max_results: int = 5):
    query = q.strip()
    if not query:
        return {"results": "Digite um termo para pesquisar."}
    results = web_tool.search(query, max_results=max_results) if web_tool else "Pesquisa nao disponivel."
    return {"results": results}


class SummarizeRequest(BaseModel):
    url: str | None = None
    text: str | None = None


class SummarizeResponse(BaseModel):
    summary: str


@app.post("/summarize", response_model=SummarizeResponse)
async def summarize(req: SummarizeRequest):
    if not web_tool:
        return SummarizeResponse(summary="Resumo nao disponivel.")
    llm_func = (assistant.llm.chat if hasattr(assistant, "llm") and assistant.llm else None) if assistant else None
    if req.url and req.url.strip().startswith(("http://", "https://")):
        result = web_tool.fetch_and_summarize(req.url.strip(), llm_chat_func=llm_func)
    elif req.text and req.text.strip():
        result = web_tool.summarize_text(req.text.strip(), llm_chat_func=llm_func)
    else:
        return SummarizeResponse(summary="Informe uma URL ou cole o texto para resumir.")
    return SummarizeResponse(summary=result)


@app.get("/status")
async def status():
    if assistant:
        return assistant.get_status()
    return {"llm": "Nao configurado", "calendario": "-", "e-mail": "-", "pesquisa web": "-"}
