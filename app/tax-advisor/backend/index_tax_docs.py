"""
TaxBot India — Statutory Tax Documents Indexing Pipeline
=========================================================
Provisions index 'tax-docs' on Azure AI Search (srch-ht-taxb-p-cin-01)
and indexes all 10 Indian Tax Code circulars from app/tax-advisor/documents/.
"""

import os
import sys
import re
import json
import urllib.request
import urllib.parse
from pathlib import Path

# Force UTF-8 on Windows consoles
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

SEARCH_SERVICE = os.environ.get("SEARCH_SERVICE_NAME", "srch-ht-taxb-p-cin-01")
SEARCH_ENDPOINT = f"https://{SEARCH_SERVICE}.search.windows.net"
INDEX_NAME = "tax-docs"
API_VERSION = "2023-11-01"

def get_admin_key() -> str:
    """Fetch search admin key from env or via az CLI."""
    key = os.environ.get("AZURE_SEARCH_KEY")
    if key:
        return key
    import subprocess
    cmd = [
        "az", "search", "admin-key", "show",
        "--service-name", SEARCH_SERVICE,
        "--resource-group", "rg-ht-taxb-p-cin-01",
        "--subscription", "f4ffefe1-d689-4059-969c-ccc73e2a11d4",
        "--query", "primaryKey",
        "-o", "tsv"
    ]
    res = subprocess.run(cmd, capture_output=True, text=True, check=True, shell=True)
    return res.stdout.strip()

def create_index_if_not_exists(admin_key: str):
    """Create the tax-docs search index if it doesn't exist."""
    url = f"{SEARCH_ENDPOINT}/indexes/{INDEX_NAME}?api-version={API_VERSION}"
    headers = {
        "api-key": admin_key,
        "Content-Type": "application/json"
    }

    # Index schema definition
    index_schema = {
        "name": INDEX_NAME,
        "fields": [
            {"name": "id", "type": "Edm.String", "key": True, "searchable": False, "filterable": True, "sortable": False, "facetable": False},
            {"name": "title", "type": "Edm.String", "searchable": True, "filterable": True, "sortable": True, "facetable": False},
            {"name": "content", "type": "Edm.String", "searchable": True, "filterable": False, "sortable": False, "facetable": False},
            {"name": "source", "type": "Edm.String", "searchable": True, "filterable": True, "sortable": True, "facetable": True},
            {"name": "category", "type": "Edm.String", "searchable": True, "filterable": True, "sortable": True, "facetable": True}
        ]
    }

    req = urllib.request.Request(url, data=json.dumps(index_schema).encode("utf-8"), headers=headers, method="PUT")
    try:
        with urllib.request.urlopen(req) as resp:
            print(f"✅ Index '{INDEX_NAME}' provisioned successfully (HTTP {resp.status})")
    except urllib.error.HTTPError as e:
        print(f"❌ Failed creating index: {e.code} - {e.read().decode('utf-8')}")
        raise

def chunk_markdown_file(file_path: Path) -> list:
    """Split markdown into logical section chunks based on headers."""
    content = file_path.read_text(encoding="utf-8")
    lines = content.splitlines()
    title = file_path.stem.replace("-", " ").title()
    category = "Direct Taxes"

    chunks = []
    current_header = title
    current_lines = []

    for line in lines:
        if line.startswith("# ") and title == file_path.stem.replace("-", " ").title():
            title = line.replace("# ", "").strip()
        elif line.startswith("## "):
            if current_lines:
                chunk_text = "\n".join(current_lines).strip()
                if len(chunk_text) > 80:
                    chunks.append({
                        "header": current_header,
                        "text": chunk_text
                    })
                current_lines = []
            current_header = line.replace("## ", "").strip()
        else:
            current_lines.append(line)

    if current_lines:
        chunk_text = "\n".join(current_lines).strip()
        if len(chunk_text) > 80:
            chunks.append({
                "header": current_header,
                "text": chunk_text
            })

    return title, category, chunks

def upload_documents(admin_key: str, docs: list):
    """Upload documents batch to Azure AI Search."""
    url = f"{SEARCH_ENDPOINT}/indexes/{INDEX_NAME}/docs/index?api-version={API_VERSION}"
    headers = {
        "api-key": admin_key,
        "Content-Type": "application/json"
    }

    payload = {
        "value": [
            {
                "@search.action": "mergeOrUpload",
                **doc
            }
            for doc in docs
        ]
    }

    req = urllib.request.Request(url, data=json.dumps(payload).encode("utf-8"), headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req) as resp:
            result = json.loads(resp.read().decode("utf-8"))
            succeeded = sum(1 for item in result.get("value", []) if item.get("status"))
            print(f"✅ Uploaded {succeeded}/{len(docs)} document chunks successfully.")
    except urllib.error.HTTPError as e:
        print(f"❌ Failed uploading documents: {e.code} - {e.read().decode('utf-8')}")
        raise

def main():
    print("🚀 Starting TaxBot India Document Indexing Pipeline...")
    admin_key = get_admin_key()
    create_index_if_not_exists(admin_key)

    docs_dir = Path(__file__).resolve().parent.parent / "documents"
    if not docs_dir.exists():
        docs_dir = Path("app/tax-advisor/documents")

    md_files = sorted(docs_dir.glob("*.md"))
    print(f"📂 Found {len(md_files)} markdown tax documents in {docs_dir}")

    all_docs = []
    for md_file in md_files:
        title, category, chunks = chunk_markdown_file(md_file)
        for idx, chunk in enumerate(chunks):
            doc_id = re.sub(r'[^a-zA-Z0-9_\-=]', '_', f"{md_file.stem}_{idx}")
            all_docs.append({
                "id": doc_id,
                "title": f"{title} - {chunk['header']}",
                "content": chunk["text"],
                "source": md_file.name,
                "category": category
            })

    print(f"📦 Generated {len(all_docs)} search chunks from {len(md_files)} files.")
    upload_documents(admin_key, all_docs)
    print("🎉 Azure AI Search Indexing Complete!")

if __name__ == "__main__":
    main()
