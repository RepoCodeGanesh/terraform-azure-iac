import React, { useState } from 'react'
import ChatAdvisor from './tabs/ChatAdvisor'
import RegimeComparator from './tabs/RegimeComparator'
import SalaryAnalyser from './tabs/SalaryAnalyser'
import CTCOptimiser from './tabs/CTCOptimiser'
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

      {/* Tab Navigation */}
      <nav className="tab-nav">
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
            className={`tab-btn ${activeTab === 'salary' ? 'active' : ''}`}
            onClick={() => setActiveTab('salary')}
          >
            <span className="tab-icon">📄</span> Salary Analyser
          </button>

          <button
            className={`tab-btn ${activeTab === 'ctc' ? 'active' : ''}`}
            onClick={() => setActiveTab('ctc')}
          >
            <span className="tab-icon">💼</span> CTC Optimiser
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
        {activeTab === 'salary' && <SalaryAnalyser />}
        {activeTab === 'ctc' && <CTCOptimiser />}
        {activeTab === 'filing' && <FilingGuide />}
      </main>
    </div>
  )
}
