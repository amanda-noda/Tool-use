import { useState, useRef, useEffect } from 'react'
import {
  IconCalendar,
  IconMail,
  IconSearch,
  IconSummarize,
  IconSparkles,
  IconSend,
} from './components/Icons'
import { Logo } from './components/Logo'

const API_URL = '/api'

interface Message {
  role: 'user' | 'assistant'
  content: string
  type?: 'calendar' | 'chat' | 'search'
}

function formatSearchContent(content: string) {
  const blocks = content.split(/\n\n+/)
  const results: { title: string; href: string; body: string }[] = []
  let header = ''
  for (const block of blocks) {
    const lines = block.trim().split('\n')
    if (lines.length >= 2 && lines[0].startsWith('- ')) {
      const title = lines[0].replace(/^-\s*/, '').trim()
      const href = lines[1].replace(/^\s+/, '').trim()
      const body = lines[2]?.replace(/^\s+/, '').trim() || ''
      if (href.startsWith('http')) results.push({ title, href, body })
    } else if (!header && lines[0] && !lines[0].startsWith('- ')) {
      header = lines[0].trim()
    }
  }
  return results.length ? { header, results } : null
}

function formatCalendarContent(content: string) {
  const lines = content.trim().split('\n')
  const eventLines = lines.filter((l) => l.trim().startsWith('- '))
  if (eventLines.length === 0) return null
  const header = lines
    .filter((l) => l.trim() && !l.trim().startsWith('- '))
    .join(' ')
    .trim()
  return {
    header,
    events: eventLines.map((e) => e.replace(/^-\s*/, '')),
  }
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
  const chatEndRef = useRef<HTMLDivElement>(null)

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
      setMessages((m) => [...m, { role: 'assistant', content: data.events, type: 'calendar' }])
    } catch (e) {
      setMessages((m) => [...m, { role: 'assistant', content: `Erro: ${e}` }])
    } finally {
      setLoading(false)
    }
  }

  const [showEmailModal, setShowEmailModal] = useState(false)
  const [emailForm, setEmailForm] = useState({ to: '', subject: '', body: '' })

  const sendEmail = async (to: string, subject: string, body: string) => {
    setLoading(true)
    setMessages((m) => [...m, { role: 'user', content: `Enviar e-mail para ${to}: ${subject}` }])
    try {
      const res = await fetch(`${API_URL}/email`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ to, subject, body }),
      })
      const data = await res.json()
      setMessages((m) => [...m, { role: 'assistant', content: data.result }])
      setShowEmailModal(false)
      setEmailForm({ to: '', subject: '', body: '' })
    } catch (e) {
      setMessages((m) => [...m, { role: 'assistant', content: `Erro: ${e}` }])
    } finally {
      setLoading(false)
    }
  }

  const [showSearchModal, setShowSearchModal] = useState(false)
  const [searchQuery, setSearchQuery] = useState('')

  const runSearch = async (query: string) => {
    if (!query.trim() || loading) return
    setLoading(true)
    setMessages((m) => [...m, { role: 'user', content: `Pesquisar: ${query.trim()}` }])
    try {
      const res = await fetch(`${API_URL}/search?q=${encodeURIComponent(query.trim())}`)
      const data = await res.json()
      setMessages((m) => [...m, { role: 'assistant', content: data.results, type: 'search' }])
      setShowSearchModal(false)
      setSearchQuery('')
    } catch (e) {
      setMessages((m) => [...m, { role: 'assistant', content: `Erro: ${e}` }])
    } finally {
      setLoading(false)
    }
  }

  const [showSummarizeModal, setShowSummarizeModal] = useState(false)
  const [summarizeInput, setSummarizeInput] = useState('')

  const runSummarize = async (input: string) => {
    if (!input.trim() || loading) return
    const isUrl = /^https?:\/\//i.test(input.trim())
    setLoading(true)
    setMessages((m) => [...m, { role: 'user', content: isUrl ? `Resumir: ${input.trim()}` : `Resumir texto (${input.trim().slice(0, 50)}...)` }])
    try {
      const res = await fetch(`${API_URL}/summarize`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(isUrl ? { url: input.trim() } : { text: input.trim() }),
      })
      const data = await res.json()
      setMessages((m) => [...m, { role: 'assistant', content: data.summary }])
      setShowSummarizeModal(false)
      setSummarizeInput('')
    } catch (e) {
      setMessages((m) => [...m, { role: 'assistant', content: `Erro: ${e}` }])
    } finally {
      setLoading(false)
    }
  }

  const handleSuggestion = (label: string, prompt: string) => {
    if (label === 'Calendário') {
      loadCalendar()
    } else if (label === 'E-mail') {
      setShowEmailModal(true)
    } else if (label === 'Pesquisa') {
      setShowSearchModal(true)
    } else if (label === 'Resumos') {
      setShowSummarizeModal(true)
    } else {
      setInput(prompt)
    }
  }

  const SUGGESTION_COLORS = [
    'from-blue-500/20 to-blue-600/10 border-blue-400/30 hover:border-blue-400/50 text-blue-200',
    'from-violet-500/20 to-violet-600/10 border-violet-400/30 hover:border-violet-400/50 text-violet-200',
    'from-emerald-500/20 to-emerald-600/10 border-emerald-400/30 hover:border-emerald-400/50 text-emerald-200',
    'from-fuchsia-500/20 to-fuchsia-600/10 border-fuchsia-400/30 hover:border-fuchsia-400/50 text-fuchsia-200',
  ]

  return (
    <div className="min-h-screen flex font-sans relative overflow-hidden">
      {/* Animated gradient background */}
      <div
        className="fixed inset-0 animate-gradient"
        style={{
          background: 'linear-gradient(135deg, #0f172a 0%, #1e1b4b 25%, #0c4a6e 50%, #134e4a 75%, #1e1b4b 100%)',
          backgroundSize: '400% 400%',
          backgroundPosition: '0% 50%',
        }}
      />
      <div className="fixed inset-0 bg-black/30" />

      {/* Sidebar */}
      <aside className="relative z-10 w-64 min-w-[240px] bg-white/5 backdrop-blur-2xl border-r border-white/10 flex flex-col shrink-0">
        <div className="p-5 flex items-center gap-3">
          <div className="w-11 h-11 rounded-2xl bg-gradient-to-br from-blue-500 via-violet-500 to-emerald-500 flex items-center justify-center shadow-lg shadow-violet-500/25 animate-float">
            <Logo className="w-6 h-6" />
          </div>
          <div>
            <span className="font-bold text-white text-lg tracking-tight">Assistente</span>
            <span className="block text-xs text-blue-200/80 font-medium">Pessoal</span>
          </div>
        </div>

        <nav className="flex-1 px-3 pt-6 space-y-1">
          {[
            { icon: IconSparkles, label: 'Novo chat', onClick: () => setMessages([]) },
            { icon: IconCalendar, label: 'Calendário', onClick: loadCalendar, disabled: loading },
            { icon: IconMail, label: 'E-mail', onClick: () => setShowEmailModal(true), disabled: loading },
            { icon: IconSearch, label: 'Pesquisa', onClick: () => setShowSearchModal(true), disabled: loading },
            { icon: IconSummarize, label: 'Resumos', onClick: () => setShowSummarizeModal(true), disabled: loading },
          ].map(({ icon: Icon, label, onClick, disabled }) => (
            <button
              key={label}
              onClick={onClick}
              disabled={disabled}
              className="w-full flex items-center gap-3 px-4 py-3 rounded-2xl text-white/80 hover:bg-white/10 hover:text-white transition-all duration-300 text-left disabled:opacity-50"
            >
              <Icon />
              <span className="font-medium text-sm">{label}</span>
            </button>
          ))}
        </nav>
      </aside>

      {/* Main */}
      <main className="relative z-10 flex-1 flex flex-col min-w-0 p-8 max-w-4xl mx-auto w-full">
        <header className="mb-10 animate-fade-up">
          <h1 className="text-4xl font-bold bg-gradient-to-r from-blue-300 via-violet-300 to-emerald-300 bg-clip-text text-transparent tracking-tight mb-2">
            Como posso ajudar?
          </h1>
          <p className="text-white/60 text-base font-medium">
            Escolha uma opção ou digite sua mensagem
          </p>
        </header>

        {/* Sugestões */}
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 mb-10">
          {SUGGESTIONS.map(({ label, icon: Icon, prompt }, i) => (
            <button
              key={label}
              onClick={() => handleSuggestion(label, prompt)}
              disabled={loading}
              className={`group flex flex-col items-center gap-3 p-5 rounded-3xl bg-gradient-to-br ${SUGGESTION_COLORS[i]} border backdrop-blur-sm hover:scale-[1.02] transition-all duration-300 disabled:opacity-50 animate-fade-up`}
            >
              <span className="w-12 h-12 rounded-2xl bg-white/10 flex items-center justify-center text-white group-hover:bg-white/20 transition-colors">
                <Icon />
              </span>
              <span className="text-sm font-semibold text-white/90 tracking-tight">{label}</span>
            </button>
          ))}
        </div>

        {/* Chat */}
        <div className="flex-1 flex flex-col min-h-0">
          <div className="flex-1 overflow-y-auto space-y-4 mb-6 rounded-3xl border border-white/10 bg-white/5 backdrop-blur-sm p-6 min-h-[360px]">
            {messages.length === 0 && (
              <div className="flex flex-col items-center justify-center py-20 text-center">
                <div className="w-20 h-20 rounded-3xl bg-gradient-to-br from-blue-500/20 via-violet-500/20 to-emerald-500/20 flex items-center justify-center mb-6 animate-float text-white">
                  <IconSparkles />
                </div>
                <p className="text-white/70 font-medium mb-1 text-lg">Nenhuma mensagem ainda</p>
                <p className="text-white/40 text-sm">Clique em uma sugestão ou digite abaixo para começar</p>
              </div>
            )}
            {messages.map((msg, i) => {
              const searchFormatted = msg.type === 'search' ? formatSearchContent(msg.content) : null
              const calendarFormatted = msg.type === 'calendar' ? formatCalendarContent(msg.content) : null
              return (
                <div
                  key={i}
                  className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
                >
                  <div
                    className={`max-w-[85%] rounded-2xl px-4 py-3 ${
                      msg.role === 'user'
                        ? 'bg-gradient-to-r from-blue-500/30 via-violet-500/30 to-emerald-500/20 border border-white/20'
                        : 'bg-white/5 border border-white/10 backdrop-blur-sm'
                    }`}
                  >
                    {searchFormatted?.results?.length ? (
                      <div>
                        {searchFormatted.header && (
                          <p className="text-violet-200 text-sm font-medium mb-3">
                            {searchFormatted.header}
                          </p>
                        )}
                        <ul className="space-y-3">
                          {searchFormatted.results.map((r, j) => (
                            <li
                              key={j}
                              className="py-3 px-4 rounded-xl bg-white/5 border border-white/10"
                            >
                              <a
                                href={r.href}
                                target="_blank"
                                rel="noopener noreferrer"
                                className="text-blue-200 hover:text-white font-medium block mb-1 transition-colors"
                              >
                                {r.title}
                              </a>
                              <span className="text-xs text-white/50 block truncate">{r.href}</span>
                              {r.body && (
                                <p className="text-white/60 text-sm mt-1 line-clamp-2">{r.body}</p>
                              )}
                            </li>
                          ))}
                        </ul>
                      </div>
                    ) : calendarFormatted?.events?.length ? (
                      <div>
                        {calendarFormatted.header && (
                          <p className="text-violet-200 text-sm font-medium mb-3">
                            {calendarFormatted.header}
                          </p>
                        )}
                        <ul className="space-y-2">
                          {calendarFormatted.events.map((evt, j) => {
                            const parts = evt.split(/\s+[—\-]\s+/)
                            const datePart = parts[0]?.trim() ?? ''
                            const title = parts.slice(1).join(' — ').trim() || evt
                            return (
                              <li
                                key={j}
                                className="flex items-center gap-3 py-2 px-3 rounded-xl bg-white/5 border border-white/10"
                              >
                                <span className="text-emerald-300 text-sm font-mono shrink-0">
                                  {datePart}
                                </span>
                                <span className="text-white/90 font-medium">{title}</span>
                              </li>
                            )
                          })}
                        </ul>
                      </div>
                    ) : (
                      <p className="text-white/90 text-[15px] leading-relaxed whitespace-pre-wrap font-medium">
                        {msg.content}
                      </p>
                    )}
                  </div>
                </div>
              )
            })}
            {loading && (
              <div className="flex justify-start">
                <div className="bg-white/5 rounded-2xl px-4 py-3 animate-pulse border border-white/10">
                  <span className="text-violet-300 font-medium">...</span>
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
              className="flex-1 rounded-2xl bg-white/5 border border-white/10 px-5 py-3.5 text-white placeholder-white/40 focus:outline-none focus:ring-2 focus:ring-violet-400/50 focus:border-violet-400/30 text-[15px] font-medium transition-all backdrop-blur-sm"
            />
            <button
              type="submit"
              disabled={loading}
              className="px-6 py-3.5 rounded-2xl bg-gradient-to-r from-blue-500 via-violet-500 to-emerald-500 text-white font-semibold hover:opacity-90 transition-all duration-200 disabled:opacity-50 flex items-center gap-2 shadow-lg shadow-violet-500/25"
            >
              <IconSend />
              Enviar
            </button>
          </form>
        </div>
      </main>

      {/* Modal E-mail */}
      {showEmailModal && (
        <div
          className="fixed inset-0 bg-black/50 backdrop-blur-md flex items-center justify-center z-50 p-4"
          onClick={() => !loading && setShowEmailModal(false)}
        >
          <div
            className="bg-slate-900/95 border border-white/10 rounded-3xl shadow-2xl w-full max-w-md overflow-hidden backdrop-blur-xl"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="p-6 border-b border-white/10">
              <h2 className="text-xl font-bold text-white flex items-center gap-2">
                <IconMail />
                Novo e-mail
              </h2>
            </div>
            <form
              onSubmit={(e) => {
                e.preventDefault()
                if (emailForm.to.trim() && emailForm.subject.trim()) {
                  sendEmail(emailForm.to.trim(), emailForm.subject.trim(), emailForm.body.trim())
                }
              }}
              className="p-6 space-y-4"
            >
              <div>
                <label className="block text-sm font-medium text-violet-200 mb-1.5">Para</label>
                <input
                  type="email"
                  value={emailForm.to}
                  onChange={(e) => setEmailForm((f) => ({ ...f, to: e.target.value }))}
                  placeholder="email@exemplo.com"
                  required
                  className="w-full rounded-xl bg-white/5 border border-white/10 px-4 py-2.5 text-white placeholder-white/40 focus:outline-none focus:ring-2 focus:ring-violet-400/50"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-violet-200 mb-1.5">Assunto</label>
                <input
                  type="text"
                  value={emailForm.subject}
                  onChange={(e) => setEmailForm((f) => ({ ...f, subject: e.target.value }))}
                  placeholder="Assunto do e-mail"
                  required
                  className="w-full rounded-xl bg-white/5 border border-white/10 px-4 py-2.5 text-white placeholder-white/40 focus:outline-none focus:ring-2 focus:ring-violet-400/50"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-violet-200 mb-1.5">Mensagem</label>
                <textarea
                  value={emailForm.body}
                  onChange={(e) => setEmailForm((f) => ({ ...f, body: e.target.value }))}
                  placeholder="Digite sua mensagem..."
                  rows={4}
                  className="w-full rounded-xl bg-white/5 border border-white/10 px-4 py-2.5 text-white placeholder-white/40 focus:outline-none focus:ring-2 focus:ring-violet-400/50 resize-none"
                />
              </div>
              <div className="flex gap-3 pt-2">
                <button
                  type="button"
                  onClick={() => setShowEmailModal(false)}
                  disabled={loading}
                  className="flex-1 py-2.5 rounded-xl border border-white/20 text-white/80 hover:bg-white/10 transition-colors disabled:opacity-50"
                >
                  Cancelar
                </button>
                <button
                  type="submit"
                  disabled={loading}
                  className="flex-1 py-2.5 rounded-xl bg-gradient-to-r from-blue-500 via-violet-500 to-emerald-500 text-white font-semibold hover:opacity-90 transition-all disabled:opacity-50 flex items-center justify-center gap-2"
                >
                  <IconSend />
                  Enviar
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Modal Pesquisa */}
      {showSearchModal && (
        <div
          className="fixed inset-0 bg-black/50 backdrop-blur-md flex items-center justify-center z-50 p-4"
          onClick={() => !loading && setShowSearchModal(false)}
        >
          <div
            className="bg-slate-900/95 border border-white/10 rounded-3xl shadow-2xl w-full max-w-md overflow-hidden backdrop-blur-xl"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="p-6 border-b border-white/10">
              <h2 className="text-xl font-bold text-white flex items-center gap-2">
                <IconSearch />
                Pesquisar na web
              </h2>
            </div>
            <form
              onSubmit={(e) => {
                e.preventDefault()
                if (searchQuery.trim()) runSearch(searchQuery.trim())
              }}
              className="p-6 space-y-4"
            >
              <div>
                <label className="block text-sm font-medium text-violet-200 mb-1.5">O que deseja pesquisar?</label>
                <input
                  type="text"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  placeholder="Ex: clima em São Paulo, receita de bolo..."
                  autoFocus
                  className="w-full rounded-xl bg-white/5 border border-white/10 px-4 py-2.5 text-white placeholder-white/40 focus:outline-none focus:ring-2 focus:ring-violet-400/50"
                />
              </div>
              <div className="flex gap-3 pt-2">
                <button
                  type="button"
                  onClick={() => setShowSearchModal(false)}
                  disabled={loading}
                  className="flex-1 py-2.5 rounded-xl border border-white/20 text-white/80 hover:bg-white/10 transition-colors disabled:opacity-50"
                >
                  Cancelar
                </button>
                <button
                  type="submit"
                  disabled={loading || !searchQuery.trim()}
                  className="flex-1 py-2.5 rounded-xl bg-gradient-to-r from-blue-500 via-violet-500 to-emerald-500 text-white font-semibold hover:opacity-90 transition-all disabled:opacity-50 flex items-center justify-center gap-2"
                >
                  <IconSearch />
                  Pesquisar
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Modal Resumos */}
      {showSummarizeModal && (
        <div
          className="fixed inset-0 bg-black/50 backdrop-blur-md flex items-center justify-center z-50 p-4"
          onClick={() => !loading && setShowSummarizeModal(false)}
        >
          <div
            className="bg-slate-900/95 border border-white/10 rounded-3xl shadow-2xl w-full max-w-lg overflow-hidden backdrop-blur-xl"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="p-6 border-b border-white/10">
              <h2 className="text-xl font-bold text-white flex items-center gap-2">
                <IconSummarize />
                Resumir
              </h2>
              <p className="text-sm text-white/60 mt-1">
                Cole uma URL ou o texto que deseja resumir
              </p>
            </div>
            <form
              onSubmit={(e) => {
                e.preventDefault()
                if (summarizeInput.trim()) runSummarize(summarizeInput.trim())
              }}
              className="p-6 space-y-4"
            >
              <div>
                <textarea
                  value={summarizeInput}
                  onChange={(e) => setSummarizeInput(e.target.value)}
                  placeholder="https://exemplo.com/artigo ou cole o texto aqui..."
                  rows={6}
                  autoFocus
                  className="w-full rounded-xl bg-white/5 border border-white/10 px-4 py-2.5 text-white placeholder-white/40 focus:outline-none focus:ring-2 focus:ring-violet-400/50 resize-none"
                />
              </div>
              <div className="flex gap-3 pt-2">
                <button
                  type="button"
                  onClick={() => setShowSummarizeModal(false)}
                  disabled={loading}
                  className="flex-1 py-2.5 rounded-xl border border-white/20 text-white/80 hover:bg-white/10 transition-colors disabled:opacity-50"
                >
                  Cancelar
                </button>
                <button
                  type="submit"
                  disabled={loading || !summarizeInput.trim()}
                  className="flex-1 py-2.5 rounded-xl bg-gradient-to-r from-blue-500 via-violet-500 to-emerald-500 text-white font-semibold hover:opacity-90 transition-all disabled:opacity-50 flex items-center justify-center gap-2"
                >
                  <IconSummarize />
                  Resumir
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  )
}
