import React, { useState } from 'react'
import { Shield, Building2, BookOpen, ExternalLink } from 'lucide-react'
import ChatWindow from './components/ChatWindow'

export default function App() {
  const [selectedCircular, setSelectedCircular] = useState('All')

  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: '100vh', background: '#090d16' }}>
      {/* Header */}
      <header style={{
        background: '#111827',
        borderBottom: '1px solid #374151',
        padding: '12px 24px',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <div style={{ background: '#1e3a8a', padding: '8px', borderRadius: '8px', display: 'flex', alignItems: 'center' }}>
            <Building2 size={24} color="#60a5fa" />
          </div>
          <div>
            <h1 style={{ fontSize: '1.2rem', fontWeight: 700, color: '#f3f4f6', letterSpacing: '-0.02em' }}>
              BankCompliance AI
            </h1>
            <p style={{ fontSize: '0.75rem', color: '#9ca3af' }}>
              RBI Master Directions & Regulatory Legal Copilot â€¢ Hosted on AKS
            </p>
          </div>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <span style={{
            background: 'rgba(16, 185, 129, 0.15)',
            border: '1px solid #10b981',
            color: '#10b981',
            fontSize: '0.75rem',
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
            style={{ color: '#9ca3af', textDecoration: 'none', fontSize: '0.85rem', display: 'flex', alignItems: 'center', gap: '4px' }}
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
          width: '280px',
          background: '#0d131f',
          borderRight: '1px solid #374151',
          padding: '16px',
          display: 'flex',
          flexDirection: 'column',
          gap: '12px'
        }}>
          <div style={{ fontSize: '0.75rem', fontWeight: 700, color: '#9ca3af', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
            Indexed RBI Master Directions
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
            {[
              "All Master Directions",
              "KYC & V-CIP (2016-2026)",
              "IT Governance & Localization",
              "IT Outsourcing & Vendor Risk",
              "Digital Payment Security",
              "Credit Card Conduct (2025)"
            ].map((c, i) => (
              <button
                key={i}
                onClick={() => setSelectedCircular(c)}
                style={{
                  textAlign: 'left',
                  background: selectedCircular === c ? '#1f2937' : 'transparent',
                  border: selectedCircular === c ? '1px solid #3b82f6' : '1px solid transparent',
                  borderRadius: '6px',
                  padding: '8px 12px',
                  color: selectedCircular === c ? '#60a5fa' : '#9ca3af',
                  fontSize: '0.85rem',
                  cursor: 'pointer',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '8px'
                }}
              >
                <BookOpen size={14} />
                <span>{c}</span>
              </button>
            ))}
          </div>
          <div style={{ marginTop: 'auto', background: '#111827', padding: '12px', borderRadius: '8px', border: '1px solid #1f2937' }}>
            <div style={{ fontSize: '0.75rem', fontWeight: 600, color: '#f59e0b' }}>Cluster FinOps State</div>
            <div style={{ fontSize: '0.7rem', color: '#9ca3af', marginTop: '4px' }}>
              AKS Free Tier â€¢ Ephemeral OS â€¢ 4GB CSI Managed Disk
            </div>
          </div>
        </aside>

        {/* Chat Area */}
        <ChatWindow selectedCircular={selectedCircular} />
      </div>
    </div>
  )
}
