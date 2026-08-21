"""
RBI Master Direction PDF Downloader & Data Lake Ingestion Tool
==============================================================
Downloads official Reserve Bank of India (RBI) signed Master Direction PDFs
and prepares them for upload to Azure Blob Storage (sthtbankcpcin01 / rbi-raw-pdfs).
"""

import os
import urllib.request
import ssl
from pathlib import Path

# Official RBI Master Direction PDF Sources
RBI_PDF_CATALOG = [
    {
        "filename": "rbi-master-direction-kyc-aml.pdf",
        "title": "Master Direction - Know Your Customer (KYC) Direction, 2016",
        "circular_no": "RBI/DBR/2016-17/14",
        "url": "https://rbidocs.rbi.org.in/rdocs/notification/PDFs/14MDKYCEED6320098F24BB29E57EEA419B86D49.PDF"
    },
    {
        "filename": "rbi-master-direction-it-governance.pdf",
        "title": "Master Direction on Information Technology Governance & Cybersecurity",
        "circular_no": "RBI/2023-24/108",
        "url": "https://rbidocs.rbi.org.in/rdocs/notification/PDFs/108MDITGOVERNANCE07112023.PDF"
    },
    {
        "filename": "rbi-master-direction-it-outsourcing.pdf",
        "title": "Master Direction on Outsourcing of Information Technology Services",
        "circular_no": "RBI/2023-24/102",
        "url": "https://rbidocs.rbi.org.in/rdocs/notification/PDFs/102MDOUTSOURCING10042023.PDF"
    },
    {
        "filename": "rbi-master-direction-credit-debit-cards.pdf",
        "title": "Master Direction - Credit Card and Debit Card Issuance & Conduct",
        "circular_no": "RBI/2022-23/92",
        "url": "https://rbidocs.rbi.org.in/rdocs/notification/PDFs/62MDCC21042022137B5EEF11FB421495A2AECEFAAA67DA.PDF"
    },
    {
        "filename": "rbi-guidelines-digital-lending.pdf",
        "title": "Guidelines on Digital Lending - Direct Fund Flow & FLDG Mandates",
        "circular_no": "RBI/2022-23/111",
        "url": "https://rbidocs.rbi.org.in/rdocs/notification/PDFs/DLGUIDELINES02092022.PDF"
    }
]

def download_pdfs(target_dir: Path = None):
    if target_dir is None:
        target_dir = Path(__file__).resolve().parent / "raw_pdfs"

    target_dir.mkdir(parents=True, exist_ok=True)
    print(f"[*] Downloading official RBI Master Direction PDFs to: {target_dir}")

    # Configure permissive SSL context for government public documents
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    for item in RBI_PDF_CATALOG:
        dest_path = target_dir / item["filename"]
        print(f" -> Fetching [{item['circular_no']}] {item['title']}...")
        try:
            req = urllib.request.Request(item["url"], headers=headers)
            with urllib.request.urlopen(req, context=ctx, timeout=30) as resp, open(dest_path, "wb") as f:
                f.write(resp.read())
            size_kb = dest_path.stat().st_size / 1024
            print(f"    [OK] Saved {item['filename']} ({size_kb:.1f} KB)")
        except Exception as e:
            print(f"    [!] Download notice: {e} (Bundled Markdown fallback remains active)")

    print("[*] Completed RBI Master Direction Data Lake preparation.")

if __name__ == "__main__":
    download_pdfs()
