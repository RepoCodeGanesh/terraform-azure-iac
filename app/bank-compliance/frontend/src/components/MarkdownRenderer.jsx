import React from 'react'

/**
 * Lightweight Zero-Dependency Markdown & Table Renderer for BankCompliance AI
 * Supports: Tables (| a | b |), Headings (###), Bold (**text**), Bullet points (* item), Block dividers (---)
 */
export default function MarkdownRenderer({ content }) {
  if (!content) return null

  const lines = content.split('\n')
  const elements = []
  let tableRows = []
  let inTable = false

  const renderInline = (text) => {
    if (!text) return ''
    // Split bold formatting: **bold**
    const parts = text.split(/(\*\*[^*]+\*\*)/g)
    return parts.map((part, i) => {
      if (part.startsWith('**') && part.endsWith('**')) {
        return <strong key={i} style={{ color: '#60a5fa', fontWeight: 600 }}>{part.slice(2, -2)}</strong>
      }
      // Handle backtick code: `code`
      if (part.startsWith('`') && part.endsWith('`')) {
        return <code key={i} style={{ background: '#1f2937', color: '#f59e0b', padding: '2px 6px', borderRadius: '4px', fontSize: '0.85em' }}>{part.slice(1, -1)}</code>
      }
      return part
    })
  }

  const flushTable = (keyPrefix) => {
    if (tableRows.length === 0) return null
    
    // Filter out separator lines (|:---|:---| or |---|---|)
    const validRows = tableRows.filter(row => !row.every(cell => /^:?-+:?$/.test(cell.trim())))
    if (validRows.length === 0) {
      tableRows = []
      inTable = false
      return null
    }

    const header = validRows[0]
    const body = validRows.slice(1)

    const tableEl = (
      <div key={`table-${keyPrefix}`} style={{ overflowX: 'auto', margin: '14px 0' }}>
        <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.85rem', background: '#0d131f', borderRadius: '8px', overflow: 'hidden', border: '1px solid #374151' }}>
          <thead>
            <tr style={{ background: '#1e293b', borderBottom: '2px solid #3b82f6' }}>
              {header.map((col, cIdx) => (
                <th key={cIdx} style={{ padding: '10px 14px', textAlign: 'left', color: '#93c5fd', fontWeight: 600 }}>
                  {renderInline(col.trim())}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {body.map((row, rIdx) => (
              <tr key={rIdx} style={{ borderBottom: '1px solid #1f2937', background: rIdx % 2 === 0 ? 'transparent' : 'rgba(30, 41, 59, 0.4)' }}>
                {row.map((cell, cIdx) => (
                  <td key={cIdx} style={{ padding: '9px 14px', color: '#e2e8f0' }}>
                    {renderInline(cell.trim())}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    )

    tableRows = []
    inTable = false
    return tableEl
  }

  for (let i = 0; i < lines.length; i++) {
    const line = lines[i].trim()

    // 1. Table Row Detection
    if (line.startsWith('|') && line.endsWith('|')) {
      inTable = true
      const cells = line.slice(1, -1).split('|')
      tableRows.push(cells)
      continue
    } else if (inTable) {
      const table = flushTable(i)
      if (table) elements.push(table)
    }

    // 2. Horizontal Rules
    if (line.startsWith('---')) {
      elements.push(<hr key={i} style={{ border: 'none', borderTop: '1px solid #374151', margin: '14px 0' }} />)
      continue
    }

    // 3. Headings
    if (line.startsWith('### ')) {
      elements.push(
        <h3 key={i} style={{ fontSize: '1rem', fontWeight: 700, color: '#f59e0b', margin: '12px 0 6px 0', display: 'flex', alignItems: 'center', gap: '6px' }}>
          {renderInline(line.slice(4))}
        </h3>
      )
      continue
    }
    if (line.startsWith('## ')) {
      elements.push(
        <h2 key={i} style={{ fontSize: '1.1rem', fontWeight: 700, color: '#60a5fa', margin: '14px 0 8px 0' }}>
          {renderInline(line.slice(3))}
        </h2>
      )
      continue
    }
    if (line.startsWith('# ')) {
      elements.push(
        <h1 key={i} style={{ fontSize: '1.2rem', fontWeight: 800, color: '#f3f4f6', margin: '16px 0 10px 0' }}>
          {renderInline(line.slice(2))}
        </h1>
      )
      continue
    }

    // 4. Bullet Points (* or -)
    if (line.startsWith('* ') || line.startsWith('- ')) {
      elements.push(
        <div key={i} style={{ display: 'flex', gap: '8px', margin: '4px 0', paddingLeft: '8px' }}>
          <span style={{ color: '#3b82f6', fontWeight: 700 }}>•</span>
          <span style={{ flex: 1, color: '#e5e7eb' }}>{renderInline(line.slice(2))}</span>
        </div>
      )
      continue
    }

    // 5. Numbered Lists (1., 2., etc.)
    const numMatch = line.match(/^(\d+)\.\s+(.*)/)
    if (numMatch) {
      elements.push(
        <div key={i} style={{ display: 'flex', gap: '8px', margin: '4px 0', paddingLeft: '8px' }}>
          <span style={{ color: '#60a5fa', fontWeight: 600, minWidth: '18px' }}>{numMatch[1]}.</span>
          <span style={{ flex: 1, color: '#e5e7eb' }}>{renderInline(numMatch[2])}</span>
        </div>
      )
      continue
    }

    // 6. Regular Paragraph
    if (line.length > 0) {
      elements.push(
        <p key={i} style={{ margin: '6px 0', color: '#f3f4f6', lineHeight: 1.6 }}>
          {renderInline(line)}
        </p>
      )
    } else {
      elements.push(<div key={i} style={{ height: '6px' }} />)
    }
  }

  if (inTable) {
    const table = flushTable(lines.length)
    if (table) elements.push(table)
  }

  return <div>{elements}</div>
}
