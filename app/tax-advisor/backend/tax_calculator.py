"""
Statutory Indian Income Tax Calculator (FY 2026-27 / AY 2027-28)
Pure mathematical domain functions for Old vs New Tax Regimes.
Zero external dependencies; directly testable with standard pytest.
"""

from typing import Tuple, Dict, Any


def calculate_new_regime_tax(income: float) -> float:
    """Calculate tax under New Tax Regime FY 2026-27."""
    slabs = [
        (400000, 0.0),
        (400000, 0.05),   # 4L-8L
        (400000, 0.10),   # 8L-12L
        (400000, 0.15),   # 12L-16L
        (400000, 0.20),   # 16L-20L
        (400000, 0.25),   # 20L-24L
        (float("inf"), 0.30),
    ]
    tax = 0.0
    remaining = max(0.0, float(income))
    for slab_size, rate in slabs:
        if remaining <= 0:
            break
        taxable = min(remaining, slab_size)
        tax += taxable * rate
        remaining -= taxable
    return tax


def calculate_old_regime_tax(income: float, is_senior: bool = False) -> float:
    """Calculate tax under Old Tax Regime FY 2026-27."""
    basic_exemption = 300000.0 if is_senior else 250000.0
    income_val = max(0.0, float(income))
    if income_val <= basic_exemption:
        return 0.0

    if is_senior:
        slabs = [
            (200000, 0.05),   # 3L-5L
            (500000, 0.20),   # 5L-10L
            (float("inf"), 0.30),
        ]
        remaining = income_val - 300000.0
    else:
        slabs = [
            (250000, 0.05),   # 2.5L-5L
            (500000, 0.20),   # 5L-10L
            (float("inf"), 0.30),
        ]
        remaining = income_val - 250000.0

    tax = 0.0
    for slab_size, rate in slabs:
        if remaining <= 0:
            break
        taxable = min(remaining, slab_size)
        tax += taxable * rate
        remaining -= taxable
    return tax


def apply_87a_rebate_new(tax: float, net_income: float) -> float:
    """Apply Section 87A rebate for new regime (₹60K rebate if income ≤ ₹12L)."""
    if net_income <= 1200000:
        return max(0.0, tax - min(tax, 60000.0))
    # Marginal relief
    excess = net_income - 1200000
    if tax > excess:
        return excess
    return tax


def apply_87a_rebate_old(tax: float, net_income: float) -> float:
    """Apply Section 87A rebate for old regime (₹12,500 if income ≤ ₹5L)."""
    if net_income <= 500000:
        return max(0.0, tax - min(tax, 12500.0))
    return tax


def add_cess(tax: float) -> float:
    """Add 4% Health and Education Cess."""
    return tax * 1.04


def format_inr(amount: float) -> str:
    """Format float amount into INR string."""
    return f"₹{amount:,.0f}"
