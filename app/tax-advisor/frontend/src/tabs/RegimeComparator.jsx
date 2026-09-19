import React, { useState } from 'react'

const API_BASE = import.meta.env.VITE_API_BASE || 'https://apim-ht-ss-p-cin-01.azure-api.net/tax-advisor'

export default function RegimeComparator() {
  const [form, setForm] = useState({
    gross_salary: '1800000',
    deductions_80c: '150000',
    deductions_80d: '25000',
    nps_80ccd1b: '50000',
    employer_nps: '84000',
    home_loan_interest: '0',
    hra_exempt: '180000',
    other_deductions: '0',
    is_senior: false,
  })

  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState(null)
  const [error, setError] = useState(null)

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target
    setForm((prev) => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value,
    }))
  }

  const handleCalculate = async (e) => {
    e.preventDefault()
    setLoading(true)
    setError(null)
    setResult(null)

    try {
      const payload = {
        gross_salary: parseFloat(form.gross_salary) || 0,
        deductions_80c: parseFloat(form.deductions_80c) || 0,
        deductions_80d: parseFloat(form.deductions_80d) || 0,
        nps_80ccd1b: parseFloat(form.nps_80ccd1b) || 0,
        employer_nps: parseFloat(form.employer_nps) || 0,
        home_loan_interest: parseFloat(form.home_loan_interest) || 0,
        hra_exempt: parseFloat(form.hra_exempt) || 0,
        other_deductions: parseFloat(form.other_deductions) || 0,
        is_senior: form.is_senior,
      }

      const res = await fetch(`${API_BASE}/compare-regime`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      })

      if (!res.ok) {
        throw new Error(`HTTP ${res.status}`)
      }

      const data = await res.json()
      setResult(data)
    } catch (err) {
      console.error('Calculate error:', err)
      setError(err.message || 'Failed to calculate regime comparison.')
    } finally {
      setLoading(false)
    }
  }

  const formatRupee = (val) =>
    `₹${(val || 0).toLocaleString('en-IN', { maximumFractionDigits: 0 })}`

  return (
    <div className="card">
      <div className="card-header">
        <div className="card-icon">⚖️</div>
        <div>
          <h2 className="card-title">Old vs New Tax Regime Comparator</h2>
          <p className="card-subtitle">
            Side-by-side tax computation for FY 2026-27 (AY 2027-28)
          </p>
        </div>
      </div>

      <form onSubmit={handleCalculate}>
        <div className="form-grid">
          <div className="form-group">
            <label className="form-label">Annual Gross Salary (₹)</label>
            <input
              type="number"
              name="gross_salary"
              className="form-input"
              value={form.gross_salary}
              onChange={handleChange}
              placeholder="e.g. 1800000"
              required
            />
          </div>

          <div className="form-group">
            <label className="form-label">Employer NPS - Sec 80CCD(2) (₹)</label>
            <input
              type="number"
              name="employer_nps"
              className="form-input"
              value={form.employer_nps}
              onChange={handleChange}
              placeholder="Up to 14% of Basic (Works in BOTH regimes)"
            />
          </div>

          <div className="form-group">
            <label className="form-label">80C Investments (₹)</label>
            <input
              type="number"
              name="deductions_80c"
              className="form-input"
              value={form.deductions_80c}
              onChange={handleChange}
              placeholder="PPF, ELSS, EPF (Max 1.5L - Old Regime)"
            />
          </div>

          <div className="form-group">
            <label className="form-label">80D Health Insurance (₹)</label>
            <input
              type="number"
              name="deductions_80d"
              className="form-input"
              value={form.deductions_80d}
              onChange={handleChange}
              placeholder="Self & Parents (Max 75K - Old Regime)"
            />
          </div>

          <div className="form-group">
            <label className="form-label">NPS Self - Sec 80CCD(1B) (₹)</label>
            <input
              type="number"
              name="nps_80ccd1b"
              className="form-input"
              value={form.nps_80ccd1b}
              onChange={handleChange}
              placeholder="Extra Tier 1 (Max 50K - Old Regime)"
            />
          </div>

          <div className="form-group">
            <label className="form-label" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <span>HRA Exemption (₹)</span>
            </label>
            <input
              type="number"
              name="hra_exempt"
              className="form-input"
              value={form.hra_exempt}
              onChange={handleChange}
              placeholder="Exempt HRA (Old Regime)"
            />
            <div style={{ fontSize: '0.8rem', color: '#94a3b8', marginTop: '4px' }}>
              💡 Rule 2A (Old Regime Only): <strong>Statutory Metros (Delhi, Mumbai, Kolkata, Chennai) = 50% Basic</strong> | <strong>Non-Metros (Bengaluru, Hyd, Pune, etc.) = 40% Basic</strong>. <em>(HRA Exemption is ₹0 in New Regime)</em>
            </div>
          </div>

          <div className="form-group">
            <label className="form-label">Home Loan Interest - Sec 24b (₹)</label>
            <input
              type="number"
              name="home_loan_interest"
              className="form-input"
              value={form.home_loan_interest}
              onChange={handleChange}
              placeholder="Self occupied property (Max 2L - Old Regime)"
            />
          </div>

          <div className="form-group">
            <label className="form-label">Other Deductions (80E, 80G, etc) (₹)</label>
            <input
              type="number"
              name="other_deductions"
              className="form-input"
              value={form.other_deductions}
              onChange={handleChange}
              placeholder="Education loan, donations, etc."
            />
          </div>
        </div>

        <div style={{ marginTop: '8px', display: 'flex', alignItems: 'center', gap: '8px' }}>
          <input
            type="checkbox"
            id="is_senior"
            name="is_senior"
            checked={form.is_senior}
            onChange={handleChange}
          />
          <label htmlFor="is_senior" className="form-label" style={{ margin: 0, cursor: 'pointer' }}>
            Senior Citizen (60+ years)
          </label>
        </div>

        <div style={{ marginTop: '24px' }}>
          <button type="submit" className="btn-primary" disabled={loading}>
            {loading ? (
              <>
                <div className="spinner" /> Calculating...
              </>
            ) : (
              'Compare Tax Regimes ➔'
            )}
          </button>
        </div>
      </form>

      {error && <div className="error-banner">⚠️ {error}</div>}

      {result && (
        <div style={{ marginTop: '32px' }}>
          <div className={`result-panel ${result.recommendation === 'new' ? 'success' : 'warning'}`}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <div>
                <span
                  className={`winner-badge ${result.recommendation}`}
                  style={{ marginBottom: '8px' }}
                >
                  {result.recommendation === 'new'
                    ? '✨ NEW REGIME WINS'
                    : '🏆 OLD REGIME WINS'}
                </span>
                <h3 style={{ fontSize: '18px', marginTop: '4px' }}>{result.summary}</h3>
              </div>
            </div>
          </div>

          {/* Desktop Table View (>= 769px) */}
          <table className="comparison-table desktop-only-table">
            <thead>
              <tr>
                <th>Component</th>
                <th className="col-new">New Regime (Default)</th>
                <th className="col-old">Old Regime</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td className="col-label">Gross Salary</td>
                <td>{formatRupee(result.gross_salary)}</td>
                <td>{formatRupee(result.gross_salary)}</td>
              </tr>
              <tr>
                <td className="col-label">Standard Deduction</td>
                <td className="col-new">-{formatRupee(result.new_regime.standard_deduction)}</td>
                <td className="col-old">-{formatRupee(result.old_regime.standard_deduction)}</td>
              </tr>
              <tr>
                <td className="col-label">Employer NPS [80CCD(2)]</td>
                <td className="col-new">-{formatRupee(result.new_regime.employer_nps_deduction)}</td>
                <td className="col-old">-{formatRupee(result.old_regime.employer_nps_deduction)}</td>
              </tr>
              <tr>
                <td className="col-label">Other Deductions (80C, 80D, HRA, Home Loan)</td>
                <td className="col-new" style={{ color: 'var(--text-muted)' }}>
                  Not Allowed
                </td>
                <td className="col-old">
                  -{formatRupee(result.old_regime.total_deductions - result.old_regime.standard_deduction - result.old_regime.employer_nps_deduction)}
                </td>
              </tr>
              <tr style={{ fontWeight: '600', borderTop: '2px solid var(--border)' }}>
                <td className="col-label">Net Taxable Income</td>
                <td className="col-new">{formatRupee(result.new_regime.taxable_income)}</td>
                <td className="col-old">{formatRupee(result.old_regime.taxable_income)}</td>
              </tr>
              <tr>
                <td className="col-label">Base Tax</td>
                <td>{formatRupee(result.new_regime.tax_before_cess)}</td>
                <td>{formatRupee(result.old_regime.tax_before_cess)}</td>
              </tr>
              <tr style={{ fontSize: '16px', fontWeight: '700', borderTop: '2px solid var(--border)' }}>
                <td className="col-label" style={{ color: 'var(--text-primary)' }}>
                  Total Tax Payable (inc. 4% Cess)
                </td>
                <td className="col-new" style={{ fontSize: '18px' }}>
                  {formatRupee(result.new_regime.total_tax)}
                </td>
                <td className="col-old" style={{ fontSize: '18px' }}>
                  {formatRupee(result.old_regime.total_tax)}
                </td>
              </tr>
              <tr>
                <td className="col-label">Effective Tax Rate</td>
                <td className="col-new">{result.new_regime.effective_rate}%</td>
                <td className="col-old">{result.old_regime.effective_rate}%</td>
              </tr>
            </tbody>
          </table>

          {/* Mobile Card-Based Reflow View (<= 768px) */}
          <div className="comparison-cards-mobile mobile-only-block">
            {/* Total Tax Highlight Card */}
            <div className="mobile-summary-card" style={{
              background: result.recommendation === 'new' ? 'rgba(29, 185, 84, 0.08)' : 'rgba(96, 165, 250, 0.08)',
              border: `1.5px solid ${result.recommendation === 'new' ? 'rgba(29, 185, 84, 0.4)' : 'rgba(96, 165, 250, 0.4)'}`,
              borderRadius: '12px',
              padding: '16px',
              marginBottom: '14px'
            }}>
              <div style={{ fontSize: '0.78rem', color: 'var(--text-secondary)', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.5px' }}>
                Total Tax Payable (inc. 4% Cess)
              </div>
              <div style={{ display: 'flex', gap: '10px', marginTop: '10px' }}>
                <div style={{
                  flex: 1,
                  background: 'rgba(29, 185, 84, 0.12)',
                  border: '1px solid rgba(29, 185, 84, 0.3)',
                  padding: '10px',
                  borderRadius: '8px',
                  textAlign: 'center'
                }}>
                  <div style={{ fontSize: '0.72rem', color: 'var(--green-light)', fontWeight: 700 }}>NEW REGIME</div>
                  <div style={{ fontSize: '1.25rem', fontWeight: 800, color: 'var(--green-light)', marginTop: '4px' }}>
                    {formatRupee(result.new_regime.total_tax)}
                  </div>
                  <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>{result.new_regime.effective_rate}% eff.</div>
                </div>

                <div style={{
                  flex: 1,
                  background: 'rgba(96, 165, 250, 0.1)',
                  border: '1px solid rgba(96, 165, 250, 0.25)',
                  padding: '10px',
                  borderRadius: '8px',
                  textAlign: 'center'
                }}>
                  <div style={{ fontSize: '0.72rem', color: '#60a5fa', fontWeight: 700 }}>OLD REGIME</div>
                  <div style={{ fontSize: '1.25rem', fontWeight: 800, color: '#60a5fa', marginTop: '4px' }}>
                    {formatRupee(result.old_regime.total_tax)}
                  </div>
                  <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>{result.old_regime.effective_rate}% eff.</div>
                </div>
              </div>
            </div>

            {/* Detailed Component Breakdown Cards */}
            <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
              {[
                { label: 'Gross Salary', newVal: formatRupee(result.gross_salary), oldVal: formatRupee(result.gross_salary) },
                { label: 'Standard Deduction', newVal: `-${formatRupee(result.new_regime.standard_deduction)}`, oldVal: `-${formatRupee(result.old_regime.standard_deduction)}` },
                { label: 'Employer NPS [80CCD(2)]', newVal: `-${formatRupee(result.new_regime.employer_nps_deduction)}`, oldVal: `-${formatRupee(result.old_regime.employer_nps_deduction)}` },
                { label: 'Other Deductions (80C/80D/HRA)', newVal: 'Not Allowed', oldVal: `-${formatRupee(result.old_regime.total_deductions - result.old_regime.standard_deduction - result.old_regime.employer_nps_deduction)}` },
                { label: 'Net Taxable Income', newVal: formatRupee(result.new_regime.taxable_income), oldVal: formatRupee(result.old_regime.taxable_income) },
                { label: 'Base Tax (Pre-Cess)', newVal: formatRupee(result.new_regime.tax_before_cess), oldVal: formatRupee(result.old_regime.tax_before_cess) }
              ].map((item, idx) => (
                <div key={idx} style={{
                  background: 'var(--bg-elevated)',
                  border: '1px solid var(--border)',
                  borderRadius: '10px',
                  padding: '12px 14px'
                }}>
                  <div style={{ fontSize: '0.82rem', fontWeight: 600, color: 'var(--text-primary)', marginBottom: '8px' }}>
                    {item.label}
                  </div>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', fontSize: '0.85rem' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                      <span style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>New:</span>
                      <span style={{ color: 'var(--green-light)', fontWeight: 600 }}>{item.newVal}</span>
                    </div>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                      <span style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>Old:</span>
                      <span style={{ color: '#60a5fa', fontWeight: 600 }}>{item.oldVal}</span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
