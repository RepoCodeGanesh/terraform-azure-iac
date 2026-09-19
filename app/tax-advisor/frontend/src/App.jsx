import React, { useState } from 'react'
import ChatAdvisor from './tabs/ChatAdvisor'
import RegimeComparator from './tabs/RegimeComparator'
import SalaryCtcOptimiser from './tabs/SalaryCtcOptimiser'
import FilingGuide from './tabs/FilingGuide'

export default function App() {
  const [activeTab, setActiveTab] = useState('chat')

  return (
    <div className="app-shell">
      {/* Header */}
      <header className="header">
        <div className="header-inner">
          <div className="logo">
            <div className="logo-icon">🇮🇳</div>
            <div className="logo-text">
              TaxBot <span>India</span>
            </div>
            <span className="header-badge">FY 2026-27</span>
          </div>

          <div style={{ fontSize: '12px', color: 'var(--text-muted)' }}>
            Budget 2025 Compliant • Azure AI Engine
          </div>
        </div>
      </header>

      {/* Tab Navigation (Desktop) */}
      <nav className="tab-nav desktop-tab-nav">
        <div className="tab-nav-inner">
          <button
            className={`tab-btn ${activeTab === 'chat' ? 'active' : ''}`}
            onClick={() => setActiveTab('chat')}
          >
            <span className="tab-icon">💬</span> AI Tax Advisor
          </button>

          <button
            className={`tab-btn ${activeTab === 'comparator' ? 'active' : ''}`}
            onClick={() => setActiveTab('comparator')}
          >
            <span className="tab-icon">⚖️</span> Regime Comparator
          </button>

          <button
            className={`tab-btn ${activeTab === 'optimiser' ? 'active' : ''}`}
            onClick={() => setActiveTab('optimiser')}
          >
            <span className="tab-icon">💼</span> Salary & CTC Optimiser
          </button>

          <button
            className={`tab-btn ${activeTab === 'filing' ? 'active' : ''}`}
            onClick={() => setActiveTab('filing')}
          >
            <span className="tab-icon">📁</span> Filing Guide
          </button>
        </div>
      </nav>

      {/* Main Content View */}
      <main className="main-content">
        {activeTab === 'chat' && <ChatAdvisor />}
        {activeTab === 'comparator' && <RegimeComparator />}
        {activeTab === 'optimiser' && <SalaryCtcOptimiser />}
        {activeTab === 'filing' && <FilingGuide />}
      </main>

      {/* Mobile Bottom Navigation Dock (Visible on <= 768px) */}
      <nav className="mobile-bottom-nav" aria-label="Mobile Navigation">
        <button
          className={`mobile-nav-btn ${activeTab === 'chat' ? 'active' : ''}`}
          onClick={() => setActiveTab('chat')}
        >
          <span className="mobile-nav-icon">💬</span>
          <span className="mobile-nav-label">Advisor</span>
        </button>

        <button
          className={`mobile-nav-btn ${activeTab === 'comparator' ? 'active' : ''}`}
          onClick={() => setActiveTab('comparator')}
        >
          <span className="mobile-nav-icon">⚖️</span>
          <span className="mobile-nav-label">Compare</span>
        </button>

        <button
          className={`mobile-nav-btn ${activeTab === 'optimiser' ? 'active' : ''}`}
          onClick={() => setActiveTab('optimiser')}
        >
          <span className="mobile-nav-icon">💼</span>
          <span className="mobile-nav-label">CTC Restruct</span>
        </button>

        <button
          className={`mobile-nav-btn ${activeTab === 'filing' ? 'active' : ''}`}
          onClick={() => setActiveTab('filing')}
        >
          <span className="mobile-nav-icon">📁</span>
          <span className="mobile-nav-label">Filing Guide</span>
        </button>
      </nav>
    </div>
  )
}
