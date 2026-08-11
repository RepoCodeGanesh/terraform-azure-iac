import React, { useState } from 'react'

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
    <div className="card" style={{ maxWidth: '1000px', margin: '0 auto', padding: '28px' }}>
      <div className="card-header" style={{ marginBottom: '20px', borderBottom: '1px solid rgba(255,255,255,0.08)', paddingBottom: '16px' }}>
        <div className="card-icon" style={{ background: 'linear-gradient(135deg, #ff9933 0%, #ff6600 100%)', color: '#fff', fontSize: '24px' }}>💼</div>
        <div>
          <h2 className="card-title" style={{ fontSize: '1.4rem', fontWeight: '700' }}>Salary & CTC Optimiser</h2>
          <p className="card-subtitle" style={{ fontSize: '0.9rem', color: '#94a3b8' }}>Analyze salary slips or offer letters to maximize your net take-home pay for FY 2026-27</p>
        </div>
      </div>

      {/* Sub-mode Toggle Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '12px', marginBottom: '24px' }}>
        <div style={{ display: 'flex', gap: '8px', background: 'rgba(15, 17, 30, 0.8)', padding: '6px', borderRadius: '12px', border: '1px solid rgba(255,255,255,0.08)' }}>
          <button
            className={`btn ${subMode === 'slip' ? 'btn-primary' : 'btn-outline'}`}
            onClick={() => handleModeChange('slip')}
            type="button"
            style={{ padding: '10px 20px', fontSize: '0.95rem', borderRadius: '8px', fontWeight: subMode === 'slip' ? '600' : '400' }}
          >
            📄 Monthly Salary Slip
          </button>
          <button
            className={`btn ${subMode === 'ctc' ? 'btn-primary' : 'btn-outline'}`}
            onClick={() => handleModeChange('ctc')}
            type="button"
            style={{ padding: '10px 20px', fontSize: '0.95rem', borderRadius: '8px', fontWeight: subMode === 'ctc' ? '600' : '400' }}
          >
            💼 Annual CTC Offer Letter
          </button>
        </div>

        <div style={{ display: 'flex', gap: '8px' }}>
          <button
            type="button"
            className="btn btn-outline"
            style={{ fontSize: '0.85rem', padding: '6px 12px', color: '#94a3b8' }}
            onClick={() => setInputText(subMode === 'slip' ? SAMPLE_SLIP : SAMPLE_CTC)}
          >
            🔄 Reset Sample Data
          </button>
          <button
            type="button"
            className="btn btn-outline"
            style={{ fontSize: '0.85rem', padding: '6px 12px', color: '#94a3b8' }}
            onClick={() => setInputText('')}
          >
            🗑️ Clear Text
          </button>
        </div>
      </div>

      <form onSubmit={handleAnalyze}>
        <div className="form-group" style={{ marginBottom: '20px' }}>
          <label className="form-label" style={{ fontSize: '0.95rem', fontWeight: '600', color: '#f1f5f9', marginBottom: '10px', display: 'flex', alignItems: 'center', gap: '8px' }}>
            <span>{subMode === 'slip' ? '📝 Paste Salary Slip Breakdown:' : '📝 Paste CTC / Offer Letter Breakdown:'}</span>
            <span style={{ fontSize: '0.8rem', color: '#94a3b8', fontWeight: '400' }}>(Include Basic, HRA, Special Allowance, PF, etc.)</span>
          </label>
          <textarea
            className="form-control"
            rows={8}
            value={inputText}
            onChange={(e) => setInputText(e.target.value)}
            placeholder={subMode === 'slip' ? 'Paste salary breakdown here...' : 'Paste CTC breakdown here...'}
            style={{ width: '100%', minHeight: '220px', fontFamily: "'Inter', sans-serif", fontSize: '0.95rem' }}
          />
        </div>

        {subMode === 'ctc' && (
          <div className="form-group" style={{ marginBottom: '20px' }}>
            <label className="form-label" style={{ fontSize: '0.95rem', fontWeight: '600', color: '#f1f5f9', marginBottom: '8px' }}>Target Tax Regime:</label>
            <select className="form-control" value={regime} onChange={(e) => setRegime(e.target.value)} style={{ width: '100%', height: '48px' }}>
              <option value="new">New Tax Regime (Default FY 2026-27 - ₹12L Zero Tax Limit)</option>
              <option value="old">Old Tax Regime (With 80C, 80D & HRA Deductions)</option>
            </select>
          </div>
        )}

        <button type="submit" className="btn btn-primary" disabled={loading} style={{ width: '100%', height: '52px', fontSize: '1.05rem', fontWeight: '700', borderRadius: '10px', marginTop: '10px' }}>
          {loading ? 'Analyzing Pay Structure...' : subMode === 'slip' ? '⚡ Analyze Salary Slip & Calculate HRA' : '⚡ Optimize CTC Structure & Calculate Savings'}
        </button>
      </form>

      {error && (
        <div className="alert alert-error" style={{ marginTop: '20px', padding: '16px', borderRadius: '10px' }}>
          ⚠️ {error}
        </div>
      )}

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

      {result && subMode === 'ctc' && (
        <div style={{ marginTop: '28px', paddingTop: '20px', borderTop: '1px solid rgba(255,255,255,0.08)' }}>
          <h3 style={{ fontSize: '1.2rem', marginBottom: '16px', color: '#60a5fa', fontWeight: '700' }}>💡 CTC Restructuring Recommendations</h3>
          {result.optimised_ctc && (
            <div className="summary-banner" style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '12px', marginBottom: '20px' }}>
              <div className="metric-card" style={{ padding: '16px', borderRadius: '10px', background: 'rgba(16, 185, 129, 0.08)', border: '1px solid rgba(16, 185, 129, 0.2)' }}>
                <div className="metric-label" style={{ color: '#34d399', fontSize: '0.85rem' }}>Total Annual Savings</div>
                <div className="metric-value text-green" style={{ fontSize: '1.4rem', fontWeight: '700', color: '#34d399' }}>₹{result.optimised_ctc.total_annual_saving?.toLocaleString('en-IN')}</div>
              </div>
              <div className="metric-card" style={{ padding: '16px', borderRadius: '10px', background: 'rgba(16, 185, 129, 0.08)', border: '1px solid rgba(16, 185, 129, 0.2)' }}>
                <div className="metric-label" style={{ color: '#34d399', fontSize: '0.85rem' }}>Extra Take-Home / Month</div>
                <div className="metric-value text-green" style={{ fontSize: '1.4rem', fontWeight: '700', color: '#34d399' }}>₹{result.optimised_ctc.effective_monthly_saving?.toLocaleString('en-IN')}</div>
              </div>
            </div>
          )}

          {result.restructuring_recommendations && (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
              {result.restructuring_recommendations.map((rec, idx) => (
                <div key={idx} className="card" style={{ background: 'rgba(15, 23, 42, 0.6)', padding: '18px', borderLeft: '4px solid #10b981', borderRadius: '10px' }}>
                  <div style={{ fontWeight: '700', color: '#34d399', fontSize: '1.05rem', marginBottom: '6px' }}>{rec.action}</div>
                  <div style={{ fontSize: '0.95rem', color: '#e2e8f0', marginBottom: '10px', lineHeight: '1.6' }}>{rec.steps}</div>
                  <div style={{ fontSize: '0.85rem', color: '#94a3b8', background: 'rgba(255,255,255,0.03)', padding: '8px 12px', borderRadius: '6px', width: 'fit-content' }}>
                    Section: <span style={{ color: '#ff9933', fontWeight: '600' }}>{rec.section}</span> | Est. Tax Saving: <span style={{ color: '#34d399', fontWeight: '600' }}>₹{rec.tax_saving?.toLocaleString('en-IN')}</span>
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
