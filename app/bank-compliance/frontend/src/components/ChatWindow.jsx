import React, { useState } from 'react'
import { Send, Bot, User, Shield, Sparkles } from 'lucide-react'
import PIIBanner from './PIIBanner'
import CitationCard from './CitationCard'

export default function ChatWindow({ selectedCircular }) {
  const [messages, setMessages] = useState([
    {
      role: 'assistant',
      text: 'Welcome to BankCompliance AI 🙏\n\nI am your Enterprise Banking Regulatory Copilot. Ask any compliance question regarding RBI Master Directions (KYC, IT Governance, Cloud Outsourcing, Tokenisation). All PAN, Aadhaar, and account numbers are auto-redacted in real-time.',
      citations: [],
      pii: []
    }
  ])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)

  const handleSend = async (e) => {
    e.preventDefault()
    if (!input.trim() || loading) return

    const userQuery = input.trim()
    setInput('')
    setMessages(prev => [...prev, { role: 'user', text: userQuery }])
    setLoading(true)

    try {
      const isLocal = typeof window !== 'undefined' && (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1')
      const defaultEndpoint = isLocal
        ? 'http://localhost:8000/api/v1/compliance/query'
        : 'http://bankc-api-ht-cin.centralindia.cloudapp.azure.com/api/v1/compliance/query'
      const apiEndpoint = import.meta.env.VITE_API_URL || defaultEndpoint
      const res = await fetch(apiEndpoint, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          query: userQuery,
          department: 'legal-compliance',
          circular: selectedCircular !== 'All' ? selectedCircular : undefined
        })
      })
      const data = await res.json()
      
      setMessages(prev => [...prev, {
        role: 'assistant',
        text: data.answer,
        citations: data.citations || [],
        pii: data.pii_redacted || []
      }])
    } catch (err) {
      setMessages(prev => [...prev, {
        role: 'assistant',
        text: '⚠️ Unable to connect to BankCompliance AKS backend API. Please ensure the cluster and backend services are active.',
        citations: [],
        pii: []
      }])
    } finally {
      setLoading(false)
    }
  }

  return (
    <div style={{ flex: 1, display: 'flex', flexDirection: 'column', height: '100%' }}>
      {/* Messages */}
      <div style={{ flex: 1, overflowY: 'auto', padding: '20px', display: 'flex', flexDirection: 'column', gap: '16px' }}>
        {messages.map((m, idx) => (
          <div key={idx} style={{
            display: 'flex',
            gap: '12px',
            alignSelf: m.role === 'user' ? 'flex-end' : 'flex-start',
            maxWidth: '85%'
          }}>
            {m.role === 'assistant' && (
              <div style={{ width: '32px', height: '32px', borderRadius: '50%', background: '#3b82f6', display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0 }}>
                <Bot size={18} color="#fff" />
              </div>
            )}
            <div style={{
              background: m.role === 'user' ? '#1d4ed8' : '#111827',
              border: m.role === 'user' ? 'none' : '1px solid #374151',
              borderRadius: '12px',
              padding: '14px 18px',
              color: '#f3f4f6',
              fontSize: '0.95rem',
              lineHeight: '1.5',
              whiteSpace: 'pre-line'
            }}>
              <PIIBanner piiList={m.pii} />
              {m.text}
              {m.citations && m.citations.length > 0 && (
                <div style={{ marginTop: '12px', borderTop: '1px solid #374151', paddingTop: '10px' }}>
                  <div style={{ fontSize: '0.8rem', fontWeight: 600, color: '#f59e0b', textTransform: 'uppercase' }}>
                    Auditable RBI Master Direction Citations:
                  </div>
                  {m.citations.map((c, cIdx) => (
                    <CitationCard key={cIdx} citation={c} />
                  ))}
                </div>
              )}
            </div>
          </div>
        ))}
        {loading && (
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', color: '#9ca3af', fontSize: '0.9rem' }}>
            <Sparkles size={16} className="animate-spin" />
            <span>Consulting Qdrant Vector DB & RBI Master Directions...</span>
          </div>
        )}
      </div>

      {/* Input */}
      <form onSubmit={handleSend} style={{ padding: '16px 20px', background: '#111827', borderTop: '1px solid #374151', display: 'flex', gap: '12px' }}>
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Ask an RBI regulatory compliance question (e.g. KYC for NRI accounts, IT localization)..."
          style={{
            flex: 1,
            background: '#1f2937',
            border: '1px solid #374151',
            borderRadius: '8px',
            padding: '12px 16px',
            color: '#fff',
            fontSize: '0.95rem',
            outline: 'none'
          }}
        />
        <button
          type="submit"
          disabled={loading}
          style={{
            background: '#3b82f6',
            border: 'none',
            borderRadius: '8px',
            padding: '12px 20px',
            color: '#fff',
            cursor: 'pointer',
            display: 'flex',
            alignItems: 'center',
            gap: '6px',
            fontWeight: 600
          }}
        >
          <Send size={16} />
          Send
        </button>
      </form>
    </div>
  )
}
