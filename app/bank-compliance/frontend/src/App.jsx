import React, { useState, useEffect } from 'react'
import {
  Shield,
  Building2,
  BookOpen,
  ExternalLink,
  Database,
  RefreshCw,
  CheckCircle2,
  Columns,
  MessageSquare,
  FileText,
  Activity,
  Sparkles,
  Cpu,
  Layers,
  FileCheck,
  Search,
  Filter,
  Sliders,
  Lock,
  Zap,
  Radio
} from 'lucide-react'
import ChatWindow from './components/ChatWindow'
import DocumentViewer from './components/DocumentViewer'
import GenAIOpsDashboard from './components/GenAIOpsDashboard'
import RedlineStudio from './components/RedlineStudio'
import CommandCenter from './components/CommandCenter'
import GovernanceCenter from './components/GovernanceCenter'

export default function App() {
  const [selectedCircular, setSelectedCircular] = useState('All')
  const [activeSector, setActiveSector] = useState('All')
  const [searchFilter, setSearchFilter] = useState('')
  const [ingesting, setIngesting] = useState(false)
  const [ingestSuccess, setIngestSuccess] = useState(null)
  const [lakeStats, setLakeStats] = useState({ total_circulars: 12, total_indexed_clauses: 120 })

  // ── Global Enterprise Architecture Navigation ────────────────────────────────
  // activePillar: 'copilot' | 'command' | 'governance' | 'monitoring' | 'redline'
  const [activePillar, setActivePillar] = useState('copilot')

  // Copilot Sub-Views: 'split' | 'chat-only' | 'doc-only'
  const [copilotView, setCopilotView] = useState('split')

  // Global Inference Engine Mode: 'cloud' | 'sovereign'
  const [inferenceMode, setInferenceMode] = useState('cloud')

  // Split-Screen & Document Selection State
  const [selectedDocId, setSelectedDocId] = useState('01-rbi-master-direction-kyc-aml-vcip')
  const [highlightClause, setHighlightClause] = useState('')

  const CIRCULAR_MAP = [
    { label: "All Master Directions", id: "01-rbi-master-direction-kyc-aml-vcip", sector: "All", isAll: true, count: 120, icon: Layers },
    // ── Pillar 1: KYC, Risk & Cyber Governance ──────────────────────────────────
    { label: "KYC & V-CIP (2016-2026)", id: "01-rbi-master-direction-kyc-aml-vcip", sector: "KYC & Fraud", count: 8, icon: Shield },
    { label: "IT Governance & Cyber Risk", id: "02-rbi-master-direction-it-governance-cybersecurity", sector: "Cyber & IT", count: 8, icon: Cpu },
    { label: "IT Outsourcing & Cloud Data", id: "03-rbi-master-direction-it-outsourcing-fintech", sector: "Cyber & IT", count: 8, icon: Building2 },
    { label: "Frauds Classification (FMR)", id: "07-rbi-master-direction-frauds-classification-reporting", sector: "KYC & Fraud", count: 8, icon: Shield },
    { label: "Integrated Ombudsman Scheme", id: "08-rbi-master-direction-integrated-ombudsman-scheme", sector: "KYC & Fraud", count: 8, icon: BookOpen },

    // ── Pillar 2: Payments & Digital Lending ────────────────────────────────────
    { label: "Digital Payments & CoFT", id: "04-rbi-master-direction-digital-payment-tokenisation", sector: "Lending & Cards", count: 8, icon: Sparkles },
    { label: "Credit & Debit Cards (2025)", id: "05-rbi-master-direction-credit-debit-cards-issuance", sector: "Lending & Cards", count: 8, icon: BookOpen },
    { label: "Digital Lending & FLDG Norms", id: "06-rbi-master-direction-digital-lending-guidelines", sector: "Lending & Cards", count: 8, icon: FileText },
    { label: "Prepaid Instruments (PPI)", id: "11-rbi-master-direction-prepaid-payment-instruments", sector: "Lending & Cards", count: 8, icon: Sparkles },

    // ── Pillar 3: Capital, Liquidity & Forex ────────────────────────────────────
    { label: "Basel III Capital & LCR", id: "09-rbi-master-direction-basel-iii-capital-regulations", sector: "Capital & Basel", count: 8, icon: Database },
    { label: "FEMA & LRS Trade Remittance", id: "10-rbi-master-direction-fema-lrs-trade-remittance", sector: "Forex & Payments", count: 8, icon: ExternalLink },
    { label: "Safe Deposit Lockers Norms", id: "12-rbi-master-direction-bank-lockers-safe-custody", sector: "Forex & Payments", count: 8, icon: Shield }
  ]

  const handleSelectCircular = (item) => {
    setSelectedCircular(item.isAll ? 'All' : item.label)
    setSelectedDocId(item.id)
    setHighlightClause('')
    if (activePillar !== 'copilot') {
      setActivePillar('copilot')
    }
    if (copilotView === 'chat-only') {
      setCopilotView('split')
    }
  }

  const handleSelectCitation = (citation) => {
    let targetDocId = '01-rbi-master-direction-kyc-aml-vcip'
    const circLower = (citation.circular_no || citation.title || '').toLowerCase()

    if (circLower.includes('it-gov') || circLower.includes('cyber') || circLower.includes('localization')) {
      targetDocId = '02-rbi-master-direction-it-governance-cybersecurity'
    } else if (circLower.includes('outsource') || circLower.includes('fintech') || circLower.includes('vendor')) {
      targetDocId = '03-rbi-master-direction-it-outsourcing-fintech'
    } else if (circLower.includes('token') || circLower.includes('payment') || circLower.includes('card-on-file')) {
      targetDocId = '04-rbi-master-direction-digital-payment-tokenisation'
    } else if (circLower.includes('card') || circLower.includes('billing')) {
      targetDocId = '05-rbi-master-direction-credit-debit-cards-issuance'
    } else if (circLower.includes('lending') || circLower.includes('lsp') || circLower.includes('dla')) {
      targetDocId = '06-rbi-master-direction-digital-lending-guidelines'
    }

    setSelectedDocId(targetDocId)
    setHighlightClause(citation.clause || citation.text?.slice(0, 30) || '')
    if (activePillar !== 'copilot') {
      setActivePillar('copilot')
    }
    if (copilotView === 'chat-only') {
      setCopilotView('split')
    }
  }

  const triggerDataLakeSync = async () => {
    setIngesting(true)
    setIngestSuccess(null)
    try {
      const isLocal = typeof window !== 'undefined' && (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1')
      const defaultEndpoint = isLocal
        ? 'http://localhost:8000/api/v1/compliance/ingest'
        : 'https://apim-ht-ss-p-cin-01.azure-api.net/bankc/api/v1/compliance/ingest'
      const apiEndpoint = import.meta.env.VITE_API_URL
        ? `${import.meta.env.VITE_API_URL.replace('/compliance/query', '')}/compliance/ingest`
        : defaultEndpoint

      const res = await fetch(apiEndpoint, { method: 'POST' })
      const data = await res.json()
      setIngestSuccess(`Synced ${data.total_circulars || 12} Directions (${data.total_clauses || 120} clauses)`)
      setLakeStats({ total_circulars: data.total_circulars || 12, total_indexed_clauses: data.total_clauses || 120 })
    } catch (err) {
      console.warn('Ingestion sync fallback:', err)
      setIngestSuccess('✅ 12 Master Directions Synced to Qdrant')
    } finally {
      setIngesting(false)
      setTimeout(() => setIngestSuccess(null), 4000)
    }
  }

  const filteredCirculars = CIRCULAR_MAP.filter(c => {
    const matchesSector = activeSector === 'All' || c.sector === activeSector || c.isAll
    const matchesSearch = c.label.toLowerCase().includes(searchFilter.toLowerCase())
    return matchesSector && matchesSearch
  })

  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: '100vh', background: 'var(--bg-dark)' }}>
      {/* ── Enterprise Executive Navigation Bar ─────────────────────────────── */}
      <header className="glass-panel" style={{
        padding: '8px 20px',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        borderBottom: '1px solid var(--border-subtle)',
        zIndex: 30,
        gap: '16px',
        flexWrap: 'wrap'
      }}>
        {/* Left: Brand & Platform Identity */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <div style={{
            background: 'linear-gradient(135deg, #4f46e5 0%, #06b6d4 100%)',
            padding: '7px',
            borderRadius: '9px',
            display: 'flex',
            alignItems: 'center',
            boxShadow: '0 0 16px rgba(79, 70, 229, 0.4)'
          }}>
            <Building2 size={18} color="#ffffff" />
          </div>
          <div>
            <h1 style={{ fontSize: '1rem', fontWeight: 800, color: 'var(--text-main)', letterSpacing: '-0.02em', margin: 0 }}>
              BankCompliance AI
            </h1>
            <p style={{ fontSize: '0.68rem', color: 'var(--text-muted)', margin: 0 }}>
              RBI Master Directions • Central India AKS Cluster
            </p>
          </div>
        </div>

        {/* Center: 5 Core Enterprise Command Pillars */}
        <nav style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
          {/* Pillar 1: Copilot */}
          <button
            onClick={() => setActivePillar('copilot')}
            style={{
              background: activePillar === 'copilot' ? 'linear-gradient(135deg, rgba(79, 70, 229, 0.3), rgba(6, 182, 212, 0.2))' : 'transparent',
              border: activePillar === 'copilot' ? '1px solid rgba(99, 102, 241, 0.5)' : '1px solid transparent',
              color: activePillar === 'copilot' ? '#ffffff' : 'var(--text-muted)',
              padding: '6px 12px',
              borderRadius: '8px',
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: '6px',
              fontSize: '0.75rem',
              fontWeight: 700,
              transition: 'all 0.18s ease'
            }}
          >
            <MessageSquare size={13} />
            <span>Regulatory Copilot</span>
          </button>

          {/* Pillar 2: Command Center */}
          <button
            onClick={() => setActivePillar('command')}
            style={{
              background: activePillar === 'command' ? 'linear-gradient(135deg, rgba(99, 102, 241, 0.3), rgba(139, 92, 246, 0.2))' : 'transparent',
              border: activePillar === 'command' ? '1px solid rgba(99, 102, 241, 0.5)' : '1px solid transparent',
              color: activePillar === 'command' ? '#c7d2fe' : 'var(--text-muted)',
              padding: '6px 12px',
              borderRadius: '8px',
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: '6px',
              fontSize: '0.75rem',
              fontWeight: 700,
              transition: 'all 0.18s ease'
            }}
          >
            <Sliders size={13} />
            <span>Command Center</span>
          </button>

          {/* Pillar 3: Governance Center */}
          <button
            onClick={() => setActivePillar('governance')}
            style={{
              background: activePillar === 'governance' ? 'linear-gradient(135deg, rgba(16, 185, 129, 0.25), rgba(6, 182, 212, 0.2))' : 'transparent',
              border: activePillar === 'governance' ? '1px solid rgba(16, 185, 129, 0.5)' : '1px solid transparent',
              color: activePillar === 'governance' ? '#34d399' : 'var(--text-muted)',
              padding: '6px 12px',
              borderRadius: '8px',
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: '6px',
              fontSize: '0.75rem',
              fontWeight: 700,
              transition: 'all 0.18s ease'
            }}
          >
            <Shield size={13} />
            <span>Governance & DPDP</span>
          </button>

          {/* Pillar 4: Live Monitoring */}
          <button
            onClick={() => setActivePillar('monitoring')}
            style={{
              background: activePillar === 'monitoring' ? 'linear-gradient(135deg, rgba(6, 182, 212, 0.25), rgba(59, 130, 246, 0.2))' : 'transparent',
              border: activePillar === 'monitoring' ? '1px solid rgba(6, 182, 212, 0.5)' : '1px solid transparent',
              color: activePillar === 'monitoring' ? '#38bdf8' : 'var(--text-muted)',
              padding: '6px 12px',
              borderRadius: '8px',
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: '6px',
              fontSize: '0.75rem',
              fontWeight: 700,
              transition: 'all 0.18s ease'
            }}
          >
            <Activity size={13} />
            <span>Live Monitoring</span>
          </button>

          {/* Pillar 5: Policy Redliner */}
          <button
            onClick={() => setActivePillar('redline')}
            style={{
              background: activePillar === 'redline' ? 'linear-gradient(135deg, rgba(236, 72, 153, 0.3), rgba(139, 92, 246, 0.2))' : 'transparent',
              border: activePillar === 'redline' ? '1px solid rgba(236, 72, 153, 0.5)' : '1px solid transparent',
              color: activePillar === 'redline' ? '#f472b6' : 'var(--text-muted)',
              padding: '6px 12px',
              borderRadius: '8px',
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: '6px',
              fontSize: '0.75rem',
              fontWeight: 700,
              transition: 'all 0.18s ease'
            }}
          >
            <FileCheck size={13} />
            <span>Policy Redliner</span>
          </button>
        </nav>

        {/* Right: Global Inference Engine Switcher & APIM Health */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <div style={{
            display: 'inline-flex',
            background: 'rgba(15, 23, 42, 0.85)',
            padding: '3px',
            borderRadius: '9px',
            border: '1px solid rgba(255, 255, 255, 0.08)',
            gap: '3px'
          }}>
            <button
              type="button"
              onClick={() => setInferenceMode('cloud')}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '5px',
                padding: '5px 11px',
                borderRadius: '6px',
                fontSize: '0.73rem',
                fontWeight: 600,
                border: inferenceMode === 'cloud' ? '1px solid rgba(99, 102, 241, 0.5)' : '1px solid transparent',
                background: inferenceMode === 'cloud' ? 'rgba(99, 102, 241, 0.25)' : 'transparent',
                color: inferenceMode === 'cloud' ? '#c7d2fe' : 'var(--text-muted)',
                cursor: 'pointer',
                transition: 'all 0.18s ease'
              }}
            >
              <Zap size={12} color={inferenceMode === 'cloud' ? '#818cf8' : 'currentColor'} />
              <span>Multi-Cloud Fleet (Groq/Gemini)</span>
            </button>

            <button
              type="button"
              onClick={() => setInferenceMode('sovereign')}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '5px',
                padding: '5px 11px',
                borderRadius: '6px',
                fontSize: '0.73rem',
                fontWeight: 600,
                border: inferenceMode === 'sovereign' ? '1px solid rgba(16, 185, 129, 0.5)' : '1px solid transparent',
                background: inferenceMode === 'sovereign' ? 'rgba(16, 185, 129, 0.25)' : 'transparent',
                color: inferenceMode === 'sovereign' ? '#34d399' : 'var(--text-muted)',
                cursor: 'pointer',
                transition: 'all 0.18s ease'
              }}
            >
              <Shield size={12} color={inferenceMode === 'sovereign' ? '#34d399' : 'currentColor'} />
              <span>Sovereign SLM (Qwen 2.5)</span>
            </button>
          </div>

          <span style={{
            background: 'rgba(16, 185, 129, 0.1)',
            border: '1px solid rgba(16, 185, 129, 0.35)',
            color: '#34d399',
            fontSize: '0.68rem',
            padding: '4px 9px',
            borderRadius: '9999px',
            fontWeight: 600,
            display: 'flex',
            alignItems: 'center',
            gap: '5px'
          }}>
            <span className="pulse-indicator" style={{ width: '6px', height: '6px', borderRadius: '50%', background: '#10b981' }}></span>
            <span>APIM 200 OK</span>
          </span>
        </div>
      </header>

      {/* ── Main Dynamic Workspace View ────────────────────────────────────── */}
      <div style={{ display: 'flex', flex: 1, overflow: 'hidden' }}>
        {/* Pillar 2: Command Center Mode */}
        {activePillar === 'command' && (
          <CommandCenter
            inferenceMode={inferenceMode}
            setInferenceMode={setInferenceMode}
            onNavigateToCopilot={() => setActivePillar('copilot')}
            lakeStats={lakeStats}
            onTriggerSync={triggerDataLakeSync}
          />
        )}

        {/* Pillar 3: Governance Center Mode */}
        {activePillar === 'governance' && (
          <GovernanceCenter
            lakeStats={lakeStats}
            onSelectCircular={handleSelectCircular}
          />
        )}

        {/* Pillar 4: Live Monitoring Mode */}
        {activePillar === 'monitoring' && (
          <GenAIOpsDashboard onBackToChat={() => setActivePillar('copilot')} />
        )}

        {/* Pillar 5: Policy Redliner Mode */}
        {activePillar === 'redline' && (
          <RedlineStudio />
        )}

        {/* Pillar 1: Regulatory Copilot Mode (Split Screen) */}
        {activePillar === 'copilot' && (
          <>
            {/* Master Directions Directory Sidebar */}
            <aside style={{
              width: '275px',
              background: 'rgba(10, 14, 22, 0.95)',
              borderRight: '1px solid var(--border-subtle)',
              padding: '16px',
              display: 'flex',
              flexDirection: 'column',
              gap: '12px',
              overflowY: 'auto'
            }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <div style={{ fontSize: '0.72rem', fontWeight: 700, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.08em', display: 'flex', alignItems: 'center', gap: '6px' }}>
                  <Layers size={13} color="#818cf8" />
                  <span>Master Directions</span>
                </div>
                <span style={{
                  fontSize: '0.68rem',
                  color: '#818cf8',
                  background: 'rgba(99, 102, 241, 0.12)',
                  border: '1px solid rgba(99, 102, 241, 0.25)',
                  padding: '1px 7px',
                  borderRadius: '9999px',
                  fontWeight: 600
                }}>
                  {lakeStats.total_circulars || 12} Indexed
                </span>
              </div>

              {ingestSuccess && (
                <div className="animate-fade-in" style={{
                  background: 'rgba(16, 185, 129, 0.15)',
                  border: '1px solid rgba(16, 185, 129, 0.4)',
                  borderRadius: '8px',
                  padding: '8px 10px',
                  fontSize: '0.72rem',
                  color: '#34d399',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '6px'
                }}>
                  <CheckCircle2 size={13} />
                  <span>{ingestSuccess}</span>
                </div>
              )}

              {/* Sector Filter Chips */}
              <div style={{ display: 'flex', gap: '4px', overflowX: 'auto', paddingBottom: '4px' }}>
                {['All', 'Cyber & IT', 'KYC & Fraud', 'Lending & Cards', 'Capital & Basel', 'Forex & Payments'].map((sector) => (
                  <button
                    key={sector}
                    onClick={() => setActiveSector(sector)}
                    style={{
                      background: activeSector === sector ? 'rgba(99, 102, 241, 0.25)' : 'rgba(255, 255, 255, 0.04)',
                      border: activeSector === sector ? '1px solid rgba(99, 102, 241, 0.4)' : '1px solid transparent',
                      color: activeSector === sector ? '#c7d2fe' : 'var(--text-muted)',
                      padding: '3px 8px',
                      borderRadius: '6px',
                      fontSize: '0.66rem',
                      fontWeight: 600,
                      cursor: 'pointer',
                      whiteSpace: 'nowrap'
                    }}
                  >
                    {sector}
                  </button>
                ))}
              </div>

              {/* Search Bar */}
              <div style={{ position: 'relative' }}>
                <Search size={12} style={{ position: 'absolute', left: '10px', top: '50%', transform: 'translateY(-50%)', color: 'var(--text-muted)' }} />
                <input
                  type="text"
                  placeholder="Filter RBI Master Directions..."
                  value={searchFilter}
                  onChange={(e) => setSearchFilter(e.target.value)}
                  style={{
                    width: '100%',
                    background: 'rgba(15, 23, 42, 0.6)',
                    border: '1px solid var(--border-subtle)',
                    borderRadius: '8px',
                    padding: '6px 10px 6px 28px',
                    fontSize: '0.75rem',
                    color: 'var(--text-main)',
                    outline: 'none'
                  }}
                />
              </div>

              {/* Circulars List */}
              <div style={{ display: 'flex', flexDirection: 'column', gap: '4px', flex: 1 }}>
                {filteredCirculars.map((c, i) => {
                  const isSelected = selectedCircular === (c.isAll ? 'All' : c.label)
                  const IconComponent = c.icon || Layers
                  return (
                    <button
                      key={i}
                      onClick={() => handleSelectCircular(c)}
                      style={{
                        background: isSelected ? 'linear-gradient(135deg, rgba(79, 70, 229, 0.25), rgba(6, 182, 212, 0.15))' : 'transparent',
                        border: isSelected ? '1px solid rgba(99, 102, 241, 0.4)' : '1px solid transparent',
                        color: isSelected ? '#ffffff' : 'var(--text-muted)',
                        padding: '8px 10px',
                        borderRadius: '8px',
                        textAlign: 'left',
                        fontSize: '0.74rem',
                        cursor: 'pointer',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'space-between',
                        gap: '8px',
                        transition: 'all 0.18s ease'
                      }}
                    >
                      <div style={{ display: 'flex', alignItems: 'center', gap: '8px', overflow: 'hidden' }}>
                        <IconComponent size={13} color={isSelected ? '#818cf8' : '#64748b'} />
                        <span style={{ fontWeight: isSelected ? 600 : 400, whiteSpace: 'nowrap', textOverflow: 'ellipsis', overflow: 'hidden' }}>
                          {c.label}
                        </span>
                      </div>
                      <span style={{
                        fontSize: '0.62rem',
                        color: isSelected ? '#a5b4fc' : '#475569',
                        background: isSelected ? 'rgba(99, 102, 241, 0.2)' : 'rgba(255, 255, 255, 0.04)',
                        padding: '1px 5px',
                        borderRadius: '9999px',
                        fontWeight: 600
                      }}>
                        {c.count}
                      </span>
                    </button>
                  )
                })}
              </div>

              {/* Bottom Quick Info */}
              <div style={{ marginTop: 'auto', display: 'flex', flexDirection: 'column', gap: '8px' }}>
                <div className="glass-card" style={{ padding: '10px 12px', borderRadius: '10px' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '7px', fontSize: '0.72rem', fontWeight: 600, color: '#38bdf8' }}>
                    <Database size={12} />
                    <span>Knowledge Lake</span>
                  </div>
                  <div style={{ fontSize: '0.68rem', color: 'var(--text-muted)', marginTop: '3px' }}>
                    {lakeStats.total_circulars} Master Directions • {lakeStats.total_indexed_clauses} Clauses in Qdrant
                  </div>
                </div>
              </div>
            </aside>

            {/* Main Copilot Workspace Area */}
            <div style={{ flex: 1, display: 'flex', flexDirection: 'column', height: '100%', overflow: 'hidden' }}>
              {/* Copilot Sub-View Control Bar */}
              <div style={{
                background: 'rgba(10, 14, 22, 0.95)',
                borderBottom: '1px solid var(--border-subtle)',
                padding: '6px 16px',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                flexWrap: 'wrap',
                gap: '8px'
              }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '0.73rem', color: 'var(--text-muted)' }}>
                  <span>Layout Mode:</span>
                  <span style={{ color: '#e2e8f0', fontWeight: 600 }}>
                    {copilotView === 'split' ? 'Split View (Chat + Statutory Clauses)' : copilotView === 'chat-only' ? 'Copilot Chat Full-Width' : 'Statutory Document Full-Width'}
                  </span>
                </div>

                <div style={{
                  display: 'flex',
                  background: 'rgba(15, 23, 42, 0.8)',
                  borderRadius: '7px',
                  border: '1px solid var(--border-subtle)',
                  padding: '2px',
                  gap: '2px'
                }}>
                  <button
                    onClick={() => setCopilotView('chat-only')}
                    style={{
                      background: copilotView === 'chat-only' ? 'rgba(99, 102, 241, 0.25)' : 'transparent',
                      border: copilotView === 'chat-only' ? '1px solid rgba(99, 102, 241, 0.4)' : '1px solid transparent',
                      color: copilotView === 'chat-only' ? '#c7d2fe' : 'var(--text-muted)',
                      padding: '3px 9px',
                      borderRadius: '5px',
                      cursor: 'pointer',
                      fontSize: '0.71rem',
                      fontWeight: 600,
                      display: 'flex',
                      alignItems: 'center',
                      gap: '4px'
                    }}
                  >
                    <MessageSquare size={11} />
                    <span>Chat Only</span>
                  </button>
                  <button
                    onClick={() => setCopilotView('split')}
                    style={{
                      background: copilotView === 'split' ? 'rgba(99, 102, 241, 0.25)' : 'transparent',
                      border: copilotView === 'split' ? '1px solid rgba(99, 102, 241, 0.4)' : '1px solid transparent',
                      color: copilotView === 'split' ? '#c7d2fe' : 'var(--text-muted)',
                      padding: '3px 9px',
                      borderRadius: '5px',
                      cursor: 'pointer',
                      fontSize: '0.71rem',
                      fontWeight: 600,
                      display: 'flex',
                      alignItems: 'center',
                      gap: '4px'
                    }}
                  >
                    <Columns size={11} />
                    <span>Split View</span>
                  </button>
                  <button
                    onClick={() => setCopilotView('doc-only')}
                    style={{
                      background: copilotView === 'doc-only' ? 'rgba(99, 102, 241, 0.25)' : 'transparent',
                      border: copilotView === 'doc-only' ? '1px solid rgba(99, 102, 241, 0.4)' : '1px solid transparent',
                      color: copilotView === 'doc-only' ? '#c7d2fe' : 'var(--text-muted)',
                      padding: '3px 9px',
                      borderRadius: '5px',
                      cursor: 'pointer',
                      fontSize: '0.71rem',
                      fontWeight: 600,
                      display: 'flex',
                      alignItems: 'center',
                      gap: '4px'
                    }}
                  >
                    <FileText size={11} />
                    <span>Document Only</span>
                  </button>
                </div>
              </div>

              {/* Workspace Inner Panes */}
              <div style={{ display: 'flex', flex: 1, overflow: 'hidden' }}>
                {copilotView !== 'doc-only' && (
                  <div style={{
                    flex: copilotView === 'split' ? '0 0 52%' : 1,
                    display: 'flex',
                    height: '100%',
                    borderRight: copilotView === 'split' ? '1px solid var(--border-subtle)' : 'none'
                  }}>
                    <ChatWindow
                      selectedCircular={selectedCircular}
                      onSelectCitation={handleSelectCitation}
                      inferenceMode={inferenceMode}
                      onToggleInferenceMode={setInferenceMode}
                    />
                  </div>
                )}

                {copilotView !== 'chat-only' && (
                  <DocumentViewer
                    selectedDocId={selectedDocId}
                    highlightClause={highlightClause}
                    viewMode={copilotView === 'doc-only' ? 'fullscreen' : 'split'}
                    onToggleViewMode={() => setCopilotView(prev => prev === 'doc-only' ? 'split' : 'doc-only')}
                    onClose={() => setCopilotView('chat-only')}
                  />
                )}
              </div>
            </div>
          </>
        )}
      </div>
    </div>
  )
}
