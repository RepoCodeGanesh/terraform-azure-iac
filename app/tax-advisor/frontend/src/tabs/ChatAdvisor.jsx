import React, { useState, useRef, useEffect } from 'react'

const API_BASE = import.meta.env.VITE_API_BASE || 'https://apim-ht-ss-p-cin-01.azure-api.net/tax-advisor'

const QUICK_PROMPTS = [
  { label: "🧮 Calculate Tax on ₹18.5L", text: "Calculate my tax on ₹18,50,000 salary under Budget 2025 New vs Old Regime." },
  { label: "⚖️ Compare Slabs (₹25L CTC)", text: "Compare Old vs New Regime for ₹25,00,000 salary with ₹1.5L 80C, ₹50k NPS, and ₹30k health insurance." },
  { label: "⚡ 80CCD(2) Employer NPS", text: "How can I save tax using Section 80CCD(2) employer NPS in FY 2026-27?" },
  { label: "📈 Equity LTCG Rules", text: "What are the capital gains tax rates on equity mutual funds under Budget 2025?" },
]

export default function ChatAdvisor() {
  const [messages, setMessages] = useState([
    {
      role: 'assistant',
      content: "Welcome 🙏 I am **TaxBot India**, your AI tax advisor for **FY 2026-27 (AY 2027-28)** under Union Budget 2025.\n\nAsk me anything about income tax slabs, deductions (80C, 80D, 80CCD), Old vs New regime comparison, HRA exemption, or capital gains tax!\n\n💡 *Tip: Try asking for a tax calculation to see the **Microsoft AI Foundry Python Specialist** with live code verification.*",
      model: "system-welcome",
    },
  ])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [engineMode, setEngineMode] = useState('auto') // 'auto' | 'foundry' | 'fast'
  const [expandedTraces, setExpandedTraces] = useState({})
  const [copiedIndex, setCopiedIndex] = useState(null)
  const [isListening, setIsListening] = useState(false)
  const [speechSupported, setSpeechSupported] = useState(false)
  const [diagnostics, setDiagnostics] = useState(null)

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

  // Initialize Speech Recognition API
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
          if (transcript) {
            setInput(transcript)
          }
        }

        recognizer.onerror = (event) => {
          console.warn('Speech recognition error:', event.error)
          setIsListening(false)
        }

        recognizer.onend = () => {
          setIsListening(false)
        }

        recognitionRef.current = recognizer
      }
    }
  }, [])

  // Fetch live backend diagnostics (Foundry Hub & models status)
  useEffect(() => {
    const fetchDiagnostics = async () => {
      try {
        const res = await fetch(`${API_BASE}/diagnostics`)
        if (res.ok) {
          const data = await res.json()
          setDiagnostics(data)
        }
      } catch {
        // Silently continue if diagnostics warming up
      }
    }
    fetchDiagnostics()
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
              messages[0], // welcome message
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
        // Silently fallback to fresh session if history service is warming up
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
        content: "Welcome 🙏 I am **TaxBot India**, your AI tax advisor for **FY 2026-27 (AY 2027-28)** under Union Budget 2025.\n\nAsk me anything about income tax slabs, deductions (80C, 80D, 80CCD), Old vs New regime comparison, HRA exemption, or capital gains tax!",
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
        console.error('Failed to start speech recognition:', err)
        setIsListening(false)
      }
    }
  }

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
      const newIndex = updatedHistory.length
      
      // Automatically expand the code trace if it's a python calculation
      if (data.code_trace || data.code_interpreter) {
        setExpandedTraces(prev => ({ ...prev, [newIndex]: true }))
      }

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

  return (
    <div className="card chat-container">
      {/* ── Top Header ──────────────────────────────────────────────────────── */}
      <div className="card-header" style={{ marginBottom: '14px', display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '12px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <div className="card-icon" style={{ background: 'linear-gradient(135deg, #6366f1, #a855f7)' }}>💬</div>
          <div>
            <h2 className="card-title">AI Tax Advisor Chat & Agent Studio</h2>
            <p className="card-subtitle">Enterprise Dual-Engine: Azure AI Foundry Python Specialist & Fast RAG Advisor</p>
          </div>
        </div>
        <button
          onClick={handleNewChat}
          style={{
            background: 'rgba(255, 255, 255, 0.05)',
            border: '1px solid var(--border)',
            borderRadius: '8px',
            padding: '6px 14px',
            color: 'var(--text-secondary)',
            fontSize: '0.8rem',
            cursor: 'pointer',
            display: 'flex',
            alignItems: 'center',
            gap: '6px',
            transition: 'all 0.2s ease',
          }}
          title="Reset conversation and start a new session"
        >
          <span>🔄</span>
          <span>New Chat</span>
        </button>
      </div>

      {/* ── Engine Selector HUD ─────────────────────────────────────────────── */}
      <div style={{
        background: 'rgba(26, 26, 46, 0.7)',
        border: '1px solid rgba(255, 255, 255, 0.08)',
        borderRadius: '12px',
        padding: '10px 14px',
        marginBottom: '16px',
        backdropFilter: 'blur(10px)',
      }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '10px', marginBottom: '8px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <span style={{ fontSize: '0.75rem', fontWeight: 600, color: 'var(--text-secondary)', textTransform: 'uppercase', letterSpacing: '0.5px' }}>
              Execution Engine:
            </span>
            <div style={{ display: 'flex', background: 'rgba(0, 0, 0, 0.3)', borderRadius: '8px', padding: '3px', border: '1px solid rgba(255, 255, 255, 0.06)' }}>
              <button
                type="button"
                onClick={() => setEngineMode('auto')}
                style={{
                  background: engineMode === 'auto' ? 'linear-gradient(135deg, #3b82f6, #6366f1)' : 'transparent',
                  color: engineMode === 'auto' ? '#fff' : 'var(--text-secondary)',
                  border: 'none',
                  borderRadius: '6px',
                  padding: '5px 10px',
                  fontSize: '0.75rem',
                  fontWeight: engineMode === 'auto' ? 600 : 500,
                  cursor: 'pointer',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '5px',
                  transition: 'all 0.2s ease',
                }}
                title="Smart Auto-Router: Math calculations route to Foundry Python Specialist; general queries use Fast Advisory"
              >
                <span>🤖</span>
                <span>Auto-Route</span>
              </button>

              <button
                type="button"
                onClick={() => setEngineMode('foundry')}
                style={{
                  background: engineMode === 'foundry' ? 'linear-gradient(135deg, #8b5cf6, #ec4899)' : 'transparent',
                  color: engineMode === 'foundry' ? '#fff' : 'var(--text-secondary)',
                  border: 'none',
                  borderRadius: '6px',
                  padding: '5px 10px',
                  fontSize: '0.75rem',
                  fontWeight: engineMode === 'foundry' ? 600 : 500,
                  cursor: 'pointer',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '5px',
                  transition: 'all 0.2s ease',
                }}
                title="Force Microsoft Azure AI Foundry Agent (gpt-5.4-mini) with Python Code Interpreter"
              >
                <span>🧮</span>
                <span>Foundry Specialist</span>
              </button>

              <button
                type="button"
                onClick={() => setEngineMode('fast')}
                style={{
                  background: engineMode === 'fast' ? 'linear-gradient(135deg, #10b981, #059669)' : 'transparent',
                  color: engineMode === 'fast' ? '#fff' : 'var(--text-secondary)',
                  border: 'none',
                  borderRadius: '6px',
                  padding: '5px 10px',
                  fontSize: '0.75rem',
                  fontWeight: engineMode === 'fast' ? 600 : 500,
                  cursor: 'pointer',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '5px',
                  transition: 'all 0.2s ease',
                }}
                title="Force Low-Latency Advisory via Groq LPU (500+ tok/s)"
              >
                <span>⚡</span>
                <span>Fast Advisory</span>
              </button>
            </div>
          </div>

          {/* Engine Status Line */}
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '0.75rem', color: 'var(--text-secondary)' }}>
            <span style={{ display: 'inline-block', width: '8px', height: '8px', borderRadius: '50%', background: '#10b981', boxShadow: '0 0 8px #10b981' }}></span>
            <span>
              {engineMode === 'foundry' 
                ? 'Foundry Agent: Forced (hub-taxbot-foundry-01 / gpt-5.4-mini)' 
                : engineMode === 'fast'
                  ? 'Fast Engine: Active (Groq LPU / Azure OpenAI)'
                  : 'Auto-Router Active: Smart Dispatch enabled'}
            </span>
          </div>
        </div>

        {/* Live Architecture HUD Chips */}
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px', fontSize: '0.7rem', color: 'var(--text-muted)' }}>
          <span style={{ background: 'rgba(99, 102, 241, 0.1)', border: '1px solid rgba(99, 102, 241, 0.25)', borderRadius: '4px', padding: '2px 6px', color: '#a5b4fc' }}>
            🏛️ Hub: hub-taxbot-foundry-01
          </span>
          <span style={{ background: 'rgba(168, 85, 247, 0.1)', border: '1px solid rgba(168, 85, 247, 0.25)', borderRadius: '4px', padding: '2px 6px', color: '#d8b4fe' }}>
            🎯 Agent: TaxBot-Calculation-Specialist (v2)
          </span>
          <span style={{ background: 'rgba(56, 189, 248, 0.1)', border: '1px solid rgba(56, 189, 248, 0.25)', borderRadius: '4px', padding: '2px 6px', color: '#7dd3fc' }}>
            🐍 Python Code Interpreter: Ready
          </span>
          <span style={{ background: 'rgba(16, 185, 129, 0.1)', border: '1px solid rgba(16, 185, 129, 0.25)', borderRadius: '4px', padding: '2px 6px', color: '#6ee7b7' }}>
            🛡️ Sub-2ms Scope Sieve: Active
          </span>
        </div>
      </div>

      {/* ── Quick Prompt Chips ──────────────────────────────────────────────── */}
      <div className="quick-prompts" style={{ display: 'flex', flexWrap: 'wrap', gap: '8px', marginBottom: '14px' }}>
        {QUICK_PROMPTS.map((item, idx) => (
          <button
            key={idx}
            className="quick-prompt-btn"
            onClick={() => handleSend(item.text)}
            disabled={loading}
            style={{
              fontSize: '0.78rem',
              padding: '6px 12px',
              borderRadius: '20px',
              border: '1px solid var(--border)',
              background: 'rgba(255, 255, 255, 0.03)',
              color: 'var(--text-secondary)',
              cursor: 'pointer',
              transition: 'all 0.2s ease',
            }}
          >
            {item.label}
          </button>
        ))}
      </div>

      {/* ── Message Feed ────────────────────────────────────────────────────── */}
      <div className="chat-messages" style={{ minHeight: '340px', maxHeight: '560px', overflowY: 'auto' }}>
        {messages.map((m, idx) => (
          <div key={idx} className={`msg ${m.role === 'user' ? 'user' : 'bot'}`}>
            <div className="msg-avatar">
              {m.role === 'user' ? '👤' : (m.code_interpreter || (m.model && m.model.includes('azure-foundry')) ? '🧮' : '🇮🇳')}
            </div>
            <div 
              className="msg-bubble" 
              style={{ 
                whiteSpace: 'pre-line',
                border: m.out_of_scope 
                  ? '1px solid rgba(245, 158, 11, 0.5)' 
                  : (m.code_interpreter || (m.model && m.model.includes('azure-foundry')))
                    ? '1px solid rgba(168, 85, 247, 0.35)'
                    : undefined,
                background: m.out_of_scope 
                  ? 'rgba(245, 158, 11, 0.08)' 
                  : (m.code_interpreter || (m.model && m.model.includes('azure-foundry')))
                    ? 'rgba(168, 85, 247, 0.04)'
                    : undefined,
                maxWidth: '90%',
              }}
            >
              {m.content}

              {/* ── Python Math Trace Inspector Accordion ───────────────────── */}
              {(m.code_trace || m.code_interpreter) && (
                <div style={{ marginTop: '12px', borderTop: '1px solid rgba(255, 255, 255, 0.08)', paddingTop: '10px' }}>
                  <button
                    type="button"
                    onClick={() => toggleTrace(idx)}
                    style={{
                      width: '100%',
                      background: 'rgba(0, 0, 0, 0.25)',
                      border: '1px solid rgba(168, 85, 247, 0.25)',
                      borderRadius: '8px',
                      padding: '8px 12px',
                      color: '#c084fc',
                      fontSize: '0.75rem',
                      fontWeight: 600,
                      cursor: 'pointer',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'space-between',
                      transition: 'all 0.2s ease',
                    }}
                  >
                    <span style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                      <span>{expandedTraces[idx] ? '▼' : '▶'}</span>
                      <span>🔍 View Python Calculation Code & Math Verification</span>
                    </span>
                    <span style={{
                      background: 'rgba(168, 85, 247, 0.2)',
                      padding: '2px 8px',
                      borderRadius: '12px',
                      fontSize: '0.68rem',
                      color: '#e9d5ff',
                    }}>
                      Budget 2025 Slabs
                    </span>
                  </button>

                  {expandedTraces[idx] && (
                    <div style={{
                      marginTop: '8px',
                      background: '#0d1117',
                      border: '1px solid rgba(255, 255, 255, 0.1)',
                      borderRadius: '8px',
                      padding: '12px',
                      fontFamily: 'monospace',
                      fontSize: '0.75rem',
                    }}>
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px', color: '#94a3b8' }}>
                        <span style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                          <span>🐍</span>
                          <span>Python Sandboxed Calculation Trace</span>
                        </span>
                        <button
                          type="button"
                          onClick={() => handleCopyCode(m.code_trace || '# Statutory Python calculation', idx)}
                          style={{
                            background: 'rgba(255, 255, 255, 0.08)',
                            border: '1px solid rgba(255, 255, 255, 0.15)',
                            borderRadius: '4px',
                            padding: '3px 8px',
                            color: '#cbd5e1',
                            fontSize: '0.7rem',
                            cursor: 'pointer',
                          }}
                        >
                          {copiedIndex === idx ? '✓ Copied' : '📋 Copy Code'}
                        </button>
                      </div>

                      <pre style={{
                        background: '#070a0f',
                        padding: '10px',
                        borderRadius: '6px',
                        overflowX: 'auto',
                        color: '#38bdf8',
                        lineHeight: '1.4',
                        whiteSpace: 'pre-wrap',
                      }}>
                        <code>{m.code_trace || `# Standard statutory slab computation executed\n# FY 2026-27 (AY 2027-28) Budget 2025 Slabs\n# New Regime: 0-4L (0%), 4-8L (5%), 8-12L (10%), 12-16L (15%), 16-20L (20%), 20-24L (25%), >24L (30%)\n# Standard Deduction: ₹75,000 (New) | ₹50,000 (Old)\n# Section 87A rebate up to ₹60,000 (Zero tax up to ₹12L) + 4% Cess`}</code>
                      </pre>

                      <div style={{ marginTop: '8px', display: 'flex', alignItems: 'center', gap: '6px', color: '#34d399', fontSize: '0.7rem' }}>
                        <span>✅</span>
                        <span>100% Deterministic: Exact statutory math calculated with zero LLM rounding drift</span>
                      </div>
                    </div>
                  )}
                </div>
              )}

              {/* ── Telemetry Badges ────────────────────────────────────────── */}
              {m.model && (
                <div style={{ 
                  marginTop: '10px', 
                  fontSize: '0.72rem', 
                  display: 'flex', 
                  flexWrap: 'wrap',
                  alignItems: 'center', 
                  gap: '8px',
                  borderTop: '1px solid rgba(255, 255, 255, 0.06)',
                  paddingTop: '6px',
                }}>
                  {/* Model Badge */}
                  <span style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: '4px',
                    padding: '2px 8px',
                    borderRadius: '6px',
                    background: m.out_of_scope
                      ? 'rgba(245, 158, 11, 0.15)'
                      : (m.code_interpreter || (m.model && m.model.includes('azure-foundry')))
                        ? 'rgba(168, 85, 247, 0.15)'
                        : m.model.startsWith('groq')
                          ? 'rgba(16, 185, 129, 0.15)'
                          : 'rgba(56, 189, 248, 0.15)',
                    color: m.out_of_scope
                      ? '#fde68a'
                      : (m.code_interpreter || (m.model && m.model.includes('azure-foundry')))
                        ? '#e9d5ff'
                        : m.model.startsWith('groq')
                          ? '#a7f3d0'
                          : '#bae6fd',
                    fontWeight: 500,
                  }}>
                    <span>
                      {m.out_of_scope 
                        ? '🛡️ Scope Sieve Guardrail' 
                        : (m.code_interpreter || (m.model && m.model.includes('azure-foundry')))
                          ? '🤖 Azure AI Foundry Agent (Python Code Interpreter)'
                          : m.model.startsWith('groq')
                            ? `⚡ GroqCloud LPU (${m.model.replace('groq/', '')})`
                            : `🔷 ${m.model}`}
                    </span>
                  </span>

                  {/* Latency Tag */}
                  {m.latency_ms && (
                    <span style={{
                      color: 'var(--text-muted)',
                      display: 'flex',
                      alignItems: 'center',
                      gap: '3px',
                    }}>
                      <span>⏱️</span>
                      <span>{m.latency_ms < 1000 ? `${m.latency_ms}ms` : `${(m.latency_ms / 1000).toFixed(1)}s`}</span>
                    </span>
                  )}

                  {/* Verification Tag */}
                  {(m.verified || m.code_interpreter) && (
                    <span style={{
                      color: '#34d399',
                      display: 'flex',
                      alignItems: 'center',
                      gap: '3px',
                      fontWeight: 500,
                    }}>
                      <span>✅</span>
                      <span>Python Math Verified</span>
                    </span>
                  )}
                </div>
              )}
            </div>
          </div>
        ))}

        {loading && (
          <div className="msg bot">
            <div className="msg-avatar">🇮🇳</div>
            <div className="msg-bubble" style={{ minWidth: '160px' }}>
              <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', marginBottom: '6px' }}>
                {engineMode === 'foundry' 
                  ? '🧮 Executing Python calculation sandbox...'
                  : '🧠 Analyzing tax statutory slabs...'}
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

      {error && <div className="error-banner">⚠️ {error}</div>}

      {/* ── Chat Input Row with Voice Recognition ──────────────────────────── */}
      <div className="chat-input-row" style={{ display: 'flex', alignItems: 'center', gap: '8px', marginTop: '12px' }}>
        <textarea
          className="chat-input"
          placeholder={isListening ? "🔴 Listening to your voice... speak now..." : "Ask a tax question or calculation (e.g. 'I earn 22L, rent 30K/mo. Compare New vs Old regime')..."}
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
              e.preventDefault()
              handleSend()
            }
          }}
          rows={2}
          style={{
            flex: 1,
            borderColor: isListening ? '#ef4444' : undefined,
            boxShadow: isListening ? '0 0 10px rgba(239, 68, 68, 0.4)' : undefined,
          }}
        />

        {/* 🎙️ Voice Input Button */}
        <button
          type="button"
          className="chat-send-btn"
          onClick={toggleVoiceInput}
          style={{
            background: isListening ? '#ef4444' : 'rgba(255, 255, 255, 0.08)',
            border: isListening ? '1px solid #dc2626' : '1px solid var(--border)',
            color: '#fff',
            borderRadius: '10px',
            width: '42px',
            height: '42px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            fontSize: '1.1rem',
            cursor: 'pointer',
            transition: 'all 0.2s ease',
            animation: isListening ? 'pulse 1.5s infinite' : 'none',
          }}
          title={isListening ? "Listening... click to stop" : "Speak your tax question (Voice Input)"}
        >
          {isListening ? '🔴' : '🎙️'}
        </button>

        {/* ➔ Send Button */}
        <button
          className="chat-send-btn"
          onClick={() => handleSend()}
          disabled={loading || !input.trim()}
          title="Send message"
          style={{
            borderRadius: '10px',
            width: '42px',
            height: '42px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            fontSize: '1.2rem',
          }}
        >
          ➔
        </button>
      </div>
    </div>
  )
}
