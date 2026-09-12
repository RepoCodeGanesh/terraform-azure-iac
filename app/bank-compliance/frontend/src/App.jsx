import React, { useState, useEffect } from 'react'
import {
  Building2,
  Sliders,
  Shield,
  Activity,
  FileCheck,
  Zap,
  MessageSquare
} from 'lucide-react'
import ChatWindow from './components/ChatWindow'
import GenAIOpsDashboard from './components/GenAIOpsDashboard'
import RedlineStudio from './components/RedlineStudio'
import CommandCenter from './components/CommandCenter'
import GovernanceCenter from './components/GovernanceCenter'

const VALID_PILLARS = ['copilot', 'command', 'governance', 'monitoring', 'redline']

function getPillarFromPath(pathname) {
  const clean = (pathname || '').toLowerCase().replace(/^\/+/, '').split('/')[0]
  if (VALID_PILLARS.includes(clean)) {
    return clean
  }
  return 'copilot'
}

export default function App() {
  const [lakeStats, setLakeStats] = useState({ total_circulars: 12, total_indexed_clauses: 120 })

  // ── Global Enterprise Architecture Navigation & URL Deep-Linking ───────────
  // activePillar: 'copilot' | 'command' | 'governance' | 'monitoring' | 'redline'
  const [activePillar, setActivePillar] = useState(() => {
    if (typeof window !== 'undefined') {
      return getPillarFromPath(window.location.pathname)
    }
    return 'copilot'
  })

  // Deep-linkable HTML5 history routing helper
  const navigateToPillar = (pillar, replace = false) => {
    setActivePillar(pillar)
    if (typeof window !== 'undefined') {
      const targetPath = pillar === 'copilot' ? '/' : `/${pillar}`
      if (window.location.pathname !== targetPath) {
        if (replace) {
          window.history.replaceState({ pillar }, '', targetPath)
        } else {
          window.history.pushState({ pillar }, '', targetPath)
        }
      }
    }
  }

  // Synchronize browser Back / Forward history navigation
  useEffect(() => {
    const handlePopState = () => {
      const pillar = getPillarFromPath(window.location.pathname)
      setActivePillar(pillar)
    }
    window.addEventListener('popstate', handlePopState)
    return () => window.removeEventListener('popstate', handlePopState)
  }, [])

  // Global Inference Engine Mode: 'cloud' | 'sovereign'
  const [inferenceMode, setInferenceMode] = useState('cloud')

  const triggerDataLakeSync = async () => {
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
      setLakeStats({ total_circulars: data.total_circulars || 12, total_indexed_clauses: data.total_clauses || 120 })
    } catch (err) {
      console.warn('Ingestion sync fallback:', err)
    }
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: '100vh', background: 'var(--bg-dark)' }}>
      {/* ── Enterprise Executive Navigation Bar ─────────────────────────────── */}
      <header className="glass-panel header-container" style={{
        padding: '8px 20px',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        borderBottom: '1px solid var(--border-subtle)',
        zIndex: 30,
        gap: '12px'
      }}>
        {/* Left: Brand & Platform Identity */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px', flexShrink: 0 }}>
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
            <h1 style={{ fontSize: '0.96rem', fontWeight: 800, color: 'var(--text-main)', letterSpacing: '-0.02em', margin: 0 }}>
              BankCompliance AI
            </h1>
            <p className="desktop-only" style={{ fontSize: '0.68rem', color: 'var(--text-muted)', margin: 0 }}>
              RBI Master Directions • Central India AKS Cluster
            </p>
          </div>
        </div>

        {/* Center: 5 Core Enterprise Command Pillars */}
        <nav className="header-nav" style={{ display: 'flex', alignItems: 'center', gap: '4px', flexShrink: 0 }}>
          {/* Pillar 1: Copilot */}
          <button
            onClick={() => navigateToPillar('copilot')}
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
            onClick={() => navigateToPillar('command')}
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
            onClick={() => navigateToPillar('governance')}
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
            <span>Governance &amp; DPDP</span>
          </button>

          {/* Pillar 4: Live Monitoring */}
          <button
            onClick={() => navigateToPillar('monitoring')}
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
            onClick={() => navigateToPillar('redline')}
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
            <span className="nav-btn-text">Policy Redliner</span>
          </button>
        </nav>

        {/* Right: Global Inference Engine Switcher & APIM Health */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', flexShrink: 0 }}>
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
              <span className="engine-btn-text-desktop">Multi-Cloud Fleet (Groq/Gemini)</span>
              <span className="engine-btn-text-mobile">Cloud</span>
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
              <span className="engine-btn-text-desktop">Sovereign SLM (Qwen 2.5)</span>
              <span className="engine-btn-text-mobile">SLM</span>
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
            <span className="desktop-only">APIM 200 OK</span>
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
            onNavigateToCopilot={() => navigateToPillar('copilot')}
            lakeStats={lakeStats}
            onTriggerSync={triggerDataLakeSync}
          />
        )}

        {/* Pillar 3: Governance Center Mode */}
        {activePillar === 'governance' && (
          <GovernanceCenter
            lakeStats={lakeStats}
          />
        )}

        {/* Pillar 4: Live Monitoring Mode */}
        {activePillar === 'monitoring' && (
          <GenAIOpsDashboard onBackToChat={() => navigateToPillar('copilot')} />
        )}

        {/* Pillar 5: Policy Redliner Mode */}
        {activePillar === 'redline' && (
          <RedlineStudio />
        )}

        {/* Pillar 1: Regulatory Copilot Mode (Dedicated Full-Width Clean Chat) */}
        {activePillar === 'copilot' && (
          <div style={{ flex: 1, display: 'flex', height: '100%', overflow: 'hidden' }}>
            <ChatWindow
              inferenceMode={inferenceMode}
              onToggleInferenceMode={setInferenceMode}
            />
          </div>
        )}
      </div>
    </div>
  )
}
