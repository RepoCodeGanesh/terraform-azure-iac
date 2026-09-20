import React, { useState, useEffect } from 'react'
import {
  Building2,
  Shield,
  FileCheck,
  MessageSquare,
  Sliders,
  Sparkles,
  Zap
} from 'lucide-react'
import ChatWindow from './components/ChatWindow'
import GenAIOpsDashboard from './components/GenAIOpsDashboard'
import RedlineStudio from './components/RedlineStudio'
import CommandCenter from './components/CommandCenter'
import GovernanceCenter from './components/GovernanceCenter'
import ArchitectureInspectorModal from './components/ArchitectureInspectorModal'

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
  const [isInspectorOpen, setIsInspectorOpen] = useState(false)
  const [inferenceMode, setInferenceMode] = useState('cloud')

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
    <div style={{ display: 'flex', flexDirection: 'column', minHeight: '100vh', height: '100dvh', background: 'var(--bg-dark)' }}>
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

        {/* Center: Enterprise Command Pillars */}
        <nav className="header-nav" style={{ display: 'flex', alignItems: 'center', gap: '5px', flexShrink: 0 }}>
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

          <button
            onClick={() => navigateToPillar('command')}
            style={{
              background: (activePillar === 'command' || activePillar === 'monitoring') ? 'linear-gradient(135deg, rgba(99, 102, 241, 0.3), rgba(139, 92, 246, 0.2))' : 'transparent',
              border: (activePillar === 'command' || activePillar === 'monitoring') ? '1px solid rgba(99, 102, 241, 0.5)' : '1px solid transparent',
              color: (activePillar === 'command' || activePillar === 'monitoring') ? '#c7d2fe' : 'var(--text-muted)',
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
            <span>Command &amp; FinOps</span>
          </button>

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
            <span>Governance &amp; Audit</span>
          </button>

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

        {/* Right: Inference Engine Dropdown */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '6px', flexShrink: 0 }}>
          {inferenceMode === 'sovereign'
            ? <Shield size={13} color="#34d399" />
            : <Zap size={13} color="#818cf8" />}
          <select
            value={inferenceMode}
            onChange={(e) => setInferenceMode(e.target.value)}
            title="Switch inference engine"
            style={{
              background: 'rgba(15, 23, 42, 0.85)',
              border: inferenceMode === 'sovereign'
                ? '1px solid rgba(16, 185, 129, 0.45)'
                : '1px solid rgba(99, 102, 241, 0.4)',
              color: inferenceMode === 'sovereign' ? '#34d399' : '#c7d2fe',
              borderRadius: '7px',
              padding: '4px 8px',
              fontSize: '0.72rem',
              fontWeight: 600,
              cursor: 'pointer',
              outline: 'none',
              fontFamily: 'inherit',
              transition: 'border-color 0.18s ease'
            }}
          >
            <option value="cloud" style={{ background: '#0f172a', color: '#c7d2fe' }}>Multi-Cloud Fleet</option>
            <option value="sovereign" style={{ background: '#0f172a', color: '#34d399' }}>Sovereign SLM</option>
          </select>
        </div>
      </header>

      {/* ── Main Dynamic Workspace View ────────────────────────────────────── */}
      <div className="workspace-container" style={{ display: 'flex', flex: 1, overflow: 'hidden' }}>
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
              onOpenInspector={() => setIsInspectorOpen(true)}
            />
          </div>
        )}
      </div>

      {/* ── Mobile Bottom Navigation Dock (<= 860px) ───────────────────────── */}
      <nav className="mobile-bottom-dock" aria-label="Mobile Navigation">
        <button
          type="button"
          onClick={() => navigateToPillar('copilot')}
          className={`mobile-dock-btn ${activePillar === 'copilot' ? 'active' : ''}`}
        >
          <MessageSquare size={18} />
          <span>Copilot</span>
        </button>

        <button
          type="button"
          onClick={() => navigateToPillar('command')}
          className={`mobile-dock-btn ${activePillar === 'command' ? 'active' : ''}`}
        >
          <Sliders size={18} />
          <span>Command</span>
        </button>

        <button
          type="button"
          onClick={() => navigateToPillar('governance')}
          className={`mobile-dock-btn ${activePillar === 'governance' ? 'active' : ''}`}
        >
          <Shield size={18} />
          <span>Governance</span>
        </button>

        <button
          type="button"
          onClick={() => navigateToPillar('redline')}
          className={`mobile-dock-btn ${activePillar === 'redline' ? 'active' : ''}`}
        >
          <FileCheck size={18} />
          <span>Redliner</span>
        </button>

        <button
          type="button"
          onClick={() => setIsInspectorOpen(true)}
          className="mobile-dock-btn"
          style={{ color: '#818cf8' }}
        >
          <Sparkles size={18} />
          <span>Inspector</span>
        </button>
      </nav>

      {/* ── 2026/2027 Architecture & Learning Inspector Modal ───────────────── */}
      <ArchitectureInspectorModal
        isOpen={isInspectorOpen}
        onClose={() => setIsInspectorOpen(false)}
      />
    </div>
  )
}

