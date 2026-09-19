---
title: "RBI Master Direction — Digital Payment Security Controls & Tokenisation, 2021 (Updated 2024)"
circular_no: "RBI/2021-22/126"
category: "digital_payments_tokenisation"
year: "2024"
authorities: "Reserve Bank of India, Department of Payment and Settlement Systems (DPSS), Payment and Settlement Systems Act 2007"
---

# RBI Master Direction on Digital Payment Security Controls & Tokenisation

## 1. Statutory Scope & Applicability
Issued under Section 18 read with Section 10(2) of the Payment and Settlement Systems Act, 2007 (Act 51 of 2007). Applies to all Scheduled Commercial Banks, Non-bank PPI Issuers, Card Payment Networks, and Payment Aggregators/Payment Gateways.

---

## 2. Card-on-File Tokenisation (CoFT) Framework

### Section 5.4: Absolute Prohibition of Card Data Storage
* **Prohibition on Merchants & Gateways:** No entity in the payment chain other than card issuers and card networks shall store actual card credentials (**16-digit PAN, CVV, Card Expiry Date**) after transaction authorization.
* **Token Service Providers (TSPs):** Tokenisation of card data shall be carried out only by RBI-approved **Token Service Providers (TSPs)** which are the authorized card networks or issuing banks.
* **Explicit Customer Consent:** Tokenisation requires explicit customer consent with Additional Factor of Authentication (AFA) validation.

---

## 3. Digital Payment Security Controls & Authentication

### Section 8.2: Mandatory Multi-Factor / Additional Factor of Authentication (AFA)
* All domestic digital payment transactions (card-not-present / e-commerce, UPI, mobile banking) must be authenticated using **Two-Factor / Additional Factor of Authentication (AFA)**.
* **Exemptions:** Contactless tap-and-pay transactions at POS terminals up to **₹5,000** without PIN entry. Recurring e-mandate transactions up to **₹15,000** per transaction (post initial AFA consent).

---

## 4. Fraud Risk Monitoring & Limits Management

### Section 11.1: Customer Limit Controls
1. **Dynamic Facility Toggling:** Customers must be provided instant 24x7 facility via Mobile App / Net Banking to enable/disable:
   - International transactions
   - Online e-commerce transactions
   - Contactless NFC transactions
   - ATM cash withdrawals
2. **Transaction Velocity & Anomaly Checks:** Real-time risk engine must detect unusual transaction spikes, geolocational impossibilities, and multiple consecutive failed OTP attempts.
