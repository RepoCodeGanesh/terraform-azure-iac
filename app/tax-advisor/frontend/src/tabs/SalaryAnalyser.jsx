import React, { useState } from 'react'

const API_BASE = 'https://func-ht-taxb-p-cin-01.azurewebsites.net/api'

const SAMPLE_SLIP = `Basic Salary: ₹85,000 / month
House Rent Allowance (HRA): ₹34,000 / month
Special Allowance: ₹28,000 / month
Performance Pay: ₹15,000 / month
Employee Provident Fund (EPF): ₹10,200 / month
Professional Tax: ₹200 / month
Monthly Rent Paid: ₹30,000 in Mumbai (Metro)`

export default function SalaryAnalyser() {
  const [salaryText, setSalaryText] = useState(SAMPLE_SLIP)
  const [city, setCity] = useState('metro')
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState(null)
  const [error, setError] = useState(null)

  const handleAnalyse = async (e) => {
    e.preventDefault()
    if (!salaryText.trim()) return

    setLoading(true)
    setError(null)
    setResult(null)

    try {
      const res = await fetch(`${API_BASE}/analyse-salary`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ salary_text: salaryText, city }),
      })

      if (!res.ok) throw new Error(`HTTP ${res.status}`)

      const data = await res.json()
      setResult(data)
    } catch (err) {
      console.error('Analyse error:', err)
      setError(err.message || 'Failed to analyse salary slip.')
    } finally {
      setLoading(false)
    }
  }

  const formatRupee = (val) =>
    `₹${(val || 0).toLocaleString('en-IN', { maximumFractionDigits: 0 })}`

  return (
    <div className="card">
      <div className="card-header">
        <div className="card-icon">📄</div>
        <div>
          <h2 className="card-title">Salary Slip Analyser</h2>
          <p className="card-subtitle">
            Paste your salary slip text or monthly breakdown to extract components & HRA exemptions
          </p>
        </div>
      </div>

      <form onSubmit={handleAnalyse}>
        <div className="form-group">
          <label className="form-label">City Category (for HRA Exemption)</label>
          <select
            className="form-select"
            value={city}
            onChange={(e) => setCity(e.target.value)}
            style={{ maxWidth: '300px' }}
          >
            <option value="metro">Metro (Mumbai, Delhi, Kolkata, Chennai - 50% Basic)</option>
            <option value="non-metro">Non-Metro (Bangalore, Hyderabad, Pune, etc - 40% Basic)</option>
          </select>
        </div>

        <div className="form-group">
          <label className="form-label">Paste Salary Slip / Component Breakdown</label>
          <textarea
            className="form-textarea"
            value={salaryText}
            onChange={(e) => setSalaryText(e.target.value)}
            placeholder="Paste your monthly or annual salary slip text here..."
            rows={7}
          />
        </div>

        <button type="submit" className="btn-primary" disabled={loading || !salaryText.trim()}>
          {loading ? (
            <>
              <div className="spinner" /> Analysing Salary Components...
            </>
          ) : (
            'Analyse Salary Slip ➔'
          )}
        </button>
      </form>

      {error && <div className="error-banner">⚠️ {error}</div>}

      {result && (
        <div style={{ marginTop: '32px' }}>
          {result.extracted_components && (
            <div className="result-panel">
              <h3 style={{ fontSize: '16px', color: 'var(--saffron)', marginBottom: '12px' }}>
                📊 Extracted Annual Components
              </h3>
              <div className="result-grid">
                <div className="result-item">
                  <div className="result-label">Basic Salary</div>
                  <div className="result-value">
                    {formatRupee(result.extracted_components.basic_salary_annual)}
                  </div>
                </div>
                <div className="result-item">
                  <div className="result-label">HRA Received</div>
                  <div className="result-value">
                    {formatRupee(result.extracted_components.hra_annual)}
                  </div>
                </div>
                <div className="result-item">
                  <div className="result-label">Special Allowance</div>
                  <div className="result-value" style={{ color: '#f87171' }}>
                    {formatRupee(result.extracted_components.special_allowance_annual)}
                  </div>
                </div>
                <div className="result-item">
                  <div className="result-label">Total Annual Gross</div>
                  <div className="result-value green">
                    {formatRupee(result.extracted_components.total_gross_annual)}
                  </div>
                </div>
              </div>
            </div>
          )}

          {result.hra_calculation && (
            <div className="result-panel" style={{ marginTop: '16px' }}>
              <h3 style={{ fontSize: '16px', color: 'var(--saffron)', marginBottom: '12px' }}>
                🏠 HRA Exemption Analysis (Section 10(13A))
              </h3>
              <ul className="tip-list">
                <li className="tip-item">
                  <span className="tip-icon">▸</span>
                  <div>
                    <strong>1. Actual HRA Received:</strong> {formatRupee(result.hra_calculation.hra_received)}
                  </div>
                </li>
                <li className="tip-item">
                  <span className="tip-icon">▸</span>
                  <div>
                    <strong>2. {city === 'metro' ? '50%' : '40%'} of Basic Salary:</strong>{' '}
                    {formatRupee(result.hra_calculation['50_or_40_percent_basic'])}
                  </div>
                </li>
                <li className="tip-item">
                  <span className="tip-icon">▸</span>
                  <div>
                    <strong>3. Rent Paid - 10% of Basic:</strong>{' '}
                    {formatRupee(result.hra_calculation.rent_minus_10pc_basic)}
                  </div>
                </li>
                <li className="tip-item" style={{ borderLeftColor: 'var(--green-light)', background: 'rgba(29,185,84,0.08)' }}>
                  <span className="tip-icon" style={{ color: 'var(--green-light)' }}>✓</span>
                  <div>
                    <strong>HRA EXEMPTION (Minimum of above):</strong>{' '}
                    <strong style={{ color: 'var(--green-light)', fontSize: '16px' }}>
                      {formatRupee(result.hra_calculation.hra_exempt)}
                    </strong>
                    <div style={{ fontSize: '12px', color: 'var(--text-muted)', marginTop: '4px' }}>
                      Taxable HRA portion: {formatRupee(result.hra_calculation.hra_taxable)}
                    </div>
                  </div>
                </li>
              </ul>
            </div>
          )}

          {result.tax_saving_tips && result.tax_saving_tips.length > 0 && (
            <div style={{ marginTop: '20px' }}>
              <h3 style={{ fontSize: '16px', marginBottom: '12px' }}>💡 Custom Tax Saving Tips</h3>
              <ul className="tip-list">
                {result.tax_saving_tips.map((tip, idx) => (
                  <li key={idx} className="tip-item">
                    <span className="tip-icon">⚡</span>
                    <div>{tip}</div>
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
