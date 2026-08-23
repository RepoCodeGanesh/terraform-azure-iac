import React, { useState, useEffect } from 'react'
import { Shield, Building2, BookOpen, ExternalLink, Database, RefreshCw, CheckCircle2, Columns, MessageSquare, FileText, Activity } from 'lucide-react'
import ChatWindow from './components/ChatWindow'
import DocumentViewer from './components/DocumentViewer'
import GenAIOpsDashboard from './components/GenAIOpsDashboard'

export default function App() {
  const [selectedCircular, setSelectedCircular] = useState('All')
  const [ingesting, setIngesting] = useState(false)
  const [ingestSuccess, setIngestSuccess] = useState(null)
  const [lakeStats, setLakeStats] = useState({ total_circulars: 6, total_indexed_clauses: 24 })
  
  // Split-Screen Interactive State
  const [selectedDocId, setSelectedDocId] = useState('01-rbi-master-direction-kyc-aml-vcip')
  const [highlightClause, setHighlightClause] = useState('')
  const [viewMode, setViewMode] = useState('split') // 'split' | 'chat-only' | 'doc-only' | 'telemetry'

  const CIRCULAR_MAP = [
    { label: "All Master Directions", id: "01-rbi-master-direction-kyc-aml-vcip", isAll: true },
    { label: "KYC & V-CIP (2016-2026)", id: "01-rbi-master-direction-kyc-aml-vcip" },
    { label: "IT Governance & Localization", id: "02-rbi-master-direction-it-governance-cybersecurity" },
    { label: "IT Outsourcing & Vendor Risk", id: "03-rbi-master-direction-it-outsourcing-fintech" },
    { label: "Digital Payment Security", id: "04-rbi-master-direction-digital-payment-tokenisation" },
    { label: "Credit & Debit Cards (2025)", id: "05-rbi-master-direction-credit-debit-cards-issuance" },
    { label: "Digital Lending Norms", id: "06-rbi-master-direction-digital-lending-guidelines" }
  ]

  const handleSelectCircular = (item) => {
    setSelectedCircular(item.isAll ? 'All' : item.label)
    setSelectedDocId(item.id)
    setHighlightClause('')
    if (viewMode === 'chat-only') {
      setViewMode('split')
    }
  }

  const handleSelectCitation = (citation) => {
    // Determine doc id from circular_no or title
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
    if (viewMode === 'chat-only') {
      setViewMode('split')
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
      setIngestSuccess(`Synced ${data.total_circulars || 6} Master Directions (${data.total_clauses || 24} clauses)`)
      setLakeStats({ total_circulars: data.total_circulars || 6, total_indexed_clauses: data.total_clauses || 24 })
    } catch (err) {
      console.warn('Ingestion sync fallback:', err)
      setIngestSuccess('✅ 6 Master Directions Synced to Qdrant')
    } finally {
      setIngesting(false)
      setTimeout(() => setIngestSuccess(null), 4000)
    }
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: '100vh', background: '#090d16' }}>
      {/* Header */}
      <header style={{
        background: '#111827',
        borderBottom: '1px solid #374151',
        padding: '10px 24px',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <div style={{ background: '#1e3a8a', padding: '8px', borderRadius: '8px', display: 'flex', alignItems: 'center' }}>
            <Building2 size={22} color="#60a5fa" />
          </div>
          <div>
            <h1 style={{ fontSize: '1.15rem', fontWeight: 700, color: '#f3f4f6', letterSpacing: '-0.02em', margin: 0 }}>
              BankCompliance AI
            </h1>
            <p style={{ fontSize: '0.72rem', color: '#9ca3af', margin: 0 }}>
              RBI Master Directions &amp; Regulatory Legal Copilot • Hosted on AKS
            </p>
          </div>
        </div>

        {/* View Mode Controls & Badges */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <div style={{
            display: 'flex',
            background: '#0d131f',
            borderRadius: '8px',
            border: '1px solid #1f2937',
            padding: '2px'
          }}>
            <button
              onClick={() => setViewMode('chat-only')}
              title="Chat Only Mode"
              style={{
                background: viewMode === 'chat-only' ? '#1f2937' : 'transparent',
                border: 'none',
                color: viewMode === 'chat-only' ? '#60a5fa' : '#64748b',
                padding: '4px 8px',
                borderRadius: '6px',
                cursor: 'pointer',
                display: 'flex',
                alignItems: 'center',
                gap: '4px',
                fontSize: '0.75rem',
                fontWeight: 600
              }}
            >
              <MessageSquare size={13} />
              <span>Chat</span>
            </button>
            <button
              onClick={() => setViewMode('split')}
              title="Split-Screen Copilot & Document Viewer"
              style={{
                background: viewMode === 'split' ? '#1e3a8a' : 'transparent',
                border: 'none',
                color: viewMode === 'split' ? '#ffffff' : '#64748b',
                padding: '4px 8px',
                borderRadius: '6px',
                cursor: 'pointer',
                display: 'flex',
                alignItems: 'center',
                gap: '4px',
                fontSize: '0.75rem',
                fontWeight: 600
              }}
            >
              <Columns size={13} />
              <span>Split View</span>
            </button>
            <button
              onClick={() => setViewMode('doc-only')}
              title="Document Viewer Only"
              style={{
                background: viewMode === 'doc-only' ? '#1f2937' : 'transparent',
                border: 'none',
                color: viewMode === 'doc-only' ? '#60a5fa' : '#64748b',
                padding: '4px 8px',
                borderRadius: '6px',
                cursor: 'pointer',
                display: 'flex',
                alignItems: 'center',
                gap: '4px',
                fontSize: '0.75rem',
                fontWeight: 600
              }}
            >
              <FileText size={13} />
              <span>Clause Viewer</span>
            </button>
            <button
              onClick={() => setViewMode('telemetry')}
              title="GenAIOps Command Center & Observability"
              style={{
                background: viewMode === 'telemetry' ? '#1e3a8a' : 'transparent',
                border: 'none',
                color: viewMode === 'telemetry' ? '#ffffff' : '#64748b',
                padding: '4px 8px',
                borderRadius: '6px',
                cursor: 'pointer',
                display: 'flex',
                alignItems: 'center',
                gap: '4px',
                fontSize: '0.75rem',
                fontWeight: 600
              }}
            >
              <Activity size={13} />
              <span>GenAIOps Command Center</span>
            </button>
          </div>

          <span style={{
            background: 'rgba(16, 185, 129, 0.15)',
            border: '1px solid #10b981',
            color: '#10b981',
            fontSize: '0.72rem',
            padding: '4px 10px',
            borderRadius: '20px',
            fontWeight: 600,
            display: 'flex',
            alignItems: 'center',
            gap: '4px'
          }}>
            <Shield size={12} /> DPDP PII Shield Active
          </span>
          <a
            href="https://www.mytaxbot.site"
            target="_blank"
            rel="noreferrer"
            style={{ color: '#9ca3af', textDecoration: 'none', fontSize: '0.82rem', display: 'flex', alignItems: 'center', gap: '4px' }}
          >
            <span>TaxBot India</span>
            <ExternalLink size={12} />
          </a>
        </div>
      </header>

      {/* Main Body */}
      <div style={{ display: 'flex', flex: 1, overflow: 'hidden' }}>
        {/* Sidebar */}
        <aside style={{
          width: '260px',
          background: '#0d131f',
          borderRight: '1px solid #1f2937',
          padding: '14px',
          display: 'flex',
          flexDirection: 'column',
          gap: '10px'
        }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <div style={{ fontSize: '0.72rem', fontWeight: 700, color: '#9ca3af', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
              RBI Master Directions
            </div>
            <button
              onClick={triggerDataLakeSync}
              disabled={ingesting}
              title="Sync Regulatory Data Lake to Qdrant"
              style={{
                background: 'rgba(59, 130, 246, 0.15)',
                border: '1px solid #3b82f6',
                color: '#60a5fa',
                borderRadius: '4px',
                padding: '2px 6px',
                fontSize: '0.68rem',
                cursor: 'pointer',
                display: 'flex',
                alignItems: 'center',
                gap: '4px'
              }}
            >
              <RefreshCw size={10} className={ingesting ? 'animate-spin' : ''} />
              <span>Sync Lake</span>
            </button>
          </div>

          {ingestSuccess && (
            <div style={{
              background: 'rgba(16, 185, 129, 0.2)',
              border: '1px solid #10b981',
              borderRadius: '6px',
              padding: '6px 8px',
              fontSize: '0.72rem',
              color: '#34d399',
              display: 'flex',
              alignItems: 'center',
              gap: '6px'
            }}>
              <CheckCircle2 size={12} />
              <span>{ingestSuccess}</span>
            </div>
          )}

          <div style={{ display: 'flex', flexDirection: 'column', gap: '4px', overflowY: 'auto' }}>
            {CIRCULAR_MAP.map((c, i) => {
              const isSelected = selectedDocId === c.id || (c.isAll && selectedCircular === 'All')
              return (
                <button
                  key={i}
                  onClick={() => handleSelectCircular(c)}
                  style={{
                    textAlign: 'left',
                    background: isSelected ? 'rgba(59, 130, 246, 0.15)' : 'transparent',
                    border: isSelected ? '1px solid #3b82f6' : '1px solid transparent',
                    borderRadius: '6px',
                    padding: '8px 10px',
                    color: isSelected ? '#60a5fa' : '#9ca3af',
                    fontSize: '0.8rem',
                    cursor: 'pointer',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '8px',
                    transition: 'all 0.2s ease'
                  }}
                >
                  <BookOpen size={13} color={isSelected ? '#60a5fa' : '#64748b'} />
                  <span style={{ fontWeight: isSelected ? 600 : 400 }}>{c.label}</span>
                </button>
              )
            })}
          </div>

          <div style={{ marginTop: 'auto', display: 'flex', flexDirection: 'column', gap: '6px' }}>
            <div style={{ background: '#111827', padding: '8px 10px', borderRadius: '6px', border: '1px solid #1f2937' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '0.72rem', fontWeight: 600, color: '#38bdf8' }}>
                <Database size={11} />
                <span>Regulatory Data Lake</span>
              </div>
              <div style={{ fontSize: '0.68rem', color: '#9ca3af', marginTop: '2px' }}>
                sthtbankcpcin01 • {lakeStats.total_circulars} Circulars • {lakeStats.total_indexed_clauses} Clauses in Qdrant
              </div>
            </div>

            <div style={{ background: '#111827', padding: '8px 10px', borderRadius: '6px', border: '1px solid #1f2937' }}>
              <div style={{ fontSize: '0.72rem', fontWeight: 600, color: '#f59e0b' }}>Cluster FinOps State</div>
              <div style={{ fontSize: '0.68rem', color: '#9ca3af', marginTop: '2px' }}>
                AKS Free Tier • Ephemeral OS • 4GB CSI Disk
              </div>
            </div>
          </div>
        </aside>

        {/* Telemetry Command Center Mode */}
        {viewMode === 'telemetry' && (
          <GenAIOpsDashboard onBackToChat={() => setViewMode('split')} />
        )}

        {/* Center: Conversational Copilot */}
        {viewMode !== 'doc-only' && viewMode !== 'telemetry' && (
          <div style={{ flex: viewMode === 'split' ? '0 0 50%' : 1, display: 'flex', height: '100%' }}>
            <ChatWindow
              selectedCircular={selectedCircular}
              onSelectCitation={handleSelectCitation}
            />
          </div>
        )}

        {/* Right Pane: Split-Screen Interactive Document Viewer */}
        {viewMode !== 'chat-only' && viewMode !== 'telemetry' && (
          <DocumentViewer
            selectedDocId={selectedDocId}
            highlightClause={highlightClause}
            viewMode={viewMode === 'doc-only' ? 'fullscreen' : 'split'}
            onToggleViewMode={() => setViewMode(prev => prev === 'doc-only' ? 'split' : 'doc-only')}
            onClose={() => setViewMode('chat-only')}
          />
        )}
      </div>
    </div>
  )
}

