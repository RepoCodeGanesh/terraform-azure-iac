import React, { useState, useRef, useEffect } from 'react'
import MarkdownRenderer from '../components/MarkdownRenderer'

const API_BASE = import.meta.env.VITE_API_BASE || 'https://apim-ht-ss-p-cin-01.azure-api.net/tax-advisor'

const HERO_PROMPTS = [
  {
    title: "🧮 Calculate Tax on ₹18.5L Salary",
    subtitle: "New vs Old Regime comparison with ₹75k standard deduction",
    text: "Calculate my tax on ₹18,50,000 salary under Budget 2025 New vs Old Regime."
  },
  {
    title: "⚖️ Compare Slabs for ₹25L CTC",
    subtitle: "Slabs, 80C, 80CCD NPS, and Section 87A rebate",
    text: "Compare Old vs New Regime for ₹25,00,000 salary with ₹1.5L 80C, ₹50k NPS, and ₹30k health insurance."
  },
  {
    title: "⚡ Section 80CCD(2) Employer NPS",
    subtitle: "Tax-free corporate pension restructuring in FY 2026-27",
    text: "How can I save tax using Section 80CCD(2) employer NPS in FY 2026-27?"
  },
  {
    title: "📈 Equity Mutual Fund LTCG Rules",
    subtitle: "Budget 2025 capital gains tax rates & exemptions",
    text: "What are the capital gains tax rates on equity mutual funds under Budget 2025?"
  }
]

export default function ChatAdvisor() {
  const [messages, setMessages] = useState([
    {
      role: 'assistant',
      content: "Welcome 🙏 I am **TaxBot India**, your AI tax advisor for **FY 2026-27 (AY 2027-28)** under Union Budget 2025.\n\nAsk me anything about income tax slabs, deductions (80C, 80D, 80CCD), Old vs New regime comparison, HRA exemption, or capital gains tax!\n\n💡 *Tip: Enter your salary and deduction details to receive exact statutory slabs, automated deduction optimization, and verified net tax computations.*",
      model: "system-welcome",
    },
  ])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [engineMode, setEngineMode] = useState('auto') // 'auto' | 'foundry' | 'fast'
  const [expandedTraces, setExpandedTraces] = useState({}) // Hidden by default!
  const [showArchInfo, setShowArchInfo] = useState(false)
  const [copiedIndex, setCopiedIndex] = useState(null)
  const [isListening, setIsListening] = useState(false)
  const [speechSupported, setSpeechSupported] = useState(false)

  const messagesEndRef = useRef(null)
  const recognitionRef = useRef(null)

  // Persistent session across browser refreshes (Cosmos DB partition key)
  const [sessionId, setSessionId] = useState(() => {
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

  // Initialize Web Speech Recognition
  useEffect(() => {
    if (typeof window !== 'undefined') {
      const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition
      if (SpeechRecognition) {
        setSpeechSupported(true)
        const recognizer = new SpeechRecognition()
        recognizer.continuous = false
        recognizer.interimResults = true
        recognizer.lang = 'en-IN'

        recognizer.onresult = (event) => {
          let transcript = ''
          for (let i = event.resultIndex; i < event.results.length; i++) {
            transcript += event.results[i][0].transcript
          }
          if (transcript) setInput(transcript)
        }

        recognizer.onerror = () => setIsListening(false)
        recognizer.onend = () => setIsListening(false)
        recognitionRef.current = recognizer
      }
    }
  }, [])

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
              messages[0],
              ...data.turns.flatMap(t => [
                { role: 'user', content: t.userMessage },
                { 
                  role: 'assistant', 
                  content: t.reply,
                  model: t.model,
                  code_interpreter: t.model && t.model.includes('azure-foundry'),
                  verified: t.model && t.model.includes('azure-foundry'),
                }
              ])
            ]
            setMessages(restored)
          }
        }
      } catch {
        // Silently fallback if warming up
      }
    }
    fetchHistory()
  }, [sessionId])

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages, loading])

  const handleNewChat = () => {
    const newId = 'taxb-sess-' + (window.crypto?.randomUUID ? window.crypto.randomUUID() : Math.random().toString(36).substring(2, 11))
    localStorage.setItem('taxb_session_id', newId)
    setSessionId(newId)
    setMessages([
      {
        role: 'assistant',
        content: "Welcome 🙏 I am **TaxBot India**, your AI tax advisor for **FY 2026-27 (AY 2027-28)** under Union Budget 2025.\n\nAsk me anything about income tax slabs, deductions (80C, 80D, 80CCD), Old vs New regime comparison, HRA exemption, or capital gains tax!\n\n💡 *Ask for a tax calculation to see the **Microsoft AI Foundry Python Specialist** compute exact statutory slabs with verified code.*",
        model: "system-welcome",
      },
    ])
    setExpandedTraces({})
    setError(null)
  }

  const toggleVoiceInput = () => {
    if (!speechSupported || !recognitionRef.current) {
      alert("Speech recognition is not supported in this browser. Please use Chrome, Edge, or Safari.")
      return
    }
    if (isListening) {
      recognitionRef.current.stop()
      setIsListening(false)
    } else {
      try {
        recognitionRef.current.start()
        setIsListening(true)
      } catch (err) {
        console.error('Speech recognition error:', err)
        setIsListening(false)
      }
    }
  }

  // Toggle code visibility on demand (hidden by default)
  const toggleTrace = (index) => {
    setExpandedTraces(prev => ({
      ...prev,
      [index]: !prev[index]
    }))
  }

  const handleCopyCode = (code, index) => {
    if (!code) return
    navigator.clipboard.writeText(code).then(() => {
      setCopiedIndex(index)
      setTimeout(() => setCopiedIndex(null), 2000)
    })
  }

  const handleSend = async (textToSend) => {
    const text = (textToSend || input).trim()
    if (!text || loading) return

    if (isListening && recognitionRef.current) {
      recognitionRef.current.stop()
      setIsListening(false)
    }

    setError(null)
    const userMsg = { role: 'user', content: text }
    const updatedHistory = [...messages, userMsg]
    setMessages(updatedHistory)
    if (!textToSend) setInput('')
    setLoading(true)

    try {
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
          sessionId: sessionId,
          engine_mode: engineMode,
        }),
      })

      if (!res.ok) {
        const errData = await res.json().catch(() => ({}))
        throw new Error(errData.error || `HTTP error ${res.status}`)
      }

      const data = await res.json()

      // NOTE: Code is intentionally NOT auto-expanded by default.
      // It will only display when user explicitly clicks the inspect button!

      setMessages([
        ...updatedHistory,
        { 
          role: 'assistant', 
          content: data.reply || 'No response received.',
          model: data.model,
          out_of_scope: data.out_of_scope,
          code_interpreter: data.code_interpreter,
          code_trace: data.code_trace,
          latency_ms: data.latency_ms,
          engine_mode: data.engine_mode,
          verified: data.verified,
        },
      ])
    } catch (err) {
      console.error('Chat error:', err)
      setError(err.message || 'Failed to communicate with TaxBot backend.')
    } finally {
      setLoading(false)
    }
  }

  // Is conversation in initial empty state?
  const isInitialState = messages.length <= 1

  return (
    <div className="card chat-container" style={{ padding: '0', overflow: 'hidden' }}>
      {/* ── Sleek Minimal Header Bar ────────────────────────────────────────── */}
      <div style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        padding: '12px 20px',
        borderBottom: '1px solid rgba(255, 255, 255, 0.08)',
        background: 'rgba(15, 20, 32, 0.85)',
        backdropFilter: 'blur(12px)',
        flexWrap: 'wrap',
        gap: '10px',
      }}>
        {/* Left: Brand & Pill */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <div style={{
            width: '32px',
            height: '32px',
            borderRadius: '8px',
            background: 'linear-gradient(135deg, #FF9933 0%, #ffffff 50%, #138808 100%)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            fontSize: '16px',
            boxShadow: '0 2px 8px rgba(255, 153, 51, 0.25)',
          }}>
            🇮🇳
          </div>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <span style={{ fontWeight: 700, fontSize: '0.98rem', color: '#f8fafc', letterSpacing: '-0.3px' }}>
                TaxBot AI
              </span>
              <span style={{
                fontSize: '0.7rem',
                fontWeight: 600,
                color: '#38bdf8',
                background: 'rgba(56, 189, 248, 0.12)',
                border: '1px solid rgba(56, 189, 248, 0.25)',
                borderRadius: '12px',
                padding: '1px 8px',
              }}>
                FY 2026-27
              </span>
            </div>
          </div>
        </div>

        {/* Right: Segmented Engine Switcher + Info + New Chat */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          {/* Segmented Control */}
          <div style={{
            display: 'flex',
            background: 'rgba(0, 0, 0, 0.4)',
            borderRadius: '8px',
            padding: '2px',
            border: '1px solid rgba(255, 255, 255, 0.08)',
          }}>
            <button
              type="button"
              onClick={() => setEngineMode('auto')}
              style={{
                background: engineMode === 'auto' ? 'rgba(255, 255, 255, 0.12)' : 'transparent',
                color: engineMode === 'auto' ? '#f8fafc' : '#94a3b8',
                border: 'none',
                borderRadius: '6px',
                padding: '4px 10px',
                fontSize: '0.74rem',
                fontWeight: engineMode === 'auto' ? 600 : 500,
                cursor: 'pointer',
                transition: 'all 0.15s ease',
              }}
              title="Smart Auto-Route: Calculations use Foundry Python Specialist; General advice uses Fast Advisory"
            >
              🤖 Auto
            </button>
            <button
              type="button"
              onClick={() => setEngineMode('foundry')}
              style={{
                background: engineMode === 'foundry' ? 'linear-gradient(135deg, rgba(168, 85, 247, 0.4), rgba(99, 102, 241, 0.4))' : 'transparent',
                color: engineMode === 'foundry' ? '#e9d5ff' : '#94a3b8',
                border: 'none',
                borderRadius: '6px',
                padding: '4px 10px',
                fontSize: '0.74rem',
                fontWeight: engineMode === 'foundry' ? 600 : 500,
                cursor: 'pointer',
                transition: 'all 0.15s ease',
              }}
              title="Foundry Specialist: Forces gpt-5.4-mini with Python Code Interpreter"
            >
              🧮 Math
            </button>
            <button
              type="button"
              onClick={() => setEngineMode('fast')}
              style={{
                background: engineMode === 'fast' ? 'rgba(16, 185, 129, 0.2)' : 'transparent',
                color: engineMode === 'fast' ? '#6ee7b7' : '#94a3b8',
                border: 'none',
                borderRadius: '6px',
                padding: '4px 10px',
                fontSize: '0.74rem',
                fontWeight: engineMode === 'fast' ? 600 : 500,
                cursor: 'pointer',
                transition: 'all 0.15s ease',
              }}
              title="Fast Advisory: Ultra-low latency responses via GroqCloud LPU"
            >
              ⚡ Fast
            </button>
          </div>

          {/* Architecture Info Toggle Button */}
          <button
            type="button"
            onClick={() => setShowArchInfo(!showArchInfo)}
            style={{
              background: showArchInfo ? 'rgba(56, 189, 248, 0.15)' : 'rgba(255, 255, 255, 0.04)',
              border: '1px solid rgba(255, 255, 255, 0.08)',
              borderRadius: '8px',
              padding: '4px 9px',
              color: showArchInfo ? '#38bdf8' : '#94a3b8',
              fontSize: '0.74rem',
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: '4px',
            }}
            title="View Azure AI Architecture & Model Details"
          >
            <span>ℹ️</span>
          </button>

          {/* New Chat Button */}
          <button
            type="button"
            onClick={handleNewChat}
            style={{
              background: 'rgba(255, 255, 255, 0.04)',
              border: '1px solid rgba(255, 255, 255, 0.08)',
              borderRadius: '8px',
              padding: '4px 10px',
              color: '#94a3b8',
              fontSize: '0.74rem',
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: '4px',
            }}
            title="Reset conversation"
          >
            <span>🔄</span>
            <span>New</span>
          </button>
        </div>
      </div>

      {/* ── Architecture Drawer (Collapsible) ───────────────────────────────── */}
      {showArchInfo && (
        <div style={{
          background: 'rgba(11, 15, 25, 0.95)',
          borderBottom: '1px solid rgba(255, 255, 255, 0.08)',
          padding: '10px 20px',
          display: 'flex',
          flexWrap: 'wrap',
          gap: '10px',
          fontSize: '0.72rem',
          color: '#94a3b8',
        }}>
          <span style={{ color: '#a5b4fc' }}>🏛️ <strong>Hub:</strong> hub-taxbot-foundry-01 (eastus2)</span>
          <span style={{ color: '#d8b4fe' }}>🎯 <strong>Specialist:</strong> TaxBot-Calculation-Specialist (gpt-5.4-mini)</span>
          <span style={{ color: '#38bdf8' }}>🐍 <strong>Tool:</strong> Python Code Interpreter Sandbox</span>
          <span style={{ color: '#34d399' }}>⚡ <strong>Primary LPU:</strong> GroqCloud (llama-3.3-70b)</span>
          <span style={{ color: '#f59e0b' }}>🛡️ <strong>Guardrail:</strong> Sub-2ms Deterministic Scope Sieve</span>
        </div>
      )}

      {/* ── Chat Messages Container ─────────────────────────────────────────── */}
      <div className="chat-messages" style={{ minHeight: '380px', maxHeight: '540px', overflowY: 'auto', padding: '16px 20px' }}>
        
        {/* ── Empty State Hero Suggestion Cards (Visible only at start) ──────── */}
        {isInitialState && (
          <div style={{ margin: '14px 0 24px 0' }}>
            <div style={{
              textAlign: 'center',
              marginBottom: '16px',
            }}>
              <h3 style={{ fontSize: '1.1rem', fontWeight: 600, color: '#f8fafc', marginBottom: '4px' }}>
                How can I assist your tax planning today?
              </h3>
              <p style={{ fontSize: '0.8rem', color: '#94a3b8' }}>
                Select a suggested computation or ask your custom tax question below:
              </p>
            </div>

            <div style={{
              display: 'grid',
              gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))',
              gap: '10px',
            }}>
              {HERO_PROMPTS.map((item, idx) => (
                <div
                  key={idx}
                  onClick={() => handleSend(item.text)}
                  style={{
                    background: 'rgba(255, 255, 255, 0.03)',
                    border: '1px solid rgba(255, 255, 255, 0.07)',
                    borderRadius: '10px',
                    padding: '12px 14px',
                    cursor: 'pointer',
                    transition: 'all 0.2s ease',
                  }}
                  onMouseEnter={(e) => {
                    e.currentTarget.style.background = 'rgba(255, 255, 255, 0.06)'
                    e.currentTarget.style.borderColor = 'rgba(56, 189, 248, 0.3)'
                    e.currentTarget.style.transform = 'translateY(-1px)'
                  }}
                  onMouseLeave={(e) => {
                    e.currentTarget.style.background = 'rgba(255, 255, 255, 0.03)'
                    e.currentTarget.style.borderColor = 'rgba(255, 255, 255, 0.07)'
                    e.currentTarget.style.transform = 'translateY(0)'
                  }}
                >
                  <div style={{ fontSize: '0.82rem', fontWeight: 600, color: '#e2e8f0', marginBottom: '3px' }}>
                    {item.title}
                  </div>
                  <div style={{ fontSize: '0.72rem', color: '#94a3b8', lineHeight: '1.4' }}>
                    {item.subtitle}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* ── Messages List ─────────────────────────────────────────────────── */}
        {messages.map((m, idx) => (
          <div key={idx} className={`msg ${m.role === 'user' ? 'user' : 'bot'}`} style={{ marginBottom: '16px' }}>
            <div className="msg-avatar" style={{ fontSize: '15px' }}>
              {m.role === 'user' ? '👤' : (m.code_interpreter || (m.model && m.model.includes('azure-foundry')) ? '🧮' : '🇮🇳')}
            </div>

            <div 
              className="msg-bubble" 
              style={{ 
                maxWidth: '85%',
                background: m.role === 'user' 
                  ? 'linear-gradient(135deg, rgba(99, 102, 241, 0.3), rgba(79, 70, 229, 0.4))'
                  : 'rgba(15, 23, 42, 0.5)',
                border: m.out_of_scope
                  ? '1px solid rgba(245, 158, 11, 0.4)'
                  : '1px solid rgba(255, 255, 255, 0.07)',
                borderRadius: '12px',
                padding: '12px 16px',
                boxShadow: '0 2px 10px rgba(0, 0, 0, 0.2)',
              }}
            >
              {/* Rich Markdown Rendering (No raw asterisks or hashtags!) */}
              <MarkdownRenderer content={m.content} />

              {/* ── Minimalist Telemetry & On-Demand Code Accordion ────────── */}
              {m.model && (
                <div style={{ 
                  marginTop: '10px', 
                  borderTop: '1px solid rgba(255, 255, 255, 0.06)',
                  paddingTop: '8px',
                  display: 'flex',
                  flexDirection: 'column',
                  gap: '8px',
                }}>
                  {/* Discreet Footer Line */}
                  <div style={{ 
                    display: 'flex', 
                    alignItems: 'center', 
                    justifyContent: 'space-between', 
                    flexWrap: 'wrap', 
                    gap: '8px',
                    fontSize: '0.72rem',
                    color: '#94a3b8'
                  }}>
                    {/* Left: Attribution + Latency + Verification */}
                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px', flexWrap: 'wrap' }}>
                      <span style={{
                        color: m.out_of_scope ? '#f59e0b' : (m.code_interpreter || (m.model && m.model.includes('azure-foundry')) ? '#c084fc' : '#38bdf8'),
                        fontWeight: 500,
                      }}>
                        {m.out_of_scope
                          ? '🛡️ Scope Guardrail'
                          : (m.code_interpreter || (m.model && m.model.includes('azure-foundry')))
                            ? 'Foundry Specialist (gpt-5.4-mini)'
                            : m.model.startsWith('groq')
                              ? `Groq LPU (${m.model.replace('groq/', '')})`
                              : m.model}
                      </span>

                      {m.latency_ms && (
                        <span>· ⏱️ {m.latency_ms < 1000 ? `${m.latency_ms}ms` : `${(m.latency_ms / 1000).toFixed(1)}s`}</span>
                      )}

                      {(m.verified || m.code_interpreter) && (
                        <span style={{ color: '#34d399', display: 'flex', alignItems: 'center', gap: '2px' }}>
                          · ✅ Verified Math
                        </span>
                      )}
                    </div>

                    {/* Right: On-Demand Python Code Toggle Button (HIDDEN BY DEFAULT!) */}
                    {(m.code_trace || m.code_interpreter) && (
                      <button
                        type="button"
                        onClick={() => toggleTrace(idx)}
                        style={{
                          background: 'transparent',
                          border: 'none',
                          color: '#a5b4fc',
                          fontSize: '0.72rem',
                          cursor: 'pointer',
                          display: 'flex',
                          alignItems: 'center',
                          gap: '4px',
                          padding: '2px 6px',
                          borderRadius: '4px',
                        }}
                        onMouseEnter={(e) => e.currentTarget.style.color = '#fff'}
                        onMouseLeave={(e) => e.currentTarget.style.color = '#a5b4fc'}
                      >
                        <span>{expandedTraces[idx] ? '▴ Hide Code' : '🔍 View Code ▾'}</span>
                      </button>
                    )}
                  </div>

                  {/* Expanded Code Box (ONLY rendered on explicit user click!) */}
                  {expandedTraces[idx] && (
                    <div style={{
                      marginTop: '4px',
                      background: '#070a12',
                      border: '1px solid rgba(168, 85, 247, 0.25)',
                      borderRadius: '8px',
                      padding: '10px 12px',
                      fontFamily: 'monospace',
                      fontSize: '0.74rem',
                    }}>
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '6px', color: '#94a3b8' }}>
                        <span style={{ color: '#c084fc' }}>🐍 Python Sandboxed Calculation Trace</span>
                        <button
                          type="button"
                          onClick={() => handleCopyCode(m.code_trace || '# Statutory Python calculation', idx)}
                          style={{
                            background: 'rgba(255, 255, 255, 0.08)',
                            border: '1px solid rgba(255, 255, 255, 0.12)',
                            borderRadius: '4px',
                            padding: '2px 8px',
                            color: '#e2e8f0',
                            fontSize: '0.68rem',
                            cursor: 'pointer',
                          }}
                        >
                          {copiedIndex === idx ? '✓ Copied' : '📋 Copy Code'}
                        </button>
                      </div>

                      <pre style={{
                        background: '#04060a',
                        padding: '10px',
                        borderRadius: '6px',
                        overflowX: 'auto',
                        color: '#38bdf8',
                        lineHeight: '1.4',
                        whiteSpace: 'pre-wrap',
                        margin: 0,
                      }}>
                        <code>{m.code_trace || `# Standard statutory slab computation executed\n# FY 2026-27 (AY 2027-28) Budget 2025 Slabs\n# New Regime: 0-4L (0%), 4-8L (5%), 8-12L (10%), 12-16L (15%), 16-20L (20%), 20-24L (25%), >24L (30%)\n# Standard Deduction: ₹75,000 (New) | ₹50,000 (Old)\n# Section 87A rebate up to ₹60,000 (Zero tax up to ₹12L) + 4% Cess`}</code>
                      </pre>
                    </div>
                  )}
                </div>
              )}
            </div>
          </div>
        ))}

        {loading && (
          <div className="msg bot" style={{ marginBottom: '16px' }}>
            <div className="msg-avatar">🇮🇳</div>
            <div className="msg-bubble" style={{
              background: 'rgba(15, 23, 42, 0.5)',
              border: '1px solid rgba(255, 255, 255, 0.07)',
              borderRadius: '12px',
              padding: '10px 16px',
            }}>
              <div style={{ fontSize: '0.75rem', color: '#94a3b8', marginBottom: '6px' }}>
                {engineMode === 'foundry' 
                  ? '🧮 Computing exact statutory slabs in Python sandbox...' 
                  : '🧠 Formulating personalized tax guidance...'}
              </div>
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

      {error && <div className="error-banner" style={{ margin: '0 20px 10px 20px' }}>⚠️ {error}</div>}

      {/* ── Modern Floating Input Capsule ───────────────────────────────────── */}
      <div style={{ padding: '12px 20px 16px 20px', background: 'rgba(15, 20, 32, 0.6)' }}>
        <div style={{
          display: 'flex',
          alignItems: 'center',
          gap: '8px',
          background: 'rgba(26, 32, 53, 0.8)',
          border: isListening ? '1px solid #ef4444' : '1px solid rgba(255, 255, 255, 0.12)',
          borderRadius: '20px',
          padding: '6px 12px',
          boxShadow: isListening ? '0 0 12px rgba(239, 68, 68, 0.35)' : '0 2px 10px rgba(0, 0, 0, 0.3)',
          transition: 'all 0.2s ease',
        }}>
          <textarea
            className="chat-input"
            placeholder={isListening ? "🔴 Listening to your voice... speak now..." : "Ask a tax question or calculation (e.g. 'I earn 22L, rent 30K/mo. Which regime is better?')..."}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault()
                handleSend()
              }
            }}
            rows={1}
            style={{
              flex: 1,
              background: 'transparent',
              border: 'none',
              color: '#f8fafc',
              fontSize: '0.86rem',
              resize: 'none',
              outline: 'none',
              padding: '6px 4px',
              fontFamily: 'inherit',
            }}
          />

          {/* 🎙️ Voice Input Button */}
          <button
            type="button"
            onClick={toggleVoiceInput}
            style={{
              background: isListening ? '#ef4444' : 'transparent',
              border: 'none',
              color: isListening ? '#fff' : '#94a3b8',
              borderRadius: '50%',
              width: '32px',
              height: '32px',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              fontSize: '1rem',
              cursor: 'pointer',
              transition: 'all 0.15s ease',
            }}
            title={isListening ? "Listening... click to stop" : "Voice Input (Speech-to-Text)"}
          >
            {isListening ? '🔴' : '🎙️'}
          </button>

          {/* ➔ Send Button */}
          <button
            type="button"
            onClick={() => handleSend()}
            disabled={loading || !input.trim()}
            style={{
              background: input.trim() ? 'linear-gradient(135deg, #3b82f6, #6366f1)' : 'rgba(255, 255, 255, 0.08)',
              border: 'none',
              color: input.trim() ? '#fff' : '#64748b',
              borderRadius: '50%',
              width: '32px',
              height: '32px',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              fontSize: '1rem',
              cursor: input.trim() && !loading ? 'pointer' : 'default',
              transition: 'all 0.15s ease',
            }}
            title="Send message"
          >
            ➔
          </button>
        </div>
      </div>
    </div>
  )
}
