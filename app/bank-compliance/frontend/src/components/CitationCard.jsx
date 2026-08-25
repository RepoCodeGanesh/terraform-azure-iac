import React from 'react'
import { BookOpen, ShieldCheck, ArrowRight, Sparkles } from 'lucide-react'
import MarkdownRenderer from './MarkdownRenderer'

export default function CitationCard({ citation, onSelectCitation }) {
  return (
    <div
      onClick={() => onSelectCitation && onSelectCitation(citation)}
      className="glass-card"
      style={{
        borderRadius: '12px',
        padding: '12px 16px',
        fontSize: '0.85rem',
        cursor: onSelectCitation ? 'pointer' : 'default',
        border: '1px solid rgba(99, 102, 241, 0.25)',
        background: 'rgba(15, 23, 42, 0.65)'
      }}
      onMouseEnter={(e) => {
        e.currentTarget.style.borderColor = 'rgba(99, 102, 241, 0.6)'
        e.currentTarget.style.background = 'rgba(30, 39, 58, 0.75)'
        e.currentTarget.style.boxShadow = '0 0 16px rgba(99, 102, 241, 0.2)'
      }}
      onMouseLeave={(e) => {
        e.currentTarget.style.borderColor = 'rgba(99, 102, 241, 0.25)'
        e.currentTarget.style.background = 'rgba(15, 23, 42, 0.65)'
        e.currentTarget.style.boxShadow = 'none'
      }}
    >
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: '8px', flexWrap: 'wrap' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '6px', color: '#818cf8', fontWeight: 600, fontSize: '0.78rem' }}>
          <BookOpen size={13} />
          <span>{citation.circular_no || citation.title}</span>
        </div>
        {citation.provenance_hash && (
          <span style={{
            fontSize: '0.65rem',
            color: '#34d399',
            background: 'rgba(16, 185, 129, 0.12)',
            border: '1px solid rgba(16, 185, 129, 0.3)',
            padding: '2px 8px',
            borderRadius: '9999px',
            display: 'flex',
            alignItems: 'center',
            gap: '4px',
            fontFamily: 'JetBrains Mono, monospace'
          }}>
            <ShieldCheck size={11} /> sha256:{citation.provenance_hash}
          </span>
        )}
      </div>

      <div style={{ fontWeight: 600, color: '#f8fafc', marginTop: '6px', fontSize: '0.84rem', letterSpacing: '-0.01em' }}>
        {citation.clause}
      </div>

      <div style={{ color: 'var(--text-secondary)', marginTop: '5px', fontSize: '0.8rem', lineHeight: '1.5' }}>
        <MarkdownRenderer content={citation.text} />
      </div>

      {onSelectCitation && (
        <div style={{
          display: 'flex',
          alignItems: 'center',
          gap: '5px',
          color: '#38bdf8',
          fontSize: '0.72rem',
          fontWeight: 600,
          marginTop: '10px'
        }}>
          <span>Inspect Clause in Split-Screen</span>
          <ArrowRight size={11} />
        </div>
      )}
    </div>
  )
}
