"""
BankCompliance AI — Regulatory Data Lake Sync Engine
=====================================================
Downloads statutory RBI Master Direction PDFs and uploads them
to Azure Blob Storage (sthtbankcpcin01 / rbi-raw-pdfs).
"""

import os
import sys
import ssl
import hashlib
import subprocess
import urllib.request
from pathlib import Path

# Force UTF-8 on Windows consoles
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

ACCOUNT_NAME = "sthtbankcpcin01"
CONTAINER_NAME = "rbi-raw-pdfs"
SUBSCRIPTION_ID = "f4ffefe1-d689-4059-969c-ccc73e2a11d4"
RESOURCE_GROUP = "rg-ht-bankc-p-cin-01"

TARGET_CIRCULARS = [
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
        "filename": "rbi-master-direction-frauds-classification.pdf",
        "title": "Master Direction on Frauds - Classification and Reporting",
        "circular_no": "RBI/DBS/2016-17/28",
        "url": "https://rbidocs.rbi.org.in/rdocs/notification/PDFs/28MDFRAUDSC874E66270E4461CB7B67B7BB1BC45EF.PDF"
    },
    {
        "filename": "rbi-master-direction-digital-payment-security.pdf",
        "title": "Master Direction on Digital Payment Security Controls",
        "circular_no": "RBI/2020-21/74",
        "url": "https://rbidocs.rbi.org.in/rdocs/notification/PDFs/MDDPSEC03022021.PDF"
    },
    {
        "filename": "rbi-guidelines-digital-lending.pdf",
        "title": "Guidelines on Digital Lending",
        "circular_no": "RBI/2022-23/111",
        "url": "https://rbidocs.rbi.org.in/rdocs/notification/PDFs/DLGUIDELINES02092022.PDF"
    }
]

def get_storage_key() -> str:
    cmd = [
        "az", "storage", "account", "keys", "list",
        "--account-name", ACCOUNT_NAME,
        "--resource-group", RESOURCE_GROUP,
        "--subscription", SUBSCRIPTION_ID,
        "--query", "[0].value",
        "-o", "tsv"
    ]
    res = subprocess.run(cmd, capture_output=True, text=True, check=True, shell=True)
    return res.stdout.strip()

def download_and_upload():
    print(f"🚀 Starting Data Lake Sync to {ACCOUNT_NAME}/{CONTAINER_NAME}...")
    storage_key = get_storage_key()

    temp_dir = Path(__file__).resolve().parent / "raw_pdfs"
    temp_dir.mkdir(parents=True, exist_ok=True)

    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }

    uploaded_count = 0
    for item in TARGET_CIRCULARS:
        dest_pdf = temp_dir / item["filename"]
        print(f"📥 Fetching: {item['filename']} [{item['circular_no']}]...")
        try:
            req = urllib.request.Request(item["url"], headers=headers)
            with urllib.request.urlopen(req, context=ctx, timeout=25) as resp:
                data = resp.read()
                dest_pdf.write_bytes(data)
                sha256 = hashlib.sha256(data).hexdigest()
                size_kb = len(data) / 1024
                print(f"   ✓ Downloaded: {size_kb:.1f} KB (SHA-256: {sha256[:16]}...)")

            # Upload to Azure Blob Storage
            print(f"☁️ Uploading to Azure Blob Storage...")
            upload_cmd = [
                "az", "storage", "blob", "upload",
                "--account-name", ACCOUNT_NAME,
                "--account-key", storage_key,
                "--container-name", CONTAINER_NAME,
                "--file", str(dest_pdf),
                "--name", item["filename"],
                "--overwrite", "true",
                "--content-type", "application/pdf"
            ]
            subprocess.run(upload_cmd, capture_output=True, text=True, check=True, shell=True)
            print(f"   ✅ Blob Live: https://{ACCOUNT_NAME}.blob.core.windows.net/{CONTAINER_NAME}/{item['filename']}")
            uploaded_count += 1
        except Exception as e:
            print(f"   ⚠️ Sync warning for {item['filename']}: {e}")

    print(f"\n🎉 Regulatory Data Lake Sync Complete! {uploaded_count}/{len(TARGET_CIRCULARS)} PDFs populated in cloud storage.")

if __name__ == "__main__":
    download_and_upload()
