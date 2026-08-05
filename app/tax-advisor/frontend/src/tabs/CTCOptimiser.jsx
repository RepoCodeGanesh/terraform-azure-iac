import React, { useState } from 'react'

const API_BASE = import.meta.env.VITE_API_BASE_URL || 'https://func-ht-taxb-p-cin-01.azurewebsites.net/api'

const SAMPLE_CTC = `Total CTC: ₹22,00,000 / year
Basic Salary: ₹9,00,000 / year (₹75,000 / month)
House Rent Allowance: ₹4,50,000 / year
Special Allowance: ₹7,00,000 / year
Employer EPF: ₹1,08,000 / year
Performance Bonus: ₹42,00,0`

export default function CTCOptimiser() {
  const [ctcText, setCtcText] = useState(SAMPLE_CTC)
  const [regime, setRegime] = useState('new')
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState(null)
  const [error, setError] = useState(null)

  const handleAnalyse = async (e) => {
    e.preventDefault()
    if (!ctcText.trim()) return

    setLoading(true)
    setError(null)
    setResult(null)

    try {
      const res = await fetch(`${API_BASE}/analyse-ctc`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ ctc_text: ctcText, regime }),
      })

      if (!res.ok) throw new Error(`HTTP ${res.status}`)

      const data = await res.json()
      setResult(data)
    } catch (err) {
      console.error('CTC analyse error:', err)
      setError(err.message || 'Failed to analyse CTC structure.')
    } finally {
      setLoading(false)
    }
  }

  const formatRupee = (val) =>
    `₹${(val || 0).toLocaleString('en-IN', { maximumFractionDigits: 0 })}`

  return (
    <div className="card">
      <div className="card-header">
        <div className="card-icon">💼</div>
        <div>
          <h2 className="card-title">CTC Restructuring & Tax Optimiser</h2>
          <p className="card-subtitle">
            Restructure special allowances into Employer NPS (80CCD(2)), Meal cards & Tax-free perks
          </p>
        </div>
      </div>

      <form onSubmit={handleAnalyse}>
        <div className="form-group">
          <label className="form-label">Target Tax Regime</label>
          <div className="regime-toggle">
            <button
              type="button"
              className={`regime-toggle-btn ${regime === 'new' ? 'active' : ''}`}
              onClick={() => setRegime('new')}
            >
              New Regime (Default - ₹12L Zero Tax)
            </button>
            <button
              type="button"
              className={`regime-toggle-btn ${regime === 'old' ? 'active' : ''}`}
              onClick={() => setRegime('old')}
            >
              Old Regime
            </button>
          </div>
        </div>

        <div className="form-group">
          <label className="form-label">Paste CTC Offer Letter / Component Breakdown</label>
          <textarea
            className="form-textarea"
            value={ctcText}
            onChange={(e) => setCtcText(e.target.value)}
            placeholder="Paste your annual CTC breakup here..."
            rows={6}
          />
        </div>

        <button type="submit" className="btn-primary" disabled={loading || !ctcText.trim()}>
          {loading ? (
            <>
              <div className="spinner" /> Generating Restructuring Plan...
            </>
          ) : (
            'Optimise CTC Structure ➔'
          )}
        </button>
      </form>

      {error && <div className="error-banner">⚠️ {error}</div>}

      {result && (
        <div style={{ marginTop: '32px' }}>
          {result.optimised_ctc && (
            <div className="result-panel success">
              <div className="result-grid">
                <div className="result-item">
                  <div className="result-label">Current Estimated Tax</div>
                  <div className="result-value" style={{ color: '#f87171' }}>
                    {formatRupee(result.current_ctc_analysis?.estimated_tax)}
                  </div>
                </div>
                <div className="result-item">
                  <div className="result-label">Optimised Tax</div>
                  <div className="result-value green">
                    {formatRupee(result.optimised_ctc.new_tax)}
                  </div>
                </div>
                <div className="result-item">
                  <div className="result-label">Annual Tax Savings</div>
                  <div className="result-value saffron">
                    {formatRupee(result.optimised_ctc.total_annual_saving)}
                  </div>
                </div>
                <div className="result-item">
                  <div className="result-label">Monthly Extra Take-Home</div>
                  <div className="result-value green">
                    +{formatRupee(result.optimised_ctc.effective_monthly_saving)} / mo
                  </div>
                </div>
              </div>
            </div>
          )}

          {result.restructuring_recommendations && (
            <div style={{ marginTop: '24px' }}>
              <h3 style={{ fontSize: '16px', color: 'var(--saffron)', marginBottom: '12px' }}>
                🚀 Recommended CTC Restructuring Steps
              </h3>
              <ul className="tip-list">
                {result.restructuring_recommendations.map((rec, idx) => (
                  <li key={idx} className="tip-item">
                    <span className="tip-icon">💡</span>
                    <div>
                      <div style={{ fontWeight: '600', color: 'var(--text-primary)' }}>
                        {rec.action} ({rec.section})
                      </div>
                      <div style={{ fontSize: '13px', marginTop: '2px' }}>
                        Reallocate {formatRupee(rec.amount_per_year)}/yr → Saves{' '}
                        <strong style={{ color: 'var(--green-light)' }}>
                          {formatRupee(rec.tax_saving)} in tax
                        </strong>
                      </div>
                      <div style={{ fontSize: '12px', color: 'var(--text-muted)', marginTop: '4px' }}>
                        Action: {rec.steps}
                      </div>
                    </div>
                  </li>
                ))}
              </ul>
            </div>
          )}

          {result.priority_actions && result.priority_actions.length > 0 && (
            <div style={{ marginTop: '20px' }}>
              <h3 style={{ fontSize: '16px', marginBottom: '8px' }}>📌 HR Email Action Items</h3>
              <ul className="tip-list">
                {result.priority_actions.map((act, idx) => (
                  <li key={idx} className="tip-item" style={{ borderLeftColor: 'var(--text-secondary)' }}>
                    <span className="tip-icon">✉️</span>
                    <div>{act}</div>
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}
    </div>
  )
}
