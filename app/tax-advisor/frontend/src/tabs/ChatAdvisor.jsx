import React, { useState, useRef, useEffect } from 'react'

const API_BASE = import.meta.env.VITE_API_BASE_URL || 'https://func-ht-taxb-p-cin-01.azurewebsites.net/api'

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

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

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
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: text, history: formattedHistory }),
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
          <p className="card-subtitle">Conversational RAG tax guidance updated for FY 2025-26 & Budget 2025</p>
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
