import React from 'react'
import { BookOpen } from 'lucide-react'
import MarkdownRenderer from './MarkdownRenderer'

export default function CitationCard({ citation }) {
  return (
    <div style={{
      background: '#1f2937',
      border: '1px solid rgba(245, 158, 11, 0.3)',
      borderRadius: '8px',
      padding: '10px 14px',
      marginTop: '8px',
      fontSize: '0.85rem'
    }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: '6px', color: '#f59e0b', fontWeight: 600 }}>
        <BookOpen size={14} />
        <span>{citation.circular_no}</span>
      </div>
      <div style={{ fontWeight: 500, color: '#e5e7eb', marginTop: '4px' }}>
        {citation.clause}
      </div>
      <div style={{ color: '#9ca3af', marginTop: '4px', fontSize: '0.85rem', lineHeight: '1.4' }}>
        <MarkdownRenderer content={citation.text} />
      </div>
    </div>
  )
}
