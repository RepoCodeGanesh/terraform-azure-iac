import React, { useState } from 'react'
import { BookOpen, ShieldCheck, ChevronDown, ChevronUp } from 'lucide-react'
import MarkdownRenderer from './MarkdownRenderer'

export default function CitationCard({ citation }) {
  const [isExpanded, setIsExpanded] = useState(false)

  if (!citation) return null

  return (
    <div
      style={{
        borderRadius: '8px',
        padding: '7px 11px',
        fontSize: '0.78rem',
        border: isExpanded ? '1px solid rgba(99, 102, 241, 0.45)' : '1px solid rgba(255, 255, 255, 0.08)',
        background: isExpanded ? 'rgba(15, 23, 42, 0.8)' : 'rgba(15, 23, 42, 0.4)',
        transition: 'all 0.18s ease'
      }}
    >
      <div
        onClick={() => setIsExpanded(prev => !prev)}
        style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          gap: '8px',
          cursor: 'pointer',
          userSelect: 'none'
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: '7px', flexWrap: 'wrap' }}>
          <span style={{
            display: 'inline-flex',
            alignItems: 'center',
            gap: '4px',
            color: '#818cf8',
            fontWeight: 700,
            fontSize: '0.73rem'
          }}>
            <BookOpen size={12} />
            {citation.circular_no || citation.title}
          </span>
          {citation.clause && (
            <span style={{ color: '#e2e8f0', fontWeight: 600, fontSize: '0.75rem' }}>
              • {citation.clause}
            </span>
          )}
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
          {citation.provenance_hash && (
            <span style={{
              fontSize: '0.62rem',
              color: '#34d399',
              background: 'rgba(16, 185, 129, 0.12)',
              border: '1px solid rgba(16, 185, 129, 0.25)',
              padding: '1px 6px',
              borderRadius: '9999px',
              display: 'flex',
              alignItems: 'center',
              gap: '3px',
              fontFamily: 'JetBrains Mono, monospace'
            }}>
              <ShieldCheck size={10} /> sha256:{citation.provenance_hash.slice(0, 8)}...
            </span>
          )}
          <span style={{ color: 'var(--text-muted)', display: 'flex', alignItems: 'center' }}>
            {isExpanded ? <ChevronUp size={13} /> : <ChevronDown size={13} />}
          </span>
        </div>
      </div>

      {isExpanded && citation.text && (
        <div style={{
          marginTop: '8px',
          paddingTop: '8px',
          borderTop: '1px solid rgba(255, 255, 255, 0.08)',
          color: 'var(--text-secondary)',
          fontSize: '0.76rem',
          lineHeight: '1.5'
        }}>
          <MarkdownRenderer content={citation.text} />
        </div>
      )}
    </div>
  )
}
