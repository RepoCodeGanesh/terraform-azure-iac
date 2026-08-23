import React from 'react'
import { BookOpen, ExternalLink, ShieldCheck, ArrowRight } from 'lucide-react'
import MarkdownRenderer from './MarkdownRenderer'

export default function CitationCard({ citation, onSelectCitation }) {
  return (
    <div
      onClick={() => onSelectCitation && onSelectCitation(citation)}
      style={{
        background: '#131c2e',
        border: '1px solid rgba(59, 130, 246, 0.35)',
        borderRadius: '8px',
        padding: '10px 14px',
        marginTop: '8px',
        fontSize: '0.85rem',
        cursor: onSelectCitation ? 'pointer' : 'default',
        transition: 'all 0.2s ease'
      }}
      onMouseEnter={(e) => e.currentTarget.style.borderColor = '#3b82f6'}
      onMouseLeave={(e) => e.currentTarget.style.borderColor = 'rgba(59, 130, 246, 0.35)'}
    >
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '6px', color: '#60a5fa', fontWeight: 600, fontSize: '0.78rem' }}>
          <BookOpen size={13} />
          <span>{citation.circular_no || citation.title}</span>
        </div>
        {citation.provenance_hash && (
          <span style={{
            fontSize: '0.65rem',
            color: '#10b981',
            display: 'flex',
            alignItems: 'center',
            gap: '3px'
          }}>
            <ShieldCheck size={11} /> {citation.provenance_hash}
          </span>
        )}
      </div>

      <div style={{ fontWeight: 600, color: '#f1f5f9', marginTop: '4px', fontSize: '0.82rem' }}>
        {citation.clause}
      </div>

      <div style={{ color: '#94a3b8', marginTop: '4px', fontSize: '0.8rem', lineHeight: '1.4' }}>
        <MarkdownRenderer content={citation.text} />
      </div>

      {onSelectCitation && (
        <div style={{
          display: 'flex',
          alignItems: 'center',
          gap: '4px',
          color: '#38bdf8',
          fontSize: '0.72rem',
          fontWeight: 600,
          marginTop: '8px'
        }}>
          <span>Inspect Clause in Split-Screen</span>
          <ArrowRight size={12} />
        </div>
      )}
    </div>
  )
}

