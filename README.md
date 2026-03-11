# Assistente Pessoal

Assistente que realiza tarefas: calendário, e-mails, pesquisa web e resumos.

## Duas interfaces disponíveis

### 1. Interface React (visual, recomendada)
Frontend moderno com React + Tailwind CSS.

```bash
# Terminal 1 - API
pip install fastapi uvicorn
uvicorn api:app --reload --port 8000

# Terminal 2 - Frontend
cd frontend
npm install
npm run dev
```

Acesse: http://localhost:5173

### 2. Interface Gradio (Python)
Interface em Python com Gradio.

```bash
python app.py
```

Acesse: http://127.0.0.1:8766

## Configuração

Configure o `.env` com `OPENAI_API_KEY` para usar o assistente.
