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

app = FastAPI(title="Assistente Pessoal API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

assistant = None
calendar_tool = None


@app.on_event("startup")
async def startup():
    global assistant, calendar_tool
    try:
        assistant = PersonalAssistant()
    except RuntimeError:
        assistant = None
    calendar_tool = CalendarTool()


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


@app.get("/status")
async def status():
    if assistant:
        return assistant.get_status()
    return {"llm": "Nao configurado", "calendario": "-", "e-mail": "-", "pesquisa web": "-"}
