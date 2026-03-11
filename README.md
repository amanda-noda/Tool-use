# Assistente Pessoal

Assistente inteligente que não só conversa, mas **executa tarefas reais**: consulta calendário, envia e-mails, pesquisa na web e resume informações. Funciona com ou sem API de IA configurada.

## Funcionalidades

### Perguntas simples (sem configuração)
Respondidas diretamente, sem necessidade de `OPENAI_API_KEY`:

- **Data e hora:** "Que dia é hoje?", "Que horas são?"
- **Clima:** "Qual a temperatura?", "Previsão do tempo", "Vai chover?"
- **Notícias:** "Quais as notícias?", "Últimas notícias"

### Tarefas com ferramentas
- **Calendário** — Eventos da semana (modo demo ou Google Calendar)
- **E-mail** — Envio de mensagens (modo demo ou Gmail)
- **Pesquisa** — Busca na web (DuckDuckGo ou modo demo)
- **Resumos** — Resumir texto ou páginas web (com ou sem IA)

### Chat com IA (opcional)
Com `OPENAI_API_KEY`, `ANTHROPIC_API_KEY` ou Ollama configurado, o assistente responde perguntas complexas e usa as ferramentas automaticamente.

---

## Estrutura do projeto

```
Tool-use/
├── api.py              # API REST (FastAPI) - backend do React
├── app.py              # Interface Gradio (Python)
├── assistant.py       # Orquestrador principal com LLM
├── config.py          # Configurações e variáveis de ambiente
├── main.py            # CLI no terminal
├── .env               # Chaves e configurações (não versionado)
├── credentials/       # Credenciais Google (OAuth)
├── frontend/          # Interface React + Tailwind
│   ├── src/
│   │   ├── App.tsx
│   │   └── components/
│   └── package.json
├── llm/               # Provedores de LLM
│   ├── openai_provider.py
│   ├── anthropic_provider.py
│   └── ollama_provider.py
└── tools/             # Ferramentas
    ├── calendar_tool.py
    ├── email_tool.py
    ├── web_tool.py
    └── simple_questions.py   # Data, hora, clima, notícias
```

---

## Como rodar

### Pré-requisitos
- Python 3.10+
- Node.js 18+ (para a interface React)

### 1. Instalar dependências

```bash
# Python
pip install -r requirements.txt

# Frontend (apenas para interface React)
cd frontend && npm install
```

### 2. Configurar ambiente (opcional)

Crie um arquivo `.env` na raiz do projeto:

```env
# Pelo menos um para chat com IA
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
# Ou use Ollama local (ollama run llama3.2)

# Opcional: Google Calendar e Gmail
GOOGLE_CALENDAR_ENABLED=true
GOOGLE_EMAIL_ENABLED=true
```

### 3. Escolher a interface

#### Interface React (recomendada)
Visual moderna com tons de azul, roxo e verde.

```bash
# Terminal 1 - API
uvicorn api:app --reload --port 8000

# Terminal 2 - Frontend
cd frontend && npm run dev
```

Acesse: **http://localhost:5173** (ou a porta indicada no terminal)

#### Interface Gradio
Interface em Python, mais simples.

```bash
python app.py
```

Acesse: **http://127.0.0.1:8768**

#### CLI (terminal)
Para uso direto no terminal:

```bash
python main.py
```

---

## Como funciona

1. **Perguntas simples** — O módulo `simple_questions` detecta perguntas como "que dia é hoje" ou "qual a temperatura" e responde sem usar LLM. Clima usa a API gratuita Open-Meteo.

2. **Ferramentas** — Calendário, e-mail, pesquisa e resumos têm modo demo quando não há credenciais configuradas. Com credenciais, usam os serviços reais.

3. **Chat com IA** — Quando há LLM configurado, o assistente interpreta a mensagem, escolhe a ferramenta adequada e monta a resposta. O prompt inclui data/hora atual para respostas mais precisas.

4. **API REST** — O frontend React chama a API em `/chat`, `/calendar`, `/email`, `/search` e `/summarize`. O Vite faz proxy de `/api` para `http://127.0.0.1:8000`.

---

## Configuração avançada

### Google Calendar
1. Crie um projeto no [Google Cloud Console](https://console.cloud.google.com)
2. Ative a API do Google Calendar
3. Baixe as credenciais OAuth e salve em `credentials/credentials.json`
4. Defina `GOOGLE_CALENDAR_ENABLED=true` no `.env`
5. Na primeira execução, faça o login no navegador

### Gmail
1. Use o mesmo projeto do Google Cloud
2. Ative a API Gmail
3. Mesmo `credentials.json`, com `GOOGLE_EMAIL_ENABLED=true`
4. Token salvo em `credentials/token_email.json`

### Ollama (LLM local)
```bash
ollama run llama3.2
```
O assistente usa Ollama automaticamente se estiver rodando e não houver outras chaves configuradas.

---

## Portas utilizadas

| Serviço   | Porta padrão |
|-----------|--------------|
| API       | 8000         |
| Frontend  | 5173         |
| Gradio    | 8768         |

Se a porta estiver ocupada, o servidor tenta a próxima disponível.
