import React from 'react'

/**
 * Enterprise Zero-Dependency Markdown & Statutory Table Renderer
 * Supports: Tables (| a | b |), Headings (###), Bold (**text**), Callouts (> Note),
 * Bullet points (* item), Block dividers (---), and Rupee highlights.
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
        const boldText = part.slice(2, -2)
        // Highlight Rupee figures inside bold text with emerald green
        if (boldText.includes('₹') || boldText.toLowerCase().includes('save') || boldText.toLowerCase().includes('recommended')) {
          return (
            <strong key={i} style={{ color: '#34d399', fontWeight: 600 }}>
              {boldText}
            </strong>
          )
        }
        return (
          <strong key={i} style={{ color: '#f1f5f9', fontWeight: 600 }}>
            {boldText}
          </strong>
        )
      }

      // Handle backtick code: `code`
      if (part.startsWith('`') && part.endsWith('`')) {
        return (
          <code key={i} style={{
            background: 'rgba(99, 102, 241, 0.15)',
            border: '1px solid rgba(99, 102, 241, 0.25)',
            color: '#a5b4fc',
            padding: '2px 6px',
            borderRadius: '4px',
            fontSize: '0.85em',
            fontFamily: 'monospace'
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
      <div key={`table-${keyPrefix}`} style={{
        overflowX: 'auto',
        margin: '14px 0',
        borderRadius: '10px',
        border: '1px solid rgba(255, 255, 255, 0.08)',
        background: 'rgba(11, 15, 25, 0.7)',
        backdropFilter: 'blur(8px)',
      }}>
        <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.82rem' }}>
          <thead>
            <tr style={{ background: 'rgba(30, 41, 59, 0.8)', borderBottom: '1px solid rgba(255, 255, 255, 0.1)' }}>
              {header.map((col, cIdx) => (
                <th key={cIdx} style={{ padding: '10px 14px', textAlign: 'left', color: '#93c5fd', fontWeight: 600 }}>
                  {renderInline(col.trim())}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {body.map((row, rIdx) => (
              <tr key={rIdx} style={{
                borderBottom: '1px solid rgba(255, 255, 255, 0.04)',
                background: rIdx % 2 === 0 ? 'transparent' : 'rgba(255, 255, 255, 0.02)',
              }}>
                {row.map((cell, cIdx) => (
                  <td key={cIdx} style={{ padding: '9px 14px', color: '#cbd5e1' }}>
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
    if (line.startsWith('---') || line === '***') {
      elements.push(
        <hr key={i} style={{ border: 'none', borderTop: '1px solid rgba(255, 255, 255, 0.08)', margin: '14px 0' }} />
      )
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
          color: '#cbd5e1',
          fontSize: '0.85rem'
        }}>
          {renderInline(line.slice(2).trim())}
        </div>
      )
      continue
    }

    // 4. Headings (###, ##, #)
    if (line.startsWith('#### ')) {
      elements.push(
        <h5 key={i} style={{ fontSize: '0.9rem', color: '#e2e8f0', margin: '12px 0 6px 0', fontWeight: 600 }}>
          {renderInline(line.slice(5).trim())}
        </h5>
      )
      continue
    }
    if (line.startsWith('### ')) {
      elements.push(
        <h4 key={i} style={{
          fontSize: '0.98rem',
          color: '#38bdf8',
          margin: '14px 0 8px 0',
          fontWeight: 600,
          display: 'flex',
          alignItems: 'center',
          gap: '6px',
        }}>
          <span style={{ width: '4px', height: '14px', background: '#38bdf8', borderRadius: '2px' }}></span>
          <span>{renderInline(line.slice(4).trim())}</span>
        </h4>
      )
      continue
    }
    if (line.startsWith('## ')) {
      elements.push(
        <h3 key={i} style={{
          fontSize: '1.05rem',
          color: '#f8fafc',
          margin: '16px 0 10px 0',
          fontWeight: 600,
          borderBottom: '1px solid rgba(255, 255, 255, 0.06)',
          paddingBottom: '4px',
        }}>
          {renderInline(line.slice(3).trim())}
        </h3>
      )
      continue
    }
    if (line.startsWith('# ')) {
      elements.push(
        <h2 key={i} style={{ fontSize: '1.15rem', color: '#f8fafc', margin: '18px 0 10px 0', fontWeight: 700 }}>
          {renderInline(line.slice(2).trim())}
        </h2>
      )
      continue
    }

    // 5. Bullet Points (*, -)
    if (line.startsWith('* ') || line.startsWith('- ') || line.startsWith('• ')) {
      elements.push(
        <div key={i} style={{ display: 'flex', gap: '8px', margin: '4px 0', fontSize: '0.88rem', color: '#e2e8f0', lineHeight: '1.5' }}>
          <span style={{ color: '#818cf8' }}>•</span>
          <span>{renderInline(line.replace(/^(\*|-|•)\s+/, ''))}</span>
        </div>
      )
      continue
    }

    // 6. Numbered Lists (1. , 2. )
    const numMatch = line.match(/^(\d+)\.\s+(.*)/)
    if (numMatch) {
      elements.push(
        <div key={i} style={{ display: 'flex', gap: '8px', margin: '4px 0', fontSize: '0.88rem', color: '#e2e8f0', lineHeight: '1.5' }}>
          <span style={{ color: '#818cf8', fontWeight: 600, minWidth: '18px' }}>{numMatch[1]}.</span>
          <span>{renderInline(numMatch[2])}</span>
        </div>
      )
      continue
    }

    // 7. Regular paragraph / text
    if (line.length > 0) {
      elements.push(
        <p key={i} style={{ margin: '6px 0', fontSize: '0.88rem', color: '#cbd5e1', lineHeight: '1.6' }}>
          {renderInline(line)}
        </p>
      )
    } else {
      // Empty line spacing
      elements.push(<div key={i} style={{ height: '6px' }} />)
    }
  }

  // Flush any trailing table
  if (inTable) {
    const table = flushTable('end')
    if (table) elements.push(table)
  }

  return <div className="markdown-body">{elements}</div>
}
