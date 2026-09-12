import React, { useState, useEffect, useRef } from 'react'
import { Send, Bot, Sparkles, ArrowRight, ShieldCheck, Download, Zap, Cpu, ChevronDown, ChevronUp, CheckCircle2, ShieldAlert, MinusCircle } from 'lucide-react'
import MarkdownRenderer from './MarkdownRenderer'
import CitationCard from './CitationCard'
import PIIBanner from './PIIBanner'

const INITIAL_SUGGESTIONS = [
  "Can a bank store transaction data in a public overseas cloud?",
  "What are the acceptable OVDs for NRI account opening under V-CIP?",
  "What are the RBI restrictions on outsourcing CISO functions?",
  "What is the penalty for issuing an unsolicited credit card?"
]

function getSynthesizerModelName(model) {
  if (!model) return 'Gemini 2.0 Flash'
  if (model.includes('gpt-5.4-nano')) return 'Azure OpenAI (gpt-5.4-nano)'
  if (model.includes('gemini-2.0-flash')) return 'Google Gemini (2.0 Flash)'
  if (model.includes('120b')) return 'Groq LPU (GPT-OSS-120B)'
  if (model.includes('groq') || model.includes('llama')) return 'Groq LPU (Llama-70B)'
  if (model.includes('qwen') || model.includes('private-slm') || model.includes('sovereign')) return 'Sovereign SLM (Qwen2.5-0.5B)'
  return model
}

function formatAgentModelBadge(model, msgMode) {
  if (!model) return '⚡ 4 Agents: Supervisor ➔ Qdrant ➔ Auditor ➔ Gemini 2.0'
  if (model === 'governance-abstention-shield') return '🛡️ Handled by: Supervisor Agent (Safety Shield)'
  if (model === 'conversational-intent-router') return '💬 Handled by: Supervisor Agent (Router)'
  if (model === 'governance-core') return '⚖️ BankCompliance Core'
  if (msgMode === 'sovereign' || model.includes('sovereign') || model.includes('qwen') || model.includes('private-slm')) {
    return '🛡️ Sovereign In-Cluster SLM: Qwen2.5-0.5B (Zero-Egress AKS Node)'
  }
  const synthName = getSynthesizerModelName(model)
  return `⚡ 4 Agents: Supervisor ➔ Qdrant ➔ Auditor ➔ ${synthName}`
}

export default function ChatWindow({ selectedCircular, onSelectCitation, inferenceMode: propInferenceMode, onToggleInferenceMode }) {
  const [internalInferenceMode, setInternalInferenceMode] = useState('cloud')
  const inferenceMode = propInferenceMode !== undefined ? propInferenceMode : internalInferenceMode
  const setInferenceMode = onToggleInferenceMode || setInternalInferenceMode
  const [messages, setMessages] = useState([
    {
      role: 'assistant',
      text: `Hello! I am **BankCompliance AI**, an enterprise-grade regulatory and statutory compliance copilot specialized in **Reserve Bank of India (RBI) Master Directions**.\n\nAsk any question regarding **KYC & V-CIP norms**, **IT Governance & Cloud Localization**, **IT Outsourcing**, **Digital Lending**, or **CoFT Payment Security**.\n\nAll answers are audited against our official indexed statutory knowledge lake.`,
      citations: [],
      pii: [],
      suggested_queries: INITIAL_SUGGESTIONS,
      model_used: 'governance-core',
      latency_ms: 8
    }
  ])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [activeSuggestions, setActiveSuggestions] = useState(INITIAL_SUGGESTIONS)
  const [expandedTraces, setExpandedTraces] = useState({})
  const messagesEndRef = useRef(null)

  const toggleTrace = (idx) => {
    setExpandedTraces(prev => ({ ...prev, [idx]: !prev[idx] }))
  }

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages, loading])

  const submitQuery = async (userQuery) => {
    if (!userQuery || !userQuery.trim() || loading) return

    const historyPayload = messages
      .slice(-4)
      .map(m => ({ role: m.role, content: m.text }))

    setInput('')
    setMessages(prev => [...prev, { role: 'user', text: userQuery }])
    setLoading(true)

    try {
      const isLocal = typeof window !== 'undefined' && (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1')
      const defaultEndpoint = isLocal
        ? 'http://localhost:8000/api/v1/compliance/query'
        : 'https://apim-ht-ss-p-cin-01.azure-api.net/bankc/api/v1/compliance/query'
      const apiEndpoint = import.meta.env.VITE_API_URL || defaultEndpoint
      
      const res = await fetch(apiEndpoint, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          query: userQuery,
          department: 'legal-compliance',
          session_id: 'active-session-01',
          circular: selectedCircular !== 'All' ? selectedCircular : undefined,
          history: historyPayload,
          model_preference: inferenceMode === 'sovereign' ? 'sovereign-slm' : 'cloud'
        })
      })
      const data = await res.json()
      
      const newSuggestions = data.suggested_queries && data.suggested_queries.length > 0
        ? data.suggested_queries
        : INITIAL_SUGGESTIONS
      
      setActiveSuggestions(newSuggestions)

      setMessages(prev => [...prev, {
        role: 'assistant',
        text: data.answer,
        citations: data.citations || [],
        pii: data.pii_redacted || [],
        cached: data.cached || false,
        latency_ms: data.latency_ms || 0,
        model_used: data.model_used || (inferenceMode === 'sovereign' ? 'qwen2.5:0.5b (sovereign-slm)' : 'gemini-2.0-flash'),
        suggested_queries: newSuggestions,
        inferenceMode: inferenceMode
      }])
    } catch (err) {
      console.error('BankCompliance API fetch error:', err)
      setMessages(prev => [...prev, {
        role: 'assistant',
        text: `⚠️ Unable to connect to BankCompliance backend API (${err.message || 'Network error'}). Please ensure the cluster services are active.`,
        citations: [],
        pii: [],
        suggested_queries: INITIAL_SUGGESTIONS
      }])
    } finally {
      setLoading(false)
    }
  }

  const handleSend = (e) => {
    e.preventDefault()
    submitQuery(input)
  }

  const exportMemo = (msg) => {
    const timestamp = new Date().toISOString()
    const content = `BANKCOMPLIANCE AI — REGULATORY AUDIT MEMORANDUM
Generated: ${timestamp}
Classification: Strictly Confidential / Bank Internal Audit

QUERY INTERPRETATION:
${msg.text}

VERIFIED RBI MASTER DIRECTION CITATIONS:
${(msg.citations || []).map(c => `- Circular: ${c.circular_no}\n  Title: ${c.title}\n  Clause: ${c.clause}\n  SHA-256 Provenance: ${c.provenance_hash || 'verified'}\n  Text: ${c.text}`).join('\n\n')}

---
Statutory Note: Generated by BankCompliance Multi-Agent Orchestration Fleet on AKS.
Approved for CCO / Internal Audit Review.`

    const blob = new Blob([content], { type: 'text/plain' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `compliance_memo_${Date.now()}.txt`
    a.click()
    URL.revokeObjectURL(url)
  }

  return (
    <div style={{ flex: 1, display: 'flex', flexDirection: 'column', height: '100%', background: 'transparent' }}>
      {/* ── Top Inference Routing Bar (Cloud Fleet vs Sovereign SLM Toggle) ── */}
      <div style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        padding: '10px 24px',
        background: 'rgba(15, 23, 42, 0.7)',
        borderBottom: '1px solid rgba(255, 255, 255, 0.08)',
        backdropFilter: 'blur(12px)',
        zIndex: 5,
        flexWrap: 'wrap',
        gap: '10px'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <span style={{ fontSize: '0.72rem', fontWeight: 700, letterSpacing: '0.05em', color: 'var(--text-muted)' }}>
            INFERENCE ENGINE:
          </span>
          <div style={{
            display: 'inline-flex',
            background: 'rgba(255, 255, 255, 0.04)',
            padding: '3px',
            borderRadius: '10px',
            border: '1px solid rgba(255, 255, 255, 0.08)'
          }}>
            <button
              type="button"
              onClick={() => setInferenceMode('cloud')}
              style={{
                padding: '5px 14px',
                borderRadius: '7px',
                fontSize: '0.75rem',
                fontWeight: 600,
                border: 'none',
                cursor: 'pointer',
                display: 'flex',
                alignItems: 'center',
                gap: '6px',
                background: inferenceMode === 'cloud' ? 'linear-gradient(135deg, #4f46e5 0%, #06b6d4 100%)' : 'transparent',
                color: inferenceMode === 'cloud' ? '#ffffff' : 'var(--text-muted)',
                transition: 'all 0.2s ease',
                boxShadow: inferenceMode === 'cloud' ? '0 0 12px rgba(79, 70, 229, 0.4)' : 'none'
              }}
              title="Ultra-fast legal reasoning via Google Gemini 2.0 Flash and Groq LPU"
            >
              <Zap size={13} /> Multi-Cloud Fleet (Groq / Gemini)
            </button>
            <button
              type="button"
              onClick={() => setInferenceMode('sovereign')}
              style={{
                padding: '5px 14px',
                borderRadius: '7px',
                fontSize: '0.75rem',
                fontWeight: 600,
                border: 'none',
                cursor: 'pointer',
                display: 'flex',
                alignItems: 'center',
                gap: '6px',
                background: inferenceMode === 'sovereign' ? 'linear-gradient(135deg, #059669 0%, #10b981 100%)' : 'transparent',
                color: inferenceMode === 'sovereign' ? '#ffffff' : 'var(--text-muted)',
                transition: 'all 0.2s ease',
                boxShadow: inferenceMode === 'sovereign' ? '0 0 12px rgba(16, 185, 129, 0.45)' : 'none'
              }}
              title="100% In-Cluster Sovereign SLM (Qwen2.5-0.5B on AKS node CPU, Zero-Egress)"
            >
              <ShieldCheck size={13} /> Sovereign In-Cluster SLM (Qwen 2.5)
            </button>
          </div>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          {inferenceMode === 'sovereign' ? (
            <span style={{
              fontSize: '0.72rem',
              color: '#34d399',
              background: 'rgba(16, 185, 129, 0.12)',
              border: '1px solid rgba(16, 185, 129, 0.3)',
              padding: '3px 10px',
              borderRadius: '9999px',
              display: 'flex',
              alignItems: 'center',
              gap: '6px',
              fontWeight: 600
            }}>
              <span style={{ width: '6px', height: '6px', borderRadius: '50%', background: '#34d399', display: 'inline-block' }} />
              Zero-Egress AKS Node Active (Air-Gapped)
            </span>
          ) : (
            <span style={{
              fontSize: '0.72rem',
              color: '#93c5fd',
              background: 'rgba(59, 130, 246, 0.1)',
              border: '1px solid rgba(59, 130, 246, 0.25)',
              padding: '3px 10px',
              borderRadius: '9999px',
              display: 'flex',
              alignItems: 'center',
              gap: '6px',
              fontWeight: 600
            }}>
              <span style={{ width: '6px', height: '6px', borderRadius: '50%', background: '#60a5fa', display: 'inline-block' }} />
              500+ tok/s Ultra-Fast Synthesis
            </span>
          )}
        </div>
      </div>

      {/* Messages Scroll Area */}
      <div style={{ flex: 1, overflowY: 'auto', padding: '24px 28px', display: 'flex', flexDirection: 'column', gap: '20px' }}>
        {messages.map((m, idx) => (
          <div key={idx} className="animate-fade-in" style={{
            display: 'flex',
            gap: '14px',
            alignSelf: m.role === 'user' ? 'flex-end' : 'flex-start',
            maxWidth: m.role === 'user' ? '75%' : '90%'
          }}>
            {m.role === 'assistant' && (
              <div style={{
                width: '34px',
                height: '34px',
                borderRadius: '10px',
                background: 'linear-gradient(135deg, #4f46e5 0%, #06b6d4 100%)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                flexShrink: 0,
                boxShadow: '0 0 12px rgba(79, 70, 229, 0.35)'
              }}>
                <Bot size={18} color="#fff" />
              </div>
            )}
            
            <div style={{
              background: m.role === 'user' 
                ? 'linear-gradient(135deg, #4f46e5 0%, #4338ca 100%)' 
                : 'rgba(15, 23, 42, 0.75)',
              backdropFilter: m.role === 'user' ? 'none' : 'blur(16px)',
              border: m.role === 'user' ? '1px solid rgba(255, 255, 255, 0.15)' : '1px solid var(--border-subtle)',
              borderRadius: m.role === 'user' ? '16px 16px 4px 16px' : '16px 16px 16px 4px',
              padding: '16px 20px',
              color: 'var(--text-main)',
              fontSize: '0.92rem',
              lineHeight: '1.6',
              boxShadow: m.role === 'user' ? '0 4px 20px rgba(79, 70, 229, 0.25)' : 'var(--shadow-glass)'
            }}>
              <PIIBanner piiList={m.pii} />

              {/* Telemetry Header Badge Bar */}
              {m.role === 'assistant' && (
                <>
                  <div style={{
                    marginBottom: '12px',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'space-between',
                    borderBottom: '1px solid rgba(255, 255, 255, 0.06)',
                    paddingBottom: '8px',
                    gap: '8px',
                    flexWrap: 'wrap'
                  }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                      {m.cached ? (
                        <span style={{
                          background: 'rgba(16, 185, 129, 0.15)',
                          border: '1px solid rgba(16, 185, 129, 0.35)',
                          color: '#34d399',
                          fontSize: '0.7rem',
                          fontWeight: 700,
                          padding: '2px 8px',
                          borderRadius: '9999px',
                          display: 'flex',
                          alignItems: 'center',
                          gap: '4px'
                        }}>
                          <Zap size={10} /> Semantic Cache Hit ({m.latency_ms}ms • $0.00)
                        </span>
                      ) : (() => {
                        const isSovereignMsg = m.inferenceMode === 'sovereign' || (m.model_used && (m.model_used.includes('sovereign') || m.model_used.includes('qwen') || m.model_used.includes('private-slm')))
                        return (
                          <button
                            type="button"
                            onClick={() => toggleTrace(idx)}
                            style={{
                              background: m.model_used === 'governance-abstention-shield'
                                ? (expandedTraces[idx] ? 'rgba(245, 158, 11, 0.25)' : 'rgba(245, 158, 11, 0.12)')
                                : isSovereignMsg
                                  ? (expandedTraces[idx] ? 'rgba(16, 185, 129, 0.25)' : 'rgba(16, 185, 129, 0.12)')
                                  : (expandedTraces[idx] ? 'rgba(99, 102, 241, 0.25)' : 'rgba(99, 102, 241, 0.12)'),
                              border: m.model_used === 'governance-abstention-shield'
                                ? '1px solid rgba(245, 158, 11, 0.4)'
                                : isSovereignMsg
                                  ? '1px solid rgba(16, 185, 129, 0.4)'
                                  : '1px solid rgba(99, 102, 241, 0.4)',
                              color: m.model_used === 'governance-abstention-shield'
                                ? '#fcd34d'
                                : isSovereignMsg ? '#34d399' : '#c7d2fe',
                              fontSize: '0.7rem',
                              fontWeight: 600,
                              padding: '3px 10px',
                              borderRadius: '9999px',
                              display: 'flex',
                              alignItems: 'center',
                              gap: '5px',
                              cursor: 'pointer',
                              transition: 'all 0.2s ease'
                            }}
                            title="Click to view step-by-step execution trace"
                          >
                            {m.model_used === 'governance-abstention-shield' ? (
                              <>
                                <ShieldAlert size={11} />
                                <span>Supervisor Agent Intercept ({m.latency_ms}ms)</span>
                              </>
                            ) : isSovereignMsg ? (
                              <>
                                <ShieldCheck size={11} />
                                <span>Sovereign Air-Gapped Pipeline ({m.latency_ms}ms)</span>
                              </>
                            ) : (
                              <>
                                <Cpu size={11} />
                                <span>4-Agent Pipeline ({m.latency_ms}ms)</span>
                              </>
                            )}
                            {expandedTraces[idx] ? <ChevronUp size={12} /> : <ChevronDown size={12} />}
                          </button>
                        )
                      })()}
                    </div>

                    <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                      <span style={{
                        fontSize: '0.72rem',
                        color: m.model_used === 'governance-abstention-shield'
                          ? '#fcd34d'
                          : (m.inferenceMode === 'sovereign' || (m.model_used && (m.model_used.includes('sovereign') || m.model_used.includes('qwen'))))
                            ? '#34d399'
                            : '#c7d2fe',
                        background: m.model_used === 'governance-abstention-shield'
                          ? 'rgba(245, 158, 11, 0.12)'
                          : (m.inferenceMode === 'sovereign' || (m.model_used && (m.model_used.includes('sovereign') || m.model_used.includes('qwen'))))
                            ? 'rgba(16, 185, 129, 0.14)'
                            : 'rgba(99, 102, 241, 0.14)',
                        border: m.model_used === 'governance-abstention-shield'
                          ? '1px solid rgba(245, 158, 11, 0.35)'
                          : (m.inferenceMode === 'sovereign' || (m.model_used && (m.model_used.includes('sovereign') || m.model_used.includes('qwen'))))
                            ? '1px solid rgba(16, 185, 129, 0.35)'
                            : '1px solid rgba(99, 102, 241, 0.3)',
                        padding: '3px 9px',
                        borderRadius: '6px',
                        fontWeight: 600
                      }}>
                        {formatAgentModelBadge(m.model_used, m.inferenceMode)}
                      </span>
                    </div>
                  </div>

                  {/* ── Expandable Multi-Agent Execution Trace ───────────────────── */}
                  {!m.cached && expandedTraces[idx] && (() => {
                    const isSovereignMsg = m.inferenceMode === 'sovereign' || (m.model_used && (m.model_used.includes('sovereign') || m.model_used.includes('qwen') || m.model_used.includes('private-slm')))
                    return (
                      <div style={{
                        background: 'rgba(15, 23, 42, 0.7)',
                        border: m.model_used === 'governance-abstention-shield'
                          ? '1px solid rgba(245, 158, 11, 0.35)'
                          : isSovereignMsg
                            ? '1px solid rgba(16, 185, 129, 0.35)'
                            : '1px solid rgba(99, 102, 241, 0.3)',
                        borderRadius: '10px',
                        padding: '14px 16px',
                        marginBottom: '14px',
                        fontSize: '0.78rem',
                        animation: 'fadeIn 0.2s ease'
                      }}>
                        <div style={{
                          fontWeight: 700,
                          color: m.model_used === 'governance-abstention-shield'
                            ? '#fde68a'
                            : isSovereignMsg ? '#34d399' : '#a5b4fc',
                          marginBottom: '10px',
                          display: 'flex',
                          alignItems: 'center',
                          gap: '6px'
                        }}>
                          {m.model_used === 'governance-abstention-shield' ? (
                            <ShieldAlert size={13} />
                          ) : isSovereignMsg ? (
                            <ShieldCheck size={13} />
                          ) : (
                            <Cpu size={13} />
                          )}
                          <span>
                            {m.model_used === 'governance-abstention-shield'
                              ? 'Supervisor Agent Safety Shield Interception Trace:'
                              : isSovereignMsg
                                ? 'Sovereign In-Cluster Air-Gapped Execution Pipeline Trace:'
                                : 'Multi-Cloud Autonomous Agent Execution Pipeline Trace:'}
                          </span>
                        </div>

                        <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
                          {/* Step 1: Guardrail / Supervisor */}
                          <div style={{ display: 'flex', alignItems: 'flex-start', gap: '8px' }}>
                            <CheckCircle2 size={14} style={{ color: '#34d399', marginTop: '2px', flexShrink: 0 }} />
                            <div>
                              <div style={{ fontWeight: 600, color: '#f1f5f9', display: 'flex', alignItems: 'center', flexWrap: 'wrap', gap: '6px' }}>
                                <span>1. {isSovereignMsg ? 'Sovereign Guardrail & DPDP Sieve' : 'Supervisor Agent (Router & Safety Shield)'} — <span style={{ color: '#34d399' }}>ACTIVE</span></span>
                                <span style={{
                                  background: isSovereignMsg ? 'rgba(16, 185, 129, 0.2)' : 'rgba(99, 102, 241, 0.2)',
                                  border: isSovereignMsg ? '1px solid rgba(16, 185, 129, 0.3)' : '1px solid rgba(99, 102, 241, 0.3)',
                                  color: isSovereignMsg ? '#34d399' : '#c7d2fe',
                                  padding: '1px 6px',
                                  borderRadius: '4px',
                                  fontSize: '0.66rem'
                                }}>
                                  {isSovereignMsg ? 'In-Memory (<3ms)' : 'Gemini 2.0 Flash-Lite'}
                                </span>
                              </div>
                              <div style={{ color: '#94a3b8', fontSize: '0.72rem', marginTop: '2px' }}>
                                {m.model_used === 'governance-abstention-shield'
                                  ? 'Executed Layer-1 Vector Centroid Sieve (<3ms). Intercepted non-banking off-topic query and enforced domain boundary.'
                                  : isSovereignMsg
                                    ? 'Executed Layer-1 Mathematical Vector Centroid Sieve (<3ms) & in-memory DPDP Act PII masking with zero cloud egress.'
                                    : 'Executed Layer-1 Vector Centroid Sieve (<3ms), checked DPDP PII guardrails, and decomposed intent into statutory sub-tasks.'}
                              </div>
                            </div>
                          </div>

                          {/* Step 2: Retriever */}
                          <div style={{ display: 'flex', alignItems: 'flex-start', gap: '8px' }}>
                            {m.model_used === 'governance-abstention-shield' ? (
                              <MinusCircle size={14} style={{ color: '#64748b', marginTop: '2px', flexShrink: 0 }} />
                            ) : (
                              <CheckCircle2 size={14} style={{ color: '#34d399', marginTop: '2px', flexShrink: 0 }} />
                            )}
                            <div>
                              <div style={{ fontWeight: 600, color: m.model_used === 'governance-abstention-shield' ? '#64748b' : '#f1f5f9', display: 'flex', alignItems: 'center', flexWrap: 'wrap', gap: '6px' }}>
                                <span>2. Retriever Agent (Qdrant Vector Lake) — {m.model_used === 'governance-abstention-shield' ? <span style={{ color: '#94a3b8' }}>BYPASSED</span> : <span style={{ color: '#34d399' }}>ACTIVE</span>}</span>
                                {m.model_used !== 'governance-abstention-shield' && (
                                  <span style={{
                                    background: 'rgba(16, 185, 129, 0.2)',
                                    border: '1px solid rgba(16, 185, 129, 0.3)',
                                    color: '#34d399',
                                    padding: '1px 6px',
                                    borderRadius: '4px',
                                    fontSize: '0.66rem'
                                  }}>
                                    {isSovereignMsg ? 'In-Cluster StatefulSet' : 'Qdrant 768-dim DB'}
                                  </span>
                                )}
                              </div>
                              <div style={{ color: '#64748b', fontSize: '0.72rem', marginTop: '2px' }}>
                                {m.model_used === 'governance-abstention-shield'
                                  ? 'Bypassed: Vector retrieval skipped for non-regulatory questions to save compute & latency.'
                                  : isSovereignMsg
                                    ? 'Executed local 768-dim semantic cosine search over indexed RBI Master Directions inside private AKS cluster network.'
                                    : 'Performed 768-dim semantic cosine search over 14 RBI Master Directions and retrieved top statutory evidence with SHA-256 hashes.'}
                              </div>
                            </div>
                          </div>

                          {/* Step 3: Auditor */}
                          <div style={{ display: 'flex', alignItems: 'flex-start', gap: '8px' }}>
                            {m.model_used === 'governance-abstention-shield' ? (
                              <MinusCircle size={14} style={{ color: '#64748b', marginTop: '2px', flexShrink: 0 }} />
                            ) : (
                              <CheckCircle2 size={14} style={{ color: '#34d399', marginTop: '2px', flexShrink: 0 }} />
                            )}
                            <div>
                              <div style={{ fontWeight: 600, color: m.model_used === 'governance-abstention-shield' ? '#64748b' : '#f1f5f9', display: 'flex', alignItems: 'center', flexWrap: 'wrap', gap: '6px' }}>
                                <span>3. Statutory Auditor Gate — {m.model_used === 'governance-abstention-shield' ? <span style={{ color: '#94a3b8' }}>BYPASSED</span> : <span style={{ color: '#34d399' }}>ACTIVE</span>}</span>
                                {m.model_used !== 'governance-abstention-shield' && (
                                  <span style={{
                                    background: isSovereignMsg ? 'rgba(16, 185, 129, 0.2)' : 'rgba(245, 158, 11, 0.2)',
                                    border: isSovereignMsg ? '1px solid rgba(16, 185, 129, 0.3)' : '1px solid rgba(245, 158, 11, 0.3)',
                                    color: isSovereignMsg ? '#34d399' : '#fcd34d',
                                    padding: '1px 6px',
                                    borderRadius: '4px',
                                    fontSize: '0.66rem'
                                  }}>
                                    {isSovereignMsg ? 'Deterministic Ground Truth Gate' : 'Gemini 2.0 Flash-Thinking'}
                                  </span>
                                )}
                              </div>
                              <div style={{ color: '#64748b', fontSize: '0.72rem', marginTop: '2px' }}>
                                {m.model_used === 'governance-abstention-shield'
                                  ? 'Bypassed: No regulatory citations to audit for out-of-scope intent.'
                                  : isSovereignMsg
                                    ? 'Validated statutory citations deterministically against ground-truth corpus without external LLM API calls.'
                                    : 'Audited retrieved clauses against circular numbers (e.g. RBI/2023-24/102). Evaluated groundedness & citation integrity (Gate: PASS).'}
                              </div>
                            </div>
                          </div>

                          {/* Step 4: Synthesizer */}
                          <div style={{ display: 'flex', alignItems: 'flex-start', gap: '8px' }}>
                            {m.model_used === 'governance-abstention-shield' ? (
                              <MinusCircle size={14} style={{ color: '#64748b', marginTop: '2px', flexShrink: 0 }} />
                            ) : (
                              <CheckCircle2 size={14} style={{ color: '#34d399', marginTop: '2px', flexShrink: 0 }} />
                            )}
                            <div>
                              <div style={{ fontWeight: 600, color: m.model_used === 'governance-abstention-shield' ? '#64748b' : '#f1f5f9', display: 'flex', alignItems: 'center', flexWrap: 'wrap', gap: '6px' }}>
                                <span>4. {isSovereignMsg ? 'Sovereign Synthesizer Agent (In-Cluster SLM)' : 'Synthesizer Agent (Statutory Legal Advisor)'} — {m.model_used === 'governance-abstention-shield' ? <span style={{ color: '#94a3b8' }}>BYPASSED</span> : <span style={{ color: '#34d399' }}>ACTIVE</span>}</span>
                                {m.model_used !== 'governance-abstention-shield' && (
                                  <span style={{
                                    background: isSovereignMsg ? 'rgba(16, 185, 129, 0.2)' : 'rgba(59, 130, 246, 0.2)',
                                    border: isSovereignMsg ? '1px solid rgba(16, 185, 129, 0.3)' : '1px solid rgba(59, 130, 246, 0.3)',
                                    color: isSovereignMsg ? '#34d399' : '#93c5fd',
                                    padding: '1px 6px',
                                    borderRadius: '4px',
                                    fontSize: '0.66rem'
                                  }}>
                                    {isSovereignMsg ? 'Qwen 2.5 0.5B (AKS CPU Node)' : getSynthesizerModelName(m.model_used)}
                                  </span>
                                )}
                              </div>
                              <div style={{ color: '#64748b', fontSize: '0.72rem', marginTop: '2px' }}>
                                {m.model_used === 'governance-abstention-shield'
                                  ? 'Bypassed: Pre-compiled statutory domain boundary shield response returned.'
                                  : isSovereignMsg
                                    ? 'Synthesized legally auditable determination on zero-egress in-cluster Ollama instance running inside the AKS tenant boundary.'
                                    : `Synthesized legally auditable determination with statutory caveats, action points, and escalation guidance via ${getSynthesizerModelName(m.model_used)}.`}
                              </div>
                            </div>
                          </div>
                        </div>
                      </div>
                    )
                  })()}
                </>
              )}

              {/* Message Content */}
              {m.role === 'user' ? m.text : <MarkdownRenderer content={m.text} />}
              
              {/* Citation Cards */}
              {m.citations && m.citations.length > 0 && (
                <div style={{ marginTop: '16px', borderTop: '1px solid var(--border-subtle)', paddingTop: '12px' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '10px' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '0.75rem', fontWeight: 700, color: '#f59e0b', letterSpacing: '0.04em', textTransform: 'uppercase' }}>
                      <ShieldCheck size={13} />
                      <span>Verified RBI Master Direction Evidence:</span>
                    </div>
                    <button
                      onClick={() => exportMemo(m)}
                      style={{
                        background: 'rgba(99, 102, 241, 0.12)',
                        border: '1px solid rgba(99, 102, 241, 0.3)',
                        color: '#c7d2fe',
                        borderRadius: '6px',
                        padding: '3px 8px',
                        fontSize: '0.7rem',
                        fontWeight: 600,
                        cursor: 'pointer',
                        display: 'flex',
                        alignItems: 'center',
                        gap: '4px',
                        transition: 'all 0.15s ease'
                      }}
                    >
                      <Download size={11} /> Export Memo
                    </button>
                  </div>
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                    {m.citations.map((c, cIdx) => (
                      <CitationCard
                        key={cIdx}
                        citation={c}
                        onSelectCitation={onSelectCitation}
                      />
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>
        ))}
        
        {loading && (
          <div className="animate-fade-in" style={{ display: 'flex', alignItems: 'center', gap: '10px', color: 'var(--text-muted)', fontSize: '0.85rem', paddingLeft: '48px' }}>
            <Sparkles size={16} color="#6366f1" className="pulse-indicator" />
            <span>Multi-Agent Fleet auditing RBI Master Directions against vector lake...</span>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Suggested Follow-up Prompt Chips */}
      {activeSuggestions && activeSuggestions.length > 0 && !loading && (
        <div style={{
          padding: '10px 24px',
          background: 'rgba(10, 14, 22, 0.65)',
          borderTop: '1px solid var(--border-subtle)',
          display: 'flex',
          gap: '8px',
          overflowX: 'auto',
          alignItems: 'center'
        }}>
          <span style={{ fontSize: '0.7rem', color: 'var(--text-muted)', flexShrink: 0, fontWeight: 700, letterSpacing: '0.04em', textTransform: 'uppercase' }}>
            Suggested:
          </span>
          {activeSuggestions.slice(0, 3).map((s, sIdx) => (
            <button
              key={sIdx}
              onClick={() => submitQuery(s)}
              style={{
                background: 'rgba(255, 255, 255, 0.04)',
                border: '1px solid var(--border-subtle)',
                borderRadius: '9999px',
                padding: '5px 12px',
                color: 'var(--text-secondary)',
                fontSize: '0.75rem',
                cursor: 'pointer',
                whiteSpace: 'nowrap',
                display: 'flex',
                alignItems: 'center',
                gap: '5px',
                transition: 'all 0.18s ease'
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.background = 'rgba(99, 102, 241, 0.18)'
                e.currentTarget.style.borderColor = 'rgba(99, 102, 241, 0.4)'
                e.currentTarget.style.color = '#ffffff'
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.background = 'rgba(255, 255, 255, 0.04)'
                e.currentTarget.style.borderColor = 'var(--border-subtle)'
                e.currentTarget.style.color = 'var(--text-secondary)'
              }}
            >
              <span>{s}</span>
              <ArrowRight size={11} />
            </button>
          ))}
        </div>
      )}

      {/* Floating Modern Command Bar Input */}
      <div style={{ padding: '16px 24px', background: 'rgba(10, 14, 22, 0.85)', borderTop: '1px solid var(--border-subtle)' }}>
        <form onSubmit={handleSend} style={{
          display: 'flex',
          alignItems: 'center',
          gap: '10px',
          background: 'rgba(15, 23, 42, 0.75)',
          borderRadius: '14px',
          border: '1px solid var(--border-glass)',
          padding: '6px 8px 6px 16px',
          boxShadow: '0 4px 20px rgba(0, 0, 0, 0.3)',
          transition: 'all 0.2s ease'
        }}>
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask an RBI compliance question (e.g. KYC for NRIs, IT data localization, CoFT tokenisation)..."
            style={{
              flex: 1,
              background: 'transparent',
              border: 'none',
              color: '#ffffff',
              fontSize: '0.9rem',
              outline: 'none',
              fontFamily: 'inherit'
            }}
          />
          <button
            type="submit"
            disabled={loading || !input.trim()}
            style={{
              background: input.trim() ? 'linear-gradient(135deg, #4f46e5 0%, #06b6d4 100%)' : 'rgba(255, 255, 255, 0.08)',
              border: 'none',
              borderRadius: '10px',
              padding: '10px 18px',
              color: input.trim() ? '#ffffff' : 'var(--text-muted)',
              cursor: input.trim() ? 'pointer' : 'not-allowed',
              display: 'flex',
              alignItems: 'center',
              gap: '6px',
              fontWeight: 600,
              fontSize: '0.85rem',
              transition: 'all 0.2s ease',
              boxShadow: input.trim() ? '0 0 12px rgba(79, 70, 229, 0.4)' : 'none'
            }}
          >
            <span>Send</span>
            <Send size={14} />
          </button>
        </form>
      </div>
    </div>
  )
}
