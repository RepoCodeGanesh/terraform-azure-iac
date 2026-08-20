---
title: "RBI Master Direction — Information Technology Governance, Risk, Controls and Cybersecurity, 2023"
circular_no: "RBI/2023-24/108"
category: "it_governance_cybersecurity"
year: "2024"
authorities: "Reserve Bank of India, Department of Supervision, IT Act 2000, CERT-In"
---

# RBI Master Direction on IT Governance, Risk, Controls and Cybersecurity

## 1. Statutory Mandate & Scope
Issued under Section 35A of the Banking Regulation Act, 1949. Mandates robust IT strategy, cybersecurity governance, and operational resilience for all Scheduled Commercial Banks, Non-Banking Financial Companies (NBFCs), and Payment System Operators.

---

## 2. IT Governance & Board Oversight

### Section 3.1: Board Level IT Strategy Committee (ITSC)
* The Board of Directors of every Regulated Entity (RE) must establish an **IT Strategy Committee (ITSC)** headed by an Independent Director.
* The ITSC must meet at least **quarterly** to review cybersecurity posture, IT risk assessments, cloud adoption roadmaps, and IT audit findings.

### Section 4.2: Chief Information Security Officer (CISO) Role
* REs must appoint a dedicated, full-time **Chief Information Security Officer (CISO)** who operates independently from the Chief Technology Officer (CTO) / IT Operations.
* The CISO reports directly to the Board Risk Committee or Executive Director / Managing Director.

---

## 3. Cloud Security & Data Localization

### Section 8.1: Mandatory Geographic Data Residency
* **Primary and DR within India:** All regulated entities storing banking transaction records, customer account data, logs, and cryptographic material in commercial public cloud environments must ensure primary active and disaster recovery (DR) data residues remain within **Indian geographical borders**.
* **MeitY Empanelment:** Cloud Service Providers (CSPs) contracted by banks (e.g. Azure, AWS, GCP) must be **empanelled with the Ministry of Electronics and Information Technology (MeitY)**.
* **Audit & Inspection Rights:** Cloud contracts must explicitly guarantee unconditional inspection and audit rights for the RBI supervisory team and bank internal auditors.

---

## 4. Cybersecurity Controls & Incident Reporting

### Section 11.4: Mandatory 6-Hour Incident Reporting
* Any major cybersecurity breach, ransomware infection, data leak, or unauthorized database access must be reported to the **RBI Cyber Security and IT Risk (CSITE) Cell** and **CERT-In within 6 hours** of detection.
* Root Cause Analysis (RCA) must be submitted within **21 calendar days**.

---

## 5. Security Architecture Standards & Zero Trust

### Section 14: Technical Safeguards
1. **Network Segmentation:** Demilitarized Zones (DMZs), Micro-segmentation for database clusters, and strict egress filtering.
2. **Multi-Factor Authentication (MFA):** Mandatory hardware/TOTP-based MFA for all privileged administrator access, database maintenance, and remote sessions.
3. **Data Loss Prevention (DLP):** Real-time monitoring and blocking of unauthorized transfer of customer PII (PAN, Aadhaar, account numbers).
4. **Vulnerability Assessment & Penetration Testing (VAPT):** Mandatory biannual VAPT on all internet-facing banking endpoints and annual red-teaming simulations.
5. **Key Management:** Cryptographic keys must be stored in FIPS 140-2 Level 3 compliant Hardware Security Modules (HSMs) located within India.
