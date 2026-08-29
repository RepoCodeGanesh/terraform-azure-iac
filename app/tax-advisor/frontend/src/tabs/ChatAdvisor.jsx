import React, { useState, useRef, useEffect } from 'react'

const API_BASE = import.meta.env.VITE_API_BASE || 'https://apim-ht-ss-p-cin-01.azure-api.net/tax-advisor'

const QUICK_PROMPTS = [
  "I earn ₹18L per year. Which tax regime is better for me?",
  "How can I save tax using Section 80CCD(2) employer NPS?",
  "What is the capital gains tax on equity mutual funds in FY 2026-27?",
  "Can I claim HRA and home loan interest deduction together?",
  "What is Section 87A rebate limit under the New Regime?",
]

export default function ChatAdvisor() {
  const [messages, setMessages] = useState([
    {
      role: 'assistant',
      content: "Welcome 🙏 I am TaxBot India, your AI tax advisor for FY 2026-27 (AY 2027-28).\n\nAsk me anything about income tax slabs, deductions (80C, 80D, 80CCD), Old vs New regime comparison, HRA exemption, or capital gains tax!",
    },
  ])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const messagesEndRef = useRef(null)

  // Persistent session across browser refreshes (Cosmos DB partition key)
  const [sessionId] = useState(() => {
    if (typeof window !== 'undefined') {
      let saved = localStorage.getItem('taxb_session_id')
      if (!saved) {
        saved = 'taxb-sess-' + (window.crypto?.randomUUID ? window.crypto.randomUUID() : Math.random().toString(36).substring(2, 11))
        localStorage.setItem('taxb_session_id', saved)
      }
      return saved
    }
    return 'default-session'
  })

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  // Restore past session history from Cosmos DB on load
  useEffect(() => {
    if (!sessionId) return
    const fetchHistory = async () => {
      try {
        const res = await fetch(`${API_BASE}/history?sessionId=${encodeURIComponent(sessionId)}`)
        if (res.ok) {
          const data = await res.json()
          if (data.turns && data.turns.length > 0) {
            const restored = [
              messages[0], // welcome message
              ...data.turns.flatMap(t => [
                { role: 'user', content: t.userMessage },
                { role: 'assistant', content: t.reply }
              ])
            ]
            setMessages(restored)
          }
        }
      } catch {
        // Silently fallback to fresh session if history service is warming up
      }
    }
    fetchHistory()
  }, [sessionId])

  useEffect(() => {
    scrollToBottom()
  }, [messages, loading])

  const handleSend = async (textToSend) => {
    const text = (textToSend || input).trim()
    if (!text || loading) return

    setError(null)
    const userMsg = { role: 'user', content: text }
    const updatedHistory = [...messages, userMsg]
    setMessages(updatedHistory)
    if (!textToSend) setInput('')
    setLoading(true)

    try {
      // Format history for backend
      const formattedHistory = updatedHistory.slice(1, -1).map((m) => ({
        role: m.role,
        content: m.content,
      }))

      const res = await fetch(`${API_BASE}/chat`, {
        method: 'POST',
        headers: { 
          'Content-Type': 'application/json',
          'x-session-id': sessionId
        },
        body: JSON.stringify({ 
          message: text, 
          history: formattedHistory,
          sessionId: sessionId 
        }),
      })

      if (!res.ok) {
        const errData = await res.json().catch(() => ({}))
        throw new Error(errData.error || `HTTP error ${res.status}`)
      }

      const data = await res.json()
      setMessages([
        ...updatedHistory,
        { role: 'assistant', content: data.reply || 'No response received.' },
      ])
    } catch (err) {
      console.error('Chat error:', err)
      setError(err.message || 'Failed to communicate with TaxBot backend.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="card chat-container">
      <div className="card-header" style={{ marginBottom: '12px' }}>
        <div className="card-icon">💬</div>
        <div>
          <h2 className="card-title">AI Tax Advisor Chat</h2>
          <p className="card-subtitle">Conversational RAG tax guidance updated for FY 2026-27 & Budget 2025</p>
        </div>
      </div>

      <div className="quick-prompts">
        {QUICK_PROMPTS.map((prompt, idx) => (
          <button
            key={idx}
            className="quick-prompt-btn"
            onClick={() => handleSend(prompt)}
            disabled={loading}
          >
            {prompt}
          </button>
        ))}
      </div>

      <div className="chat-messages">
        {messages.map((m, idx) => (
          <div key={idx} className={`msg ${m.role === 'user' ? 'user' : 'bot'}`}>
            <div className="msg-avatar">{m.role === 'user' ? '👤' : '🇮🇳'}</div>
            <div className="msg-bubble" style={{ whiteSpace: 'pre-line' }}>
              {m.content}
            </div>
          </div>
        ))}

        {loading && (
          <div className="msg bot">
            <div className="msg-avatar">🇮🇳</div>
            <div className="msg-bubble">
              <div className="loading-dots">
                <span></span>
                <span></span>
                <span></span>
              </div>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {error && <div className="error-banner">⚠️ {error}</div>}

      <div className="chat-input-row">
        <textarea
          className="chat-input"
          placeholder="Ask a tax question (e.g. 'I earn 22L, have 80C 1.5L, rent 30K/mo. Which regime is better?')..."
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
              e.preventDefault()
              handleSend()
            }
          }}
          rows={2}
        />
        <button
          className="chat-send-btn"
          onClick={() => handleSend()}
          disabled={loading || !input.trim()}
          title="Send message"
        >
          ➔
        </button>
      </div>
    </div>
  )
}
