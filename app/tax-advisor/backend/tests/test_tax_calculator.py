"""
Unit tests for Statutory Indian Income Tax Calculator (FY 2026-27).
Tests pure mathematical slab logic using standard library (runs anywhere).
"""

import os
import sys
from pathlib import Path

# Add backend directory to sys.path
backend_dir = str(Path(__file__).resolve().parent.parent)
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

import unittest
from tax_calculator import (
    calculate_new_regime_tax,
    calculate_old_regime_tax,
    apply_87a_rebate_new,
    apply_87a_rebate_old,
    add_cess,
    format_inr,
)


class TestTaxCalculator(unittest.TestCase):

    def test_new_regime_zero_tax_up_to_4_lakhs(self):
        """Income <= 4L has 0% tax in New Regime."""
        self.assertEqual(calculate_new_regime_tax(0), 0.0)
        self.assertEqual(calculate_new_regime_tax(400000), 0.0)

    def test_new_regime_slabs(self):
        """Check standard slabs: 4-8L at 5%, 8-12L at 10%."""
        # 8L: 4L * 0.05 = 20,000
        self.assertEqual(calculate_new_regime_tax(800000), 20000.0)
        # 12L: 20,000 + (4L * 0.10 = 40,000) = 60,000
        self.assertEqual(calculate_new_regime_tax(1200000), 60000.0)

    def test_new_regime_section_87a_rebate(self):
        """Section 87A provides up to ₹60K rebate for income <= ₹12L."""
        tax = calculate_new_regime_tax(1200000)  # 60,000
        rebated_tax = apply_87a_rebate_new(tax, 1200000)
        self.assertEqual(rebated_tax, 0.0)

    def test_old_regime_basic_exemption(self):
        """Basic exemption is ₹2.5L for normal and ₹3L for seniors."""
        self.assertEqual(calculate_old_regime_tax(250000, is_senior=False), 0.0)
        self.assertEqual(calculate_old_regime_tax(300000, is_senior=True), 0.0)

    def test_old_regime_slabs(self):
        """5L income: (2.5L - 5L) * 5% = 12,500."""
        tax = calculate_old_regime_tax(500000, is_senior=False)
        self.assertEqual(tax, 12500.0)
        # With 87A rebate for <= 5L, net tax is 0
        self.assertEqual(apply_87a_rebate_old(tax, 500000), 0.0)

    def test_add_cess(self):
        """Health & Education cess is exactly 4%."""
        self.assertEqual(add_cess(100000.0), 104000.0)

    def test_format_inr(self):
        """Check INR currency formatting."""
        self.assertEqual(format_inr(1250000), "₹1,250,000")


if __name__ == "__main__":
    unittest.main()
