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


@app.on_event("startup")
async def startup():
    global assistant, calendar_tool, email_tool
    try:
        assistant = PersonalAssistant()
    except RuntimeError:
        assistant = None
    calendar_tool = CalendarTool()
    email_tool = EmailTool()


class ChatRequest(BaseModel):
    message: str


class ChatResponse(BaseModel):
    response: str


@app.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):
    if not assistant:
        return ChatResponse(response="Configure OPENAI_API_KEY no .env")
    try:
        response = assistant.chat(req.message)
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


@app.get("/status")
async def status():
    if assistant:
        return assistant.get_status()
    return {"llm": "Nao configurado", "calendario": "-", "e-mail": "-", "pesquisa web": "-"}
