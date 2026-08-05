import React, { useState } from 'react'

const FAQS = [
  {
    q: "Which ITR form should I file for FY 2025-26?",
    a: `• ITR-1 (Sahaj): Income up to ₹50L from Salary, 1 House Property & Interest. NO capital gains.
• ITR-2: Salaried with Capital Gains (Mutual Funds, Stocks), Foreign Assets, or >₹50L income.
• ITR-3: Business / Freelance / F&O Trading income.
• ITR-4 (Sugam): Presumptive income under Section 44AD / 44ADA (Freelancers & Small Business).`,
  },
  {
    q: "What is the new zero-tax limit in Budget 2025?",
    a: "Under the New Tax Regime (FY 2025-26), net taxable income up to ₹12,00,000 has ZERO tax due to Section 87A rebate. For salaried employees with standard deduction of ₹75,000, gross salary up to ₹12,75,000 is completely tax-free!",
  },
  {
    q: "How does Section 80CCD(2) Employer NPS work?",
    a: "Employer contribution up to 14% of Basic Salary to NPS Tier-1 is deductible from your taxable income in BOTH Old and New Tax Regimes. It is over and above the ₹1.5L 80C limit and provides substantial tax savings without reducing your total CTC.",
  },
  {
    q: "What are the capital gains tax rates after Budget 2024?",
    a: `• LTCG on Equity / Mutual Funds: 12.5% on gains exceeding ₹1.25 Lakh per year (increased from ₹1L).
• STCG on Equity / Mutual Funds: 20% flat.
• Property LTCG: 12.5% without indexation (or 20% with indexation for properties acquired before July 23, 2024).`,
  },
  {
    q: "Can I claim HRA and Home Loan Interest together?",
    a: "Yes! If your self-occupied house is in one city and you rent in another city due to employment/business, you can claim BOTH Section 10(13A) HRA exemption AND Section 24(b) home loan interest deduction (up to ₹2L) under the Old Tax Regime.",
  },
]

export default function FilingGuide() {
  const [openFaq, setOpenFaq] = useState(null)

  return (
    <div className="card">
      <div className="card-header">
        <div className="card-icon">📁</div>
        <div>
          <h2 className="card-title">ITR Filing Guide & Tax FAQs</h2>
          <p className="card-subtitle">
            Forms selection, key deadlines, capital gains & compliance guidance for FY 2025-26
          </p>
        </div>
      </div>

      <div className="result-grid" style={{ marginBottom: '24px' }}>
        <div className="result-panel">
          <h3 style={{ fontSize: '15px', color: 'var(--saffron)', marginBottom: '8px' }}>
            📅 Key ITR Filing Deadlines (FY 2025-26)
          </h3>
          <ul className="tip-list">
            <li className="tip-item">
              <span className="tip-icon">⏰</span>
              <div>
                <strong>31 July 2026:</strong> Non-audit individual tax returns (ITR-1, 2, 4)
              </div>
            </li>
            <li className="tip-item">
              <span className="tip-icon">⏰</span>
              <div>
                <strong>31 October 2026:</strong> Audit cases & businesses
              </div>
            </li>
            <li className="tip-item">
              <span className="tip-icon">⏰</span>
              <div>
                <strong>31 December 2026:</strong> Belated return / Revised return filing
              </div>
            </li>
          </ul>
        </div>

        <div className="result-panel">
          <h3 style={{ fontSize: '15px', color: 'var(--saffron)', marginBottom: '8px' }}>
            📑 Which Form Suits You?
          </h3>
          <ul className="tip-list">
            <li className="tip-item">
              <span className="tip-icon">1️⃣</span>
              <div>
                <strong>ITR-1:</strong> Salary only + No Mutual Fund / Stock Sales
              </div>
            </li>
            <li className="tip-item">
              <span className="tip-icon">2️⃣</span>
              <div>
                <strong>ITR-2:</strong> Salary + Equity MF / Stock Capital Gains / 2+ Houses
              </div>
            </li>
            <li className="tip-item">
              <span className="tip-icon">4️⃣</span>
              <div>
                <strong>ITR-4:</strong> Freelancer / Professional under 44ADA (50% presumptive)
              </div>
            </li>
          </ul>
        </div>
      </div>

      <div style={{ marginTop: '24px' }}>
        <h3 style={{ fontSize: '18px', color: 'var(--text-primary)', marginBottom: '16px' }}>
          ❓ Frequently Asked Tax Questions
        </h3>

        <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
          {FAQS.map((faq, idx) => (
            <div
              key={idx}
              style={{
                background: 'var(--bg-elevated)',
                border: '1px solid var(--border)',
                borderRadius: 'var(--radius-md)',
                overflow: 'hidden',
              }}
            >
              <button
                onClick={() => setOpenFaq(openFaq === idx ? null : idx)}
                style={{
                  width: '100%',
                  padding: '14px 18px',
                  background: 'none',
                  border: 'none',
                  color: 'var(--text-primary)',
                  fontFamily: 'var(--font-body)',
                  fontSize: '14.5px',
                  fontWeight: '600',
                  textAlign: 'left',
                  cursor: 'pointer',
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'center',
                }}
              >
                <span>{faq.q}</span>
                <span style={{ color: 'var(--saffron)', fontSize: '18px' }}>
                  {openFaq === idx ? '−' : '+'}
                </span>
              </button>

              {openFaq === idx && (
                <div
                  style={{
                    padding: '0 18px 16px 18px',
                    fontSize: '13.5px',
                    color: 'var(--text-secondary)',
                    lineHeight: '1.6',
                    whiteSpace: 'pre-line',
                    borderTop: '1px solid var(--border)',
                    paddingTop: '12px',
                  }}
                >
                  {faq.a}
                </div>
              )}
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
