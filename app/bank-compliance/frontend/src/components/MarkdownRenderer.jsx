import React from 'react'

/**
 * 2026 Sleek Zero-Dependency Markdown & Statutory Table Renderer
 * Supports: Tables (| a | b |), Headings (###), Bold (**text**), Callouts (> Note), Bullet points (* item), Block dividers (---)
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
        return <strong key={i} style={{ color: '#818cf8', fontWeight: 600 }}>{part.slice(2, -2)}</strong>
      }
      // Handle backtick code: `code`
      if (part.startsWith('`') && part.endsWith('`')) {
        return (
          <code key={i} style={{
            background: 'rgba(99, 102, 241, 0.15)',
            border: '1px solid rgba(99, 102, 241, 0.25)',
            color: '#a5b4fc',
            padding: '2px 6px',
            borderRadius: '5px',
            fontSize: '0.85em',
            fontFamily: 'JetBrains Mono, monospace'
          }}>
            {part.slice(1, -1)}
          </code>
        )
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
      <div key={`table-${keyPrefix}`} style={{ overflowX: 'auto', margin: '14px 0', borderRadius: '10px', border: '1px solid var(--border-subtle)' }}>
        <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.82rem', background: 'rgba(15, 23, 42, 0.6)' }}>
          <thead>
            <tr style={{ background: 'rgba(30, 41, 59, 0.8)', borderBottom: '1px solid var(--border-glass)' }}>
              {header.map((col, cIdx) => (
                <th key={cIdx} style={{ padding: '10px 14px', textAlign: 'left', color: '#c7d2fe', fontWeight: 600 }}>
                  {renderInline(col.trim())}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {body.map((row, rIdx) => (
              <tr key={rIdx} style={{ borderBottom: '1px solid rgba(255, 255, 255, 0.05)', background: rIdx % 2 === 0 ? 'transparent' : 'rgba(255, 255, 255, 0.02)' }}>
                {row.map((cell, cIdx) => (
                  <td key={cIdx} style={{ padding: '9px 14px', color: 'var(--text-secondary)' }}>
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
      elements.push(<hr key={i} style={{ border: 'none', borderTop: '1px solid var(--border-subtle)', margin: '14px 0' }} />)
      continue
    }

    // 3. Blockquotes / Statutory Callouts (> text)
    if (line.startsWith('> ')) {
      elements.push(
        <div key={i} style={{
          background: 'rgba(99, 102, 241, 0.08)',
          borderLeft: '3px solid #6366f1',
          padding: '10px 14px',
          borderRadius: '0 8px 8px 0',
          margin: '10px 0',
          color: '#c7d2fe',
          fontSize: '0.85rem'
        }}>
          {renderInline(line.slice(2))}
        </div>
      )
      continue
    }

    // 4. Headings
    if (line.startsWith('#### ')) {
      elements.push(
        <h4 key={i} style={{ fontSize: '0.88rem', fontWeight: 700, color: '#38bdf8', margin: '12px 0 4px 0' }}>
          {renderInline(line.slice(5))}
        </h4>
      )
      continue
    }
    if (line.startsWith('### ')) {
      elements.push(
        <h3 key={i} style={{ fontSize: '0.95rem', fontWeight: 700, color: '#fbbf24', margin: '14px 0 6px 0' }}>
          {renderInline(line.slice(4))}
        </h3>
      )
      continue
    }
    if (line.startsWith('## ')) {
      elements.push(
        <h2 key={i} style={{ fontSize: '1.05rem', fontWeight: 700, color: '#818cf8', margin: '16px 0 8px 0' }}>
          {renderInline(line.slice(3))}
        </h2>
      )
      continue
    }
    if (line.startsWith('# ')) {
      elements.push(
        <h1 key={i} style={{ fontSize: '1.15rem', fontWeight: 800, color: 'var(--text-main)', margin: '18px 0 10px 0' }}>
          {renderInline(line.slice(2))}
        </h1>
      )
      continue
    }

    // 5. Bullet Points (* or -)
    if (line.startsWith('* ') || line.startsWith('- ') || line.startsWith('• ')) {
      const sliceIdx = line.startsWith('• ') ? 2 : 2
      elements.push(
        <div key={i} style={{ display: 'flex', gap: '8px', margin: '4px 0', paddingLeft: '6px' }}>
          <span style={{ color: '#6366f1', fontWeight: 700 }}>•</span>
          <span style={{ flex: 1, color: 'var(--text-secondary)' }}>{renderInline(line.slice(sliceIdx))}</span>
        </div>
      )
      continue
    }

    // 6. Numbered Lists (1., 2., etc.)
    const numMatch = line.match(/^(\d+)\.\s+(.*)/)
    if (numMatch) {
      elements.push(
        <div key={i} style={{ display: 'flex', gap: '8px', margin: '4px 0', paddingLeft: '6px' }}>
          <span style={{ color: '#818cf8', fontWeight: 600, minWidth: '18px' }}>{numMatch[1]}.</span>
          <span style={{ flex: 1, color: 'var(--text-secondary)' }}>{renderInline(numMatch[2])}</span>
        </div>
      )
      continue
    }

    // 7. Regular Paragraph
    if (line.length > 0) {
      elements.push(
        <p key={i} style={{ margin: '6px 0', color: 'var(--text-main)', lineHeight: 1.6 }}>
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
