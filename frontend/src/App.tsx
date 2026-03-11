import { useState, useRef, useEffect } from 'react'
import {
  IconCalendar,
  IconMail,
  IconSearch,
  IconSummarize,
  IconSparkles,
  IconSend,
} from './components/Icons'

const API_URL = '/api'

interface Message {
  role: 'user' | 'assistant'
  content: string
}

const SUGGESTIONS = [
  { label: 'Calendário', icon: IconCalendar, prompt: 'Mostre meus eventos da semana' },
  { label: 'E-mail', icon: IconMail, prompt: 'Enviar um e-mail' },
  { label: 'Pesquisa', icon: IconSearch, prompt: 'Pesquisar na web sobre' },
  { label: 'Resumos', icon: IconSummarize, prompt: 'Resumir o seguinte texto' },
] as const

export default function App() {
  const [messages, setMessages] = useState<Message[]>([])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [status, setStatus] = useState<Record<string, string>>({})
  const chatEndRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    fetch(`${API_URL}/status`)
      .then((r) => r.json())
      .then(setStatus)
      .catch(() => setStatus({}))
  }, [])

  const scrollToBottom = () => chatEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  useEffect(scrollToBottom, [messages])

  const sendMessage = async (text: string) => {
    if (!text.trim() || loading) return
    const userMsg: Message = { role: 'user', content: text.trim() }
    setMessages((m) => [...m, userMsg])
    setInput('')
    setLoading(true)

    try {
      const res = await fetch(`${API_URL}/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: text.trim() }),
      })
      const data = await res.json()
      setMessages((m) => [...m, { role: 'assistant', content: data.response }])
    } catch (e) {
      setMessages((m) => [...m, { role: 'assistant', content: `Erro: ${e}` }])
    } finally {
      setLoading(false)
    }
  }

  const loadCalendar = async () => {
    setLoading(true)
    setMessages((m) => [...m, { role: 'user', content: 'Ver calendário' }])
    try {
      const res = await fetch(`${API_URL}/calendar?days=7`)
      const data = await res.json()
      setMessages((m) => [...m, { role: 'assistant', content: data.events }])
    } catch (e) {
      setMessages((m) => [...m, { role: 'assistant', content: `Erro: ${e}` }])
    } finally {
      setLoading(false)
    }
  }

  const handleSuggestion = (label: string, prompt: string) => {
    if (label === 'Calendário') {
      loadCalendar()
    } else {
      setInput(prompt)
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 flex font-sans">
      {/* Sidebar */}
      <aside className="w-64 min-w-[240px] bg-slate-800/40 backdrop-blur-xl border-r border-cyan-500/20 flex flex-col shrink-0">
        <div className="p-5 flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-cyan-500 to-teal-600 flex items-center justify-center shadow-lg shadow-cyan-500/20">
            <img src="/logo.png" alt="Logo" className="w-6 h-6 object-contain invert" />
          </div>
          <div>
            <span className="font-bold text-cyan-50 text-lg tracking-tight">Assistente</span>
            <span className="block text-xs text-cyan-400/80 font-medium tracking-wide">Pessoal</span>
          </div>
        </div>

        <nav className="flex-1 px-3 pt-4 space-y-0.5">
          <button
            onClick={() => setMessages([])}
            className="w-full flex items-center gap-3 px-4 py-2.5 rounded-xl text-cyan-200/90 hover:bg-cyan-500/10 hover:text-cyan-100 transition-all duration-200 text-left"
          >
            <IconSparkles />
            <span className="font-medium text-sm">Novo chat</span>
          </button>
          <button
            onClick={loadCalendar}
            disabled={loading}
            className="w-full flex items-center gap-3 px-4 py-2.5 rounded-xl text-cyan-200/90 hover:bg-cyan-500/10 hover:text-cyan-100 transition-all duration-200 text-left disabled:opacity-50"
          >
            <IconCalendar />
            <span className="font-medium text-sm">Calendário</span>
          </button>
        </nav>

        <div className="p-4 m-3 rounded-xl bg-slate-800/60 border border-cyan-500/10">
          <p className="text-[10px] text-cyan-400/70 uppercase tracking-widest font-semibold mb-2.5">
            Status
          </p>
          <div className="space-y-1">
            {Object.entries(status).map(([k, v]) => (
              <p key={k} className="text-xs text-cyan-200/80 font-medium">
                {k}: <span className="text-cyan-100 font-semibold">{v}</span>
              </p>
            ))}
          </div>
        </div>
      </aside>

      {/* Main */}
      <main className="flex-1 flex flex-col min-w-0 p-8 max-w-4xl mx-auto w-full">
        {/* Header */}
        <header className="mb-8">
          <h1 className="text-3xl font-bold bg-gradient-to-r from-cyan-300 via-teal-400 to-cyan-300 bg-clip-text text-transparent tracking-tight mb-2">
            Como posso ajudar?
          </h1>
          <p className="text-cyan-200/70 text-base font-medium tracking-wide">
            Escolha uma opção ou digite sua mensagem
          </p>
        </header>

        {/* Sugestões */}
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 mb-8">
          {SUGGESTIONS.map(({ label, icon: Icon, prompt }) => (
            <button
              key={label}
              onClick={() => handleSuggestion(label, prompt)}
              disabled={loading}
              className="group flex flex-col items-center gap-2 p-4 rounded-2xl bg-slate-800/40 border border-cyan-500/10 hover:border-cyan-500/30 hover:bg-cyan-500/5 transition-all duration-300 disabled:opacity-50"
            >
              <span className="w-10 h-10 rounded-xl bg-cyan-500/10 flex items-center justify-center text-cyan-400 group-hover:bg-cyan-500/20 group-hover:text-cyan-300 transition-colors">
                <Icon />
              </span>
              <span className="text-sm font-semibold text-cyan-100/90 tracking-tight">{label}</span>
            </button>
          ))}
        </div>

        {/* Chat */}
        <div className="flex-1 flex flex-col min-h-0">
          <div className="flex-1 overflow-y-auto space-y-4 mb-6 rounded-2xl border border-cyan-500/15 bg-slate-800/20 p-6 min-h-[360px]">
            {messages.length === 0 && (
              <div className="flex flex-col items-center justify-center py-16 text-center">
                <div className="w-14 h-14 rounded-2xl bg-cyan-500/10 flex items-center justify-center mb-4">
                  <IconSparkles />
                </div>
                <p className="text-slate-400 font-medium mb-1">Nenhuma mensagem ainda</p>
                <p className="text-slate-500 text-sm">Clique em uma sugestão ou digite abaixo</p>
              </div>
            )}
            {messages.map((msg, i) => (
              <div
                key={i}
                className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                <div
                  className={`max-w-[85%] rounded-2xl px-4 py-3 ${
                    msg.role === 'user'
                      ? 'bg-gradient-to-r from-cyan-600/40 to-teal-600/40 border border-cyan-400/25'
                      : 'bg-slate-700/40 border border-cyan-500/10'
                  }`}
                >
                  <p className="text-slate-100 text-[15px] leading-relaxed whitespace-pre-wrap font-medium">
                    {msg.content}
                  </p>
                </div>
              </div>
            ))}
            {loading && (
              <div className="flex justify-start">
                <div className="bg-slate-700/40 rounded-2xl px-4 py-3 animate-pulse">
                  <span className="text-cyan-400 font-medium">...</span>
                </div>
              </div>
            )}
            <div ref={chatEndRef} />
          </div>

          {/* Input */}
          <form
            onSubmit={(e) => {
              e.preventDefault()
              sendMessage(input)
            }}
            className="flex gap-3"
          >
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Digite sua mensagem..."
              className="flex-1 rounded-2xl bg-slate-800/60 border border-cyan-500/20 px-5 py-3.5 text-cyan-100 placeholder-cyan-400/50 focus:outline-none focus:ring-2 focus:ring-cyan-400/40 focus:border-cyan-400/40 text-[15px] font-medium transition-all"
            />
            <button
              type="submit"
              disabled={loading}
              className="px-6 py-3.5 rounded-2xl bg-gradient-to-r from-cyan-500 to-teal-500 text-white font-semibold hover:from-cyan-400 hover:to-teal-400 transition-all duration-200 disabled:opacity-50 flex items-center gap-2 shadow-lg shadow-cyan-500/20"
            >
              <IconSend />
              Enviar
            </button>
          </form>
        </div>
      </main>
    </div>
  )
}
