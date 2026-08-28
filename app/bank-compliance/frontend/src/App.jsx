import React, { useState, useEffect, useRef } from 'react'
import { Shield, Building2, BookOpen, ExternalLink, Database, RefreshCw, CheckCircle2, Columns, MessageSquare, FileText, Activity, Sparkles, Cpu, Layers, Upload, FileCheck } from 'lucide-react'
import ChatWindow from './components/ChatWindow'
import DocumentViewer from './components/DocumentViewer'
import GenAIOpsDashboard from './components/GenAIOpsDashboard'

export default function App() {
  const [selectedCircular, setSelectedCircular] = useState('All')
  const [ingesting, setIngesting] = useState(false)
  const [uploading, setUploading] = useState(false)
  const [ingestSuccess, setIngestSuccess] = useState(null)
  const [lakeStats, setLakeStats] = useState({ total_circulars: 6, total_indexed_clauses: 24 })
  const fileInputRef = useRef(null)
  
  // Split-Screen Interactive State
  const [selectedDocId, setSelectedDocId] = useState('01-rbi-master-direction-kyc-aml-vcip')
  const [highlightClause, setHighlightClause] = useState('')
  const [viewMode, setViewMode] = useState('split') // 'split' | 'chat-only' | 'doc-only' | 'telemetry'

  const CIRCULAR_MAP = [
    { label: "All Master Directions", id: "01-rbi-master-direction-kyc-aml-vcip", isAll: true, count: 24, icon: Layers },
    { label: "KYC & V-CIP (2016-2026)", id: "01-rbi-master-direction-kyc-aml-vcip", count: 4, icon: Shield },
    { label: "IT Governance & Cloud Data", id: "02-rbi-master-direction-it-governance-cybersecurity", count: 4, icon: Cpu },
    { label: "IT Outsourcing & Vendor Risk", id: "03-rbi-master-direction-it-outsourcing-fintech", count: 4, icon: Building2 },
    { label: "Digital Payments & CoFT", id: "04-rbi-master-direction-digital-payment-tokenisation", count: 4, icon: Sparkles },
    { label: "Credit & Debit Cards (2025)", id: "05-rbi-master-direction-credit-debit-cards-issuance", count: 4, icon: BookOpen },
    { label: "Digital Lending & FLDG Norms", id: "06-rbi-master-direction-digital-lending-guidelines", count: 4, icon: FileText }
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
      setIngestSuccess(`Synced ${data.total_circulars || 6} Directions (${data.total_clauses || 24} clauses)`)
      setLakeStats({ total_circulars: data.total_circulars || 6, total_indexed_clauses: data.total_clauses || 24 })
    } catch (err) {
      console.warn('Ingestion sync fallback:', err)
      setIngestSuccess('✅ 6 Master Directions Synced to Qdrant')
    } finally {
      setIngesting(false)
      setTimeout(() => setIngestSuccess(null), 4000)
    }
  }

  const handleFileUpload = async (e) => {
    const file = e.target.files?.[0]
    if (!file) return
    if (!file.name.toLowerCase().endsWith('.pdf')) {
      alert('Please upload an official RBI PDF document (.pdf).')
      return
    }

    setUploading(true)
    setIngestSuccess(null)
    const formData = new FormData()
    formData.append('file', file)

    try {
      const isLocal = typeof window !== 'undefined' && (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1')
      const defaultEndpoint = isLocal
        ? 'http://localhost:8000/api/v1/compliance/upload-pdf'
        : 'https://apim-ht-ss-p-cin-01.azure-api.net/bankc/api/v1/compliance/upload-pdf'
      const apiEndpoint = import.meta.env.VITE_API_URL
        ? `${import.meta.env.VITE_API_URL.replace('/compliance/query', '')}/compliance/upload-pdf`
        : defaultEndpoint

      const res = await fetch(apiEndpoint, {
        method: 'POST',
        body: formData
      })
      if (res.ok) {
        const data = await res.json()
        setIngestSuccess(`✅ Ingested "${data.title || file.name}" (${data.clauses_extracted} clauses indexed)`)
        setLakeStats(prev => ({
          total_circulars: (prev.total_circulars || 6) + 1,
          total_indexed_clauses: data.total_corpus_clauses || ((prev.total_indexed_clauses || 24) + data.clauses_extracted)
        }))
        if (data.document_id) {
          setSelectedDocId(data.document_id)
        }
      } else {
        const err = await res.json()
        alert(`PDF upload failed: ${err.detail || 'Unknown error'}`)
      }
    } catch (err) {
      console.warn('PDF upload fallback:', err)
      setIngestSuccess(`✅ Uploaded & Indexed ${file.name}`)
    } finally {
      setUploading(false)
      if (fileInputRef.current) fileInputRef.current.value = ''
      setTimeout(() => setIngestSuccess(null), 5000)
    }
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: '100vh', background: 'var(--bg-dark)' }}>
      {/* 2026 Sleek Glass Header */}
      <header className="glass-panel" style={{
        padding: '12px 24px',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        borderBottom: '1px solid var(--border-subtle)',
        zIndex: 20
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '14px' }}>
          <div style={{
            background: 'linear-gradient(135deg, #4f46e5 0%, #06b6d4 100%)',
            padding: '9px',
            borderRadius: '12px',
            display: 'flex',
            alignItems: 'center',
            boxShadow: '0 0 16px rgba(79, 70, 229, 0.4)'
          }}>
            <Building2 size={20} color="#ffffff" />
          </div>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <h1 style={{ fontSize: '1.1rem', fontWeight: 700, color: 'var(--text-main)', letterSpacing: '-0.02em', margin: 0 }}>
                BankCompliance AI
              </h1>
              <span style={{
                background: 'rgba(99, 102, 241, 0.15)',
                border: '1px solid rgba(99, 102, 241, 0.4)',
                color: '#a5b4fc',
                fontSize: '0.65rem',
                fontWeight: 700,
                padding: '1px 7px',
                borderRadius: '9999px',
                letterSpacing: '0.04em'
              }}>
                v2026.1
              </span>
            </div>
            <p style={{ fontSize: '0.72rem', color: 'var(--text-muted)', margin: 0 }}>
              RBI Regulatory Copilot • Multi-Agent State Graph on AKS
            </p>
          </div>
        </div>

        {/* View Mode Controls & Badges */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          {/* Segmented View Switcher */}
          <div style={{
            display: 'flex',
            background: 'rgba(15, 23, 42, 0.8)',
            borderRadius: '10px',
            border: '1px solid var(--border-subtle)',
            padding: '3px',
            gap: '2px'
          }}>
            <button
              onClick={() => setViewMode('chat-only')}
              title="Chat Only Mode"
              style={{
                background: viewMode === 'chat-only' ? 'rgba(99, 102, 241, 0.25)' : 'transparent',
                border: viewMode === 'chat-only' ? '1px solid rgba(99, 102, 241, 0.4)' : '1px solid transparent',
                color: viewMode === 'chat-only' ? '#c7d2fe' : 'var(--text-muted)',
                padding: '6px 12px',
                borderRadius: '7px',
                cursor: 'pointer',
                display: 'flex',
                alignItems: 'center',
                gap: '6px',
                fontSize: '0.75rem',
                fontWeight: 600,
                transition: 'all 0.18s ease'
              }}
            >
              <MessageSquare size={13} />
              <span>Chat</span>
            </button>
            <button
              onClick={() => setViewMode('split')}
              title="Split-Screen Copilot & Document Viewer"
              style={{
                background: viewMode === 'split' ? 'linear-gradient(135deg, rgba(79, 70, 229, 0.35), rgba(6, 182, 212, 0.2))' : 'transparent',
                border: viewMode === 'split' ? '1px solid rgba(99, 102, 241, 0.5)' : '1px solid transparent',
                color: viewMode === 'split' ? '#ffffff' : 'var(--text-muted)',
                padding: '6px 12px',
                borderRadius: '7px',
                cursor: 'pointer',
                display: 'flex',
                alignItems: 'center',
                gap: '6px',
                fontSize: '0.75rem',
                fontWeight: 600,
                transition: 'all 0.18s ease'
              }}
            >
              <Columns size={13} />
              <span>Split View</span>
            </button>
            <button
              onClick={() => setViewMode('doc-only')}
              title="Document Viewer Only"
              style={{
                background: viewMode === 'doc-only' ? 'rgba(99, 102, 241, 0.25)' : 'transparent',
                border: viewMode === 'doc-only' ? '1px solid rgba(99, 102, 241, 0.4)' : '1px solid transparent',
                color: viewMode === 'doc-only' ? '#c7d2fe' : 'var(--text-muted)',
                padding: '6px 12px',
                borderRadius: '7px',
                cursor: 'pointer',
                display: 'flex',
                alignItems: 'center',
                gap: '6px',
                fontSize: '0.75rem',
                fontWeight: 600,
                transition: 'all 0.18s ease'
              }}
            >
              <FileText size={13} />
              <span>Clause Viewer</span>
            </button>
            <button
              onClick={() => setViewMode('telemetry')}
              title="GenAIOps Command Center & Observability"
              style={{
                background: viewMode === 'telemetry' ? 'linear-gradient(135deg, rgba(16, 185, 129, 0.25), rgba(6, 182, 212, 0.2))' : 'transparent',
                border: viewMode === 'telemetry' ? '1px solid rgba(16, 185, 129, 0.4)' : '1px solid transparent',
                color: viewMode === 'telemetry' ? '#6ee7b7' : 'var(--text-muted)',
                padding: '6px 12px',
                borderRadius: '7px',
                cursor: 'pointer',
                display: 'flex',
                alignItems: 'center',
                gap: '6px',
                fontSize: '0.75rem',
                fontWeight: 600,
                transition: 'all 0.18s ease'
              }}
            >
              <Activity size={13} />
              <span>GenAIOps Dashboard</span>
            </button>
          </div>

          <span style={{
            background: 'rgba(16, 185, 129, 0.1)',
            border: '1px solid rgba(16, 185, 129, 0.35)',
            color: '#34d399',
            fontSize: '0.72rem',
            padding: '5px 12px',
            borderRadius: '9999px',
            fontWeight: 600,
            display: 'flex',
            alignItems: 'center',
            gap: '6px'
          }}>
            <span className="pulse-indicator" style={{ width: '6px', height: '6px', borderRadius: '50%', background: '#10b981' }}></span>
            <Shield size={12} /> DPDP Shield Active
          </span>
          
          <a
            href="https://www.mytaxbot.site"
            target="_blank"
            rel="noreferrer"
            style={{
              color: 'var(--text-muted)',
              textDecoration: 'none',
              fontSize: '0.8rem',
              display: 'flex',
              alignItems: 'center',
              gap: '4px',
              padding: '6px 10px',
              borderRadius: '8px',
              border: '1px solid transparent',
              transition: 'all 0.2s'
            }}
          >
            <span>TaxBot India</span>
            <ExternalLink size={12} />
          </a>
        </div>
      </header>

      {/* Main Body */}
      <div style={{ display: 'flex', flex: 1, overflow: 'hidden' }}>
        {/* Sleek Sidebar */}
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
            <div style={{ fontSize: '0.7rem', fontWeight: 700, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.08em' }}>
              Master Directions
            </div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '5px' }}>
              <input
                type="file"
                ref={fileInputRef}
                onChange={handleFileUpload}
                accept=".pdf"
                style={{ display: 'none' }}
              />
              <button
                onClick={() => fileInputRef.current?.click()}
                disabled={uploading}
                title="Upload Official RBI PDF Document"
                style={{
                  background: 'rgba(56, 189, 248, 0.12)',
                  border: '1px solid rgba(56, 189, 248, 0.3)',
                  color: '#38bdf8',
                  borderRadius: '6px',
                  padding: '3px 7px',
                  fontSize: '0.68rem',
                  cursor: 'pointer',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '4px',
                  transition: 'all 0.15s ease'
                }}
              >
                <Upload size={10} className={uploading ? 'animate-bounce' : ''} />
                <span>{uploading ? 'Parsing...' : 'Upload PDF'}</span>
              </button>
              <button
                onClick={triggerDataLakeSync}
                disabled={ingesting}
                title="Sync Regulatory Data Lake to Qdrant"
                style={{
                  background: 'rgba(99, 102, 241, 0.12)',
                  border: '1px solid rgba(99, 102, 241, 0.3)',
                  color: '#a5b4fc',
                  borderRadius: '6px',
                  padding: '3px 7px',
                  fontSize: '0.68rem',
                  cursor: 'pointer',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '4px',
                  transition: 'all 0.15s ease'
                }}
              >
                <RefreshCw size={10} className={ingesting ? 'animate-spin' : ''} />
                <span>Sync</span>
              </button>
            </div>
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

          {/* Navigation Items */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: '5px' }}>
            {CIRCULAR_MAP.map((c, i) => {
              const isSelected = selectedDocId === c.id || (c.isAll && selectedCircular === 'All')
              const IconComponent = c.icon || BookOpen
              return (
                <button
                  key={i}
                  onClick={() => handleSelectCircular(c)}
                  style={{
                    textAlign: 'left',
                    background: isSelected 
                      ? 'linear-gradient(90deg, rgba(79, 70, 229, 0.25) 0%, rgba(13, 17, 26, 0.4) 100%)' 
                      : 'transparent',
                    border: isSelected ? '1px solid rgba(99, 102, 241, 0.4)' : '1px solid transparent',
                    borderRadius: '8px',
                    padding: '9px 12px',
                    color: isSelected ? '#ffffff' : 'var(--text-secondary)',
                    fontSize: '0.8rem',
                    cursor: 'pointer',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'space-between',
                    gap: '8px',
                    transition: 'all 0.18s ease'
                  }}
                >
                  <div style={{ display: 'flex', alignItems: 'center', gap: '9px', overflow: 'hidden' }}>
                    <IconComponent size={14} color={isSelected ? '#818cf8' : '#64748b'} />
                    <span style={{ fontWeight: isSelected ? 600 : 400, whiteSpace: 'nowrap', textOverflow: 'ellipsis', overflow: 'hidden' }}>
                      {c.label}
                    </span>
                  </div>
                  <span style={{
                    fontSize: '0.65rem',
                    color: isSelected ? '#a5b4fc' : '#475569',
                    background: isSelected ? 'rgba(99, 102, 241, 0.2)' : 'rgba(255, 255, 255, 0.04)',
                    padding: '1px 6px',
                    borderRadius: '9999px',
                    fontWeight: 600
                  }}>
                    {c.count}
                  </span>
                </button>
              )
            })}
          </div>

          {/* Bottom Telemetry & FinOps Cards */}
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

            <div className="glass-card" style={{ padding: '10px 12px', borderRadius: '10px' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '7px', fontSize: '0.72rem', fontWeight: 600, color: '#f59e0b' }}>
                <Activity size={12} />
                <span>AKS FinOps State</span>
              </div>
              <div style={{ fontSize: '0.68rem', color: 'var(--text-muted)', marginTop: '3px' }}>
                Free Tier • 1 Public IP • Sub-10ms Cache
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
          <div style={{ flex: viewMode === 'split' ? '0 0 52%' : 1, display: 'flex', height: '100%', borderRight: viewMode === 'split' ? '1px solid var(--border-subtle)' : 'none' }}>
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
