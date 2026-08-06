import React, { useState } from 'react'

const API_BASE = 'https://func-ht-taxb-p-cin-01.azurewebsites.net/api'

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
  const [subMode, setSubMode] = useState('slip') // 'slip' or 'ctc'
  const [inputText, setInputText] = useState(SAMPLE_SLIP)
  const [regime, setRegime] = useState('new')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [result, setResult] = useState(null)

  const handleModeChange = (mode) => {
    setSubMode(mode)
    setInputText(mode === 'slip' ? SAMPLE_SLIP : SAMPLE_CTC)
    setResult(null)
    setError(null)
  }

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

  return (
    <div className="card">
      <div className="card-header" style={{ marginBottom: '16px' }}>
        <div className="card-icon">💼</div>
        <div>
          <h2 className="card-title">Salary & CTC Optimiser</h2>
          <p className="card-subtitle">Analyze salary slips or CTC offer letters to maximize your net take-home pay</p>
        </div>
      </div>

      {/* Sub-mode Toggle */}
      <div style={{ display: 'flex', gap: '8px', marginBottom: '20px', background: 'rgba(255,255,255,0.03)', padding: '6px', borderRadius: '12px', width: 'fit-content' }}>
        <button
          className={`btn ${subMode === 'slip' ? 'btn-primary' : 'btn-outline'}`}
          onClick={() => handleModeChange('slip')}
          type="button"
          style={{ padding: '8px 16px', fontSize: '0.9rem' }}
        >
          📄 Monthly Salary Slip
        </button>
        <button
          className={`btn ${subMode === 'ctc' ? 'btn-primary' : 'btn-outline'}`}
          onClick={() => handleModeChange('ctc')}
          type="button"
          style={{ padding: '8px 16px', fontSize: '0.9rem' }}
        >
          💼 Annual CTC Offer Letter
        </button>
      </div>

      <form onSubmit={handleAnalyze}>
        <div className="form-group" style={{ marginBottom: '16px' }}>
          <label className="form-label">
            {subMode === 'slip' ? 'Paste Salary Slip Breakdown:' : 'Paste CTC / Offer Letter Breakdown:'}
          </label>
          <textarea
            className="form-control"
            rows={7}
            value={inputText}
            onChange={(e) => setInputText(e.target.value)}
            placeholder={subMode === 'slip' ? 'Paste salary breakdown...' : 'Paste CTC breakdown...'}
          />
        </div>

        {subMode === 'ctc' && (
          <div className="form-group" style={{ marginBottom: '16px' }}>
            <label className="form-label">Target Tax Regime:</label>
            <select className="form-control" value={regime} onChange={(e) => setRegime(e.target.value)}>
              <option value="new">New Tax Regime (Default FY 2026-27)</option>
              <option value="old">Old Tax Regime (With Deductions)</option>
            </select>
          </div>
        )}

        <button type="submit" className="btn btn-primary" disabled={loading} style={{ width: '100%' }}>
          {loading ? 'Analyzing Pay Structure...' : subMode === 'slip' ? '⚡ Analyze Salary Slip' : '⚡ Optimize CTC Structure'}
        </button>
      </form>

      {error && (
        <div className="alert alert-error" style={{ marginTop: '16px' }}>
          ⚠️ {error}
        </div>
      )}

      {result && subMode === 'slip' && (
        <div style={{ marginTop: '24px' }}>
          <h3 style={{ fontSize: '1.1rem', marginBottom: '12px', color: '#60a5fa' }}>📊 Salary Component Analysis</h3>
          {result.extracted_components && (
            <div className="summary-banner" style={{ gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))', marginBottom: '16px' }}>
              <div className="metric-card">
                <div className="metric-label">Gross Annual Salary</div>
                <div className="metric-value">₹{result.extracted_components.total_gross_annual?.toLocaleString('en-IN')}</div>
              </div>
              <div className="metric-card">
                <div className="metric-label">HRA Exempt (Est.)</div>
                <div className="metric-value text-green">₹{result.hra_calculation?.hra_exempt?.toLocaleString('en-IN')}</div>
              </div>
              <div className="metric-card">
                <div className="metric-label">Tax Year</div>
                <div className="metric-value">{result.tax_year || 'FY 2026-27'}</div>
              </div>
            </div>
          )}

          {result.tax_saving_tips && (
            <div className="card" style={{ background: 'rgba(255,255,255,0.02)', padding: '16px' }}>
              <h4 style={{ color: '#fbbf24', marginBottom: '8px' }}>💡 Tax Optimization Tips:</h4>
              <ul style={{ paddingLeft: '20px', margin: 0, lineHeight: 1.6 }}>
                {result.tax_saving_tips.map((tip, idx) => (
                  <li key={idx} style={{ marginBottom: '6px' }}>{tip}</li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}

      {result && subMode === 'ctc' && (
        <div style={{ marginTop: '24px' }}>
          <h3 style={{ fontSize: '1.1rem', marginBottom: '12px', color: '#60a5fa' }}>💡 CTC Restructuring Recommendations</h3>
          {result.optimised_ctc && (
            <div className="summary-banner" style={{ gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))', marginBottom: '16px' }}>
              <div className="metric-card">
                <div className="metric-label">Total Annual Savings</div>
                <div className="metric-value text-green">₹{result.optimised_ctc.total_annual_saving?.toLocaleString('en-IN')}</div>
              </div>
              <div className="metric-card">
                <div className="metric-label">Monthly Extra Take-Home</div>
                <div className="metric-value text-green">₹{result.optimised_ctc.effective_monthly_saving?.toLocaleString('en-IN')}</div>
              </div>
            </div>
          )}

          {result.restructuring_recommendations && (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
              {result.restructuring_recommendations.map((rec, idx) => (
                <div key={idx} className="card" style={{ background: 'rgba(255,255,255,0.02)', padding: '14px', borderLeft: '4px solid #10b981' }}>
                  <div style={{ fontWeight: '600', color: '#34d399', marginBottom: '4px' }}>{rec.action}</div>
                  <div style={{ fontSize: '0.9rem', color: '#cbd5e1', marginBottom: '6px' }}>{rec.steps}</div>
                  <div style={{ fontSize: '0.85rem', color: '#94a3b8' }}>
                    Section: <span style={{ color: '#fbbf24' }}>{rec.section}</span> | Est. Tax Saving: <span style={{ color: '#34d399' }}>₹{rec.tax_saving?.toLocaleString('en-IN')}</span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  )
}
