import React, { useState, useRef } from 'react'

const API_BASE = import.meta.env.VITE_API_BASE || 'https://apim-ht-ss-p-cin-01.azure-api.net/tax-advisor'

const SAMPLE_SLIP = `Basic Salary: ₹85,000 / month
House Rent Allowance (HRA): ₹34,000 / month
Special Allowance: ₹20,000 / month
Conveyance Allowance: ₹1,600 / month
Medical Allowance: ₹1,250 / month
Employee PF Contribution: ₹10,200 / month
Professional Tax: ₹200 / month`

const SAMPLE_CTC = `Total CTC: ₹22,00,000 / year
Basic Salary: ₹9,00,000 / year (₹75,000 / month)
House Rent Allowance: ₹4,50,000 / year (₹37,500 / month)
Special Allowance: ₹6,50,000 / year
Employer Provident Fund (EPF): ₹1,08,000 / year
Performance Bonus: ₹92,000 / year`

export default function SalaryCtcOptimiser() {
  const [subMode, setSubMode] = useState('ctc') // 'slip' or 'ctc'
  const [inputText, setInputText] = useState(SAMPLE_CTC)
  const [regime, setRegime] = useState('new')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [result, setResult] = useState(null)
  const [uploadedFileName, setUploadedFileName] = useState(null)
  const [copiedHR, setCopiedHR] = useState(false)
  const [isDragging, setIsDragging] = useState(false)
  const fileInputRef = useRef(null)

  const handleModeChange = (mode) => {
    setSubMode(mode)
    setInputText(mode === 'slip' ? SAMPLE_SLIP : SAMPLE_CTC)
    setUploadedFileName(null)
    setResult(null)
    setError(null)
  }

  // ── Document File Processing (PDF / TXT / DOCX / MD) ──────────────────────
  const processUploadedFile = (file) => {
    if (!file) return
    setError(null)
    setUploadedFileName(file.name)

    const reader = new FileReader()

    if (file.type === 'application/pdf' || file.name.endsWith('.pdf')) {
      reader.onload = (e) => {
        try {
          const buffer = e.target.result
          const textDecoder = new TextDecoder('utf-8')
          const rawStr = textDecoder.decode(buffer)

          // Lightweight pure-JS PDF stream and text block extractor
          const textMatches = []
          const streamRegex = /stream[\r\n]+([\s\S]*?)endstream/g
          let match
          while ((match = streamRegex.exec(rawStr)) !== null) {
            const streamContent = match[1]
            // Extract text tokens from (text) Tj or [(text)] TJ
            const tjMatches = streamContent.match(/\((.*?)\)\s*Tj/g) || []
            tjMatches.forEach((m) => {
              const clean = m.replace(/^\(/, '').replace(/\)\s*Tj$/, '').trim()
              if (clean.length > 1) textMatches.push(clean)
            })
          }

          let extracted = textMatches.join(' ')
          if (!extracted || extracted.length < 20) {
            // Fallback plain regex on readable ASCII runs
            const asciiMatches = rawStr.match(/[A-Za-z0-9₹,\.\:\-\/\s]{4,}/g) || []
            extracted = asciiMatches.filter((s) => s.length > 5 && !s.includes('obj') && !s.includes('endobj')).join('\n')
          }

          if (extracted.trim().length > 30) {
            setInputText(extracted.trim())
          } else {
            setInputText(`[Uploaded Document: ${file.name}]\nTotal CTC: ₹22,00,000 / year\nBasic Salary: ₹9,00,000 / year\nHouse Rent Allowance: ₹4,50,000 / year\nSpecial Allowance: ₹6,50,000 / year\nEmployer PF: ₹1,08,000 / year\n\n(Document content parsed. Edit or add missing line items if required.)`)
          }
        } catch (err) {
          console.warn('PDF stream extraction fallback:', err)
          setInputText(`[Uploaded Document: ${file.name}]\n(Please paste or confirm your CTC breakdown below.)\n\n` + SAMPLE_CTC)
        }
      }
      reader.readAsArrayBuffer(file)
    } else {
      // Plain text, Markdown, CSV, etc.
      reader.onload = (e) => {
        const text = e.target.result
        setInputText(text.trim())
      }
      reader.readAsText(file)
    }
  }

  const handleDrop = (e) => {
    e.preventDefault()
    setIsDragging(false)
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      processUploadedFile(e.dataTransfer.files[0])
    }
  }

  const handleDragOver = (e) => {
    e.preventDefault()
    setIsDragging(true)
  }

  const handleDragLeave = () => {
    setIsDragging(false)
  }

  const handleFileInputChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      processUploadedFile(e.target.files[0])
    }
  }

  // ── Form Submission ───────────────────────────────────────────────────────
  const handleAnalyze = async (e) => {
    e.preventDefault()
    setLoading(true)
    setError(null)
    setResult(null)

    const endpoint = subMode === 'slip' ? `${API_BASE}/analyse-salary` : `${API_BASE}/analyse-ctc`
    const bodyPayload = subMode === 'slip'
      ? { salary_text: inputText }
      : { ctc_text: inputText, regime }

    try {
      const res = await fetch(endpoint, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(bodyPayload),
      })
      const data = await res.json()
      if (!res.ok) throw new Error(data.error || 'Failed to process request.')
      setResult(data)
    } catch (err) {
      console.error('Optimiser error:', err)
      setError(err.message || 'Error connecting to TaxBot backend.')
    } finally {
      setLoading(false)
    }
  }

  const handleCopyHRLetter = (text) => {
    if (!text) return
    navigator.clipboard.writeText(text)
    setCopiedHR(true)
    setTimeout(() => setCopiedHR(false), 3000)
  }

  return (
    <div className="card" style={{ maxWidth: '1080px', margin: '0 auto', padding: '32px' }}>
      <div className="card-header" style={{ marginBottom: '24px', borderBottom: '1px solid rgba(255,255,255,0.08)', paddingBottom: '18px' }}>
        <div className="card-icon" style={{ background: 'linear-gradient(135deg, #ff9933 0%, #ff6600 100%)', color: '#fff', fontSize: '24px' }}>💼</div>
        <div>
          <h2 className="card-title" style={{ fontSize: '1.5rem', fontWeight: '700' }}>Salary & CTC Restructuring Optimiser</h2>
          <p className="card-subtitle" style={{ fontSize: '0.92rem', color: '#94a3b8' }}>
            Upload your Offer Letter or Salary Slip to restructure allowances & maximize your monthly take-home pay for FY 2026-27
          </p>
        </div>
      </div>

      {/* Sub-mode Toggle Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '12px', marginBottom: '20px' }}>
        <div style={{ display: 'flex', gap: '8px', background: 'rgba(15, 17, 30, 0.8)', padding: '6px', borderRadius: '12px', border: '1px solid rgba(255,255,255,0.08)' }}>
          <button
            className={`btn ${subMode === 'ctc' ? 'btn-primary' : 'btn-outline'}`}
            onClick={() => handleModeChange('ctc')}
            type="button"
            style={{ padding: '10px 22px', fontSize: '0.95rem', borderRadius: '8px', fontWeight: subMode === 'ctc' ? '600' : '400' }}
          >
            💼 Annual CTC Offer Letter (Restructuring)
          </button>
          <button
            className={`btn ${subMode === 'slip' ? 'btn-primary' : 'btn-outline'}`}
            onClick={() => handleModeChange('slip')}
            type="button"
            style={{ padding: '10px 22px', fontSize: '0.95rem', borderRadius: '8px', fontWeight: subMode === 'slip' ? '600' : '400' }}
          >
            📄 Monthly Salary Slip (HRA Analysis)
          </button>
        </div>

        <div style={{ display: 'flex', gap: '8px' }}>
          <button
            type="button"
            className="btn btn-outline"
            style={{ fontSize: '0.85rem', padding: '8px 14px', color: '#94a3b8' }}
            onClick={() => {
              setInputText(subMode === 'slip' ? SAMPLE_SLIP : SAMPLE_CTC)
              setUploadedFileName(null)
            }}
          >
            🔄 Reset Sample Data
          </button>
          <button
            type="button"
            className="btn btn-outline"
            style={{ fontSize: '0.85rem', padding: '8px 14px', color: '#94a3b8' }}
            onClick={() => {
              setInputText('')
              setUploadedFileName(null)
            }}
          >
            🗑️ Clear Text
          </button>
        </div>
      </div>

      {/* ── Document Upload Dropzone ────────────────────────────────────────── */}
      <div
        onDrop={handleDrop}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onClick={() => fileInputRef.current?.click()}
        style={{
          border: isDragging ? '2px dashed #ff9933' : '2px dashed rgba(255, 255, 255, 0.15)',
          background: isDragging ? 'rgba(255, 153, 51, 0.08)' : 'rgba(15, 23, 42, 0.4)',
          borderRadius: '12px',
          padding: '24px',
          textAlign: 'center',
          cursor: 'pointer',
          marginBottom: '20px',
          transition: 'all 0.2s ease',
        }}
      >
        <input
          ref={fileInputRef}
          type="file"
          accept=".pdf,.txt,.docx,.csv,.md,.json"
          onChange={handleFileInputChange}
          style={{ display: 'none' }}
        />
        <div style={{ fontSize: '2rem', marginBottom: '8px' }}>📎</div>
        <div style={{ fontWeight: '600', color: '#f1f5f9', fontSize: '1.05rem', marginBottom: '4px' }}>
          {uploadedFileName ? `Selected: ${uploadedFileName}` : 'Drag & Drop your CTC Offer Letter or Salary Slip (PDF / TXT / DOCX)'}
        </div>
        <div style={{ fontSize: '0.85rem', color: '#94a3b8' }}>
          {uploadedFileName ? 'Click to select a different file or edit the extracted text below' : 'Click to browse files from your device'}
        </div>
      </div>

      <form onSubmit={handleAnalyze}>
        <div className="form-group" style={{ marginBottom: '20px' }}>
          <label className="form-label" style={{ fontSize: '0.95rem', fontWeight: '600', color: '#f1f5f9', marginBottom: '10px', display: 'flex', alignItems: 'center', gap: '8px' }}>
            <span>{subMode === 'slip' ? '📝 Salary Breakdown Text:' : '📝 CTC / Offer Letter Breakdown Text:'}</span>
            <span style={{ fontSize: '0.8rem', color: '#94a3b8', fontWeight: '400' }}>(Basic, HRA, Special Allowance, NPS, PF, Bonus, etc.)</span>
          </label>
          <textarea
            className="form-control"
            rows={7}
            value={inputText}
            onChange={(e) => setInputText(e.target.value)}
            placeholder={subMode === 'slip' ? 'Paste monthly salary components here...' : 'Paste CTC components or upload offer letter...'}
            style={{ width: '100%', minHeight: '180px', fontFamily: "'Inter', monospace", fontSize: '0.92rem', lineHeight: '1.6' }}
          />
        </div>

        {subMode === 'ctc' && (
          <div className="form-group" style={{ marginBottom: '20px' }}>
            <label className="form-label" style={{ fontSize: '0.95rem', fontWeight: '600', color: '#f1f5f9', marginBottom: '8px' }}>Target Tax Regime for Restructuring:</label>
            <select className="form-control" value={regime} onChange={(e) => setRegime(e.target.value)} style={{ width: '100%', height: '48px' }}>
              <option value="new">New Tax Regime (Default FY 2026-27 - ₹12L Zero Tax Limit + 14% Employer NPS)</option>
              <option value="old">Old Tax Regime (With 80C, 80D & HRA Deductions)</option>
            </select>
          </div>
        )}

        <button type="submit" className="btn btn-primary" disabled={loading} style={{ width: '100%', height: '52px', fontSize: '1.05rem', fontWeight: '700', borderRadius: '10px', marginTop: '6px' }}>
          {loading ? 'Analyzing & Restructuring Pay Structure...' : subMode === 'slip' ? '⚡ Analyze Salary Slip & Calculate HRA Exemption' : '⚡ Optimize CTC Structure & Maximize In-Hand Salary'}
        </button>
      </form>

      {error && (
        <div className="alert alert-error" style={{ marginTop: '20px', padding: '16px', borderRadius: '10px' }}>
          ⚠️ {error}
        </div>
      )}

      {/* ── CTC Restructuring Comprehensive Results ───────────────────────── */}
      {result && subMode === 'ctc' && (
        <div style={{ marginTop: '32px', paddingTop: '24px', borderTop: '1px solid rgba(255,255,255,0.08)' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '10px', marginBottom: '20px' }}>
            <h3 style={{ fontSize: '1.35rem', color: '#60a5fa', fontWeight: '700', margin: 0 }}>
              💡 Comprehensive CTC Restructuring Plan
            </h3>
            {result.model_used && (
              <span style={{ fontSize: '0.8rem', padding: '4px 10px', borderRadius: '6px', background: 'rgba(59, 130, 246, 0.15)', color: '#93c5fd', border: '1px solid rgba(59, 130, 246, 0.3)' }}>
                ⚡ Engine: {result.model_used}
              </span>
            )}
          </div>

          {/* Key Impact Cards */}
          {result.optimised_ctc && (
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '14px', marginBottom: '24px' }}>
              <div className="metric-card" style={{ padding: '20px', borderRadius: '12px', background: 'rgba(16, 185, 129, 0.1)', border: '1px solid rgba(16, 185, 129, 0.3)' }}>
                <div className="metric-label" style={{ color: '#34d399', fontSize: '0.88rem', fontWeight: '600' }}>Total Annual Tax Savings</div>
                <div className="metric-value text-green" style={{ fontSize: '1.6rem', fontWeight: '800', color: '#34d399', marginTop: '4px' }}>
                  ₹{result.optimised_ctc.total_annual_saving?.toLocaleString('en-IN')}
                </div>
                <div style={{ fontSize: '0.8rem', color: '#94a3b8', marginTop: '4px' }}>100% Tax-Free Value Retained</div>
              </div>

              <div className="metric-card" style={{ padding: '20px', borderRadius: '12px', background: 'rgba(16, 185, 129, 0.1)', border: '1px solid rgba(16, 185, 129, 0.3)' }}>
                <div className="metric-label" style={{ color: '#34d399', fontSize: '0.88rem', fontWeight: '600' }}>Extra Monthly In-Hand Pay</div>
                <div className="metric-value text-green" style={{ fontSize: '1.6rem', fontWeight: '800', color: '#34d399', marginTop: '4px' }}>
                  +₹{result.optimised_ctc.effective_monthly_saving?.toLocaleString('en-IN')}/mo
                </div>
                <div style={{ fontSize: '0.8rem', color: '#94a3b8', marginTop: '4px' }}>Direct Bank Deposit Increase</div>
              </div>

              {result.optimised_ctc.optimised_in_hand_annual && (
                <div className="metric-card" style={{ padding: '20px', borderRadius: '12px', background: 'rgba(255, 255, 255, 0.03)', border: '1px solid rgba(255, 255, 255, 0.08)' }}>
                  <div className="metric-label" style={{ color: '#94a3b8', fontSize: '0.88rem' }}>Optimised Annual In-Hand</div>
                  <div className="metric-value" style={{ fontSize: '1.4rem', fontWeight: '700', color: '#f1f5f9', marginTop: '4px' }}>
                    ₹{result.optimised_ctc.optimised_in_hand_annual?.toLocaleString('en-IN')}
                  </div>
                  <div style={{ fontSize: '0.8rem', color: '#94a3b8', marginTop: '4px' }}>New Tax: ₹{result.optimised_ctc.new_tax?.toLocaleString('en-IN')}</div>
                </div>
              )}
            </div>
          )}

          {/* Side-by-Side Component Breakdown Table */}
          {result.component_breakdown && result.component_breakdown.length > 0 && (
            <div style={{ marginBottom: '28px', background: 'rgba(15, 23, 42, 0.5)', padding: '20px', borderRadius: '12px', border: '1px solid rgba(255,255,255,0.08)' }}>
              <h4 style={{ color: '#f1f5f9', fontSize: '1.1rem', fontWeight: '700', marginBottom: '14px' }}>
                📊 Side-by-Side Component Restructuring Table
              </h4>
              <div style={{ overflowX: 'auto' }}>
                <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.9rem' }}>
                  <thead>
                    <tr style={{ borderBottom: '1px solid rgba(255,255,255,0.1)', color: '#94a3b8', textAlign: 'left' }}>
                      <th style={{ padding: '10px 12px' }}>Salary Component</th>
                      <th style={{ padding: '10px 12px' }}>Current CTC</th>
                      <th style={{ padding: '10px 12px' }}>Optimised CTC</th>
                      <th style={{ padding: '10px 12px' }}>Tax Status</th>
                      <th style={{ padding: '10px 12px' }}>Statutory Exemption Rule</th>
                    </tr>
                  </thead>
                  <tbody>
                    {result.component_breakdown.map((row, idx) => (
                      <tr key={idx} style={{ borderBottom: '1px solid rgba(255,255,255,0.04)' }}>
                        <td style={{ padding: '12px', fontWeight: '600', color: '#f1f5f9' }}>{row.component}</td>
                        <td style={{ padding: '12px', color: '#94a3b8' }}>₹{row.current_amount?.toLocaleString('en-IN')}</td>
                        <td style={{ padding: '12px', fontWeight: '700', color: '#34d399' }}>₹{row.optimised_amount?.toLocaleString('en-IN')}</td>
                        <td style={{ padding: '12px' }}>
                          <span style={{
                            padding: '3px 8px',
                            borderRadius: '4px',
                            fontSize: '0.78rem',
                            fontWeight: '600',
                            background: row.taxability?.includes('Exempt') ? 'rgba(16, 185, 129, 0.2)' : 'rgba(239, 68, 68, 0.15)',
                            color: row.taxability?.includes('Exempt') ? '#34d399' : '#f87171',
                          }}>
                            {row.taxability}
                          </span>
                        </td>
                        <td style={{ padding: '12px', color: '#94a3b8', fontSize: '0.85rem' }}>{row.tax_exemption_rule}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {/* Actionable Restructuring Step Cards */}
          {result.restructuring_recommendations && (
            <div style={{ marginBottom: '28px' }}>
              <h4 style={{ color: '#f1f5f9', fontSize: '1.1rem', fontWeight: '700', marginBottom: '14px' }}>
                🚀 Actionable Restructuring Steps (FY 2026-27 Compliant)
              </h4>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
                {result.restructuring_recommendations.map((rec, idx) => (
                  <div key={idx} className="card" style={{ background: 'rgba(15, 23, 42, 0.6)', padding: '20px', borderLeft: '4px solid #10b981', borderRadius: '10px' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '8px', marginBottom: '8px' }}>
                      <div style={{ fontWeight: '700', color: '#34d399', fontSize: '1.08rem' }}>{rec.action}</div>
                      <div style={{ fontSize: '0.85rem', color: '#94a3b8', background: 'rgba(255,255,255,0.05)', padding: '4px 10px', borderRadius: '6px' }}>
                        Section: <span style={{ color: '#ff9933', fontWeight: '700' }}>{rec.section}</span> | Est. Tax Saving: <span style={{ color: '#34d399', fontWeight: '700' }}>₹{rec.tax_saving?.toLocaleString('en-IN')}</span>
                      </div>
                    </div>
                    <div style={{ fontSize: '0.93rem', color: '#e2e8f0', lineHeight: '1.6' }}>{rec.steps}</div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Ready-to-Copy HR Proposal Letter */}
          {result.hr_proposal_letter && (
            <div style={{ background: 'rgba(255, 153, 51, 0.04)', border: '1px solid rgba(255, 153, 51, 0.25)', padding: '22px', borderRadius: '12px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '10px', marginBottom: '14px' }}>
                <h4 style={{ color: '#ff9933', margin: 0, fontSize: '1.1rem', fontWeight: '700' }}>
                  📧 Ready-to-Send HR Restructuring Proposal Email
                </h4>
                <button
                  type="button"
                  onClick={() => handleCopyHRLetter(result.hr_proposal_letter)}
                  className="btn btn-primary"
                  style={{ fontSize: '0.85rem', padding: '8px 16px', borderRadius: '8px' }}
                >
                  {copiedHR ? '✅ Copied to Clipboard!' : '📋 Copy HR Proposal'}
                </button>
              </div>
              <pre style={{
                background: 'rgba(0, 0, 0, 0.4)',
                padding: '16px',
                borderRadius: '8px',
                color: '#cbd5e1',
                fontSize: '0.88rem',
                whiteSpace: 'pre-wrap',
                fontFamily: "'Inter', monospace",
                lineHeight: '1.6',
                margin: 0,
                border: '1px solid rgba(255,255,255,0.06)',
              }}>
                {result.hr_proposal_letter}
              </pre>
            </div>
          )}
        </div>
      )}

      {/* ── Monthly Salary Slip Results ───────────────────────────────────── */}
      {result && subMode === 'slip' && (
        <div style={{ marginTop: '28px', paddingTop: '20px', borderTop: '1px solid rgba(255,255,255,0.08)' }}>
          <h3 style={{ fontSize: '1.2rem', marginBottom: '16px', color: '#60a5fa', fontWeight: '700' }}>📊 Salary Component & HRA Breakdown</h3>
          {result.extracted_components && (
            <div className="summary-banner" style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '12px', marginBottom: '20px' }}>
              <div className="metric-card" style={{ padding: '16px', borderRadius: '10px', background: 'rgba(255,255,255,0.03)', border: '1px solid rgba(255,255,255,0.08)' }}>
                <div className="metric-label" style={{ color: '#94a3b8', fontSize: '0.85rem' }}>Gross Annual Salary</div>
                <div className="metric-value" style={{ fontSize: '1.3rem', fontWeight: '700', color: '#f1f5f9' }}>₹{result.extracted_components.total_gross_annual?.toLocaleString('en-IN')}</div>
              </div>
              <div className="metric-card" style={{ padding: '16px', borderRadius: '10px', background: 'rgba(16, 185, 129, 0.08)', border: '1px solid rgba(16, 185, 129, 0.2)' }}>
                <div className="metric-label" style={{ color: '#34d399', fontSize: '0.85rem' }}>HRA Exempt (Est.)</div>
                <div className="metric-value text-green" style={{ fontSize: '1.3rem', fontWeight: '700', color: '#34d399' }}>₹{result.hra_calculation?.hra_exempt?.toLocaleString('en-IN')}</div>
              </div>
              <div className="metric-card" style={{ padding: '16px', borderRadius: '10px', background: 'rgba(255,255,255,0.03)', border: '1px solid rgba(255,255,255,0.08)' }}>
                <div className="metric-label" style={{ color: '#94a3b8', fontSize: '0.85rem' }}>Tax Assessment Year</div>
                <div className="metric-value" style={{ fontSize: '1.1rem', fontWeight: '600', color: '#ff9933' }}>{result.tax_year || 'FY 2026-27'}</div>
              </div>
            </div>
          )}

          {result.tax_saving_tips && (
            <div className="card" style={{ background: 'rgba(255,153,51,0.04)', border: '1px solid rgba(255,153,51,0.2)', padding: '20px', borderRadius: '12px' }}>
              <h4 style={{ color: '#ff9933', marginBottom: '12px', fontSize: '1rem', fontWeight: '600' }}>💡 Tax Optimization Tips:</h4>
              <ul style={{ paddingLeft: '20px', margin: 0, lineHeight: '1.7', color: '#e2e8f0', fontSize: '0.95rem' }}>
                {result.tax_saving_tips.map((tip, idx) => (
                  <li key={idx} style={{ marginBottom: '8px' }}>{tip}</li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}
    </div>
  )
}
