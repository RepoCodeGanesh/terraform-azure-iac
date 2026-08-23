"""
Reorganize Confluence Space [HT] into a Clean 3-Tier Enterprise Tree
====================================================================
Arranges all 12 documents under structured Section Folders in the Confluence sidebar:
- Section 1: Enterprise Cloud Platform & Network Infrastructure
- Section 2: Enterprise AI Applications (Workloads)
- Section 3: SRE, FinOps, MLOps & Master Post-Mortems
"""

import os
import sys
import urllib.request
import json
import base64

CONFLUENCE_DOMAIN = "happytechies.atlassian.net"
SPACE_KEY = "HT"
EMAIL = os.environ.get("CONFLUENCE_EMAIL", "richtextforganesh@outlook.com")
TOKEN = os.environ.get("CONFLUENCE_API_TOKEN")

if not TOKEN and len(sys.argv) > 1:
    TOKEN = sys.argv[1]

ROOT_HOME_ID = "7602285"
SECTION_1_ID = "7766033"
SECTION_2_ID = "7766050"

SECTION_MAPPING = {
    "10289154": SECTION_1_ID,  # Page 01 (CAF Blueprint)
    "10387465": SECTION_1_ID,  # Page 08 (Platform Strategy)
    "10321962": SECTION_1_ID,  # Page 09 (Network & Ingress Spec)
    "10321945": SECTION_1_ID,  # Page 06 (Naming & Tagging)
    "10452993": SECTION_1_ID,  # Page 07 (Security & Zero-Trust)
    "7602371": SECTION_2_ID,   # Page 02 (TaxBot India)
    "7700481": SECTION_2_ID,   # Page 03 (BankCompliance AI)
}

SECTION_3_PAGE_IDS = [
    "10321929",  # Page 04 (FinOps)
    "10420225",  # Page 05 (CI/CD & WIF)
    "10387482",  # Page 10 (Master RCA Post-Mortems)
    "10485761",  # Page 11 (BankCompliance Troubleshooting)
    "10420242",  # Page 12 (LoRA Fine-Tuning & Sovereign SLMs)
]

def get_auth_header():
    auth_str = f"{EMAIL}:{TOKEN}"
    return f"Basic {base64.b64encode(auth_str.encode()).decode()}"

def make_request(url, method="GET", data=None):
    req = urllib.request.Request(url, method=method)
    req.add_header("Authorization", get_auth_header())
    req.add_header("Accept", "application/json")
    if data:
        req.data = json.dumps(data).encode("utf-8")
        req.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        print(f"HTTP Error {e.code}: {e.read().decode()}")
        return None

def get_or_create_section_3():
    list_url = f"https://{CONFLUENCE_DOMAIN}/wiki/rest/api/content?spaceKey={SPACE_KEY}&limit=100"
    res = make_request(list_url)
    sec3_title = "Section 3: SRE, FinOps, MLOps & Incident Post-Mortems"
    
    if res:
        for p in res.get("results", []):
            if p["title"].strip() == sec3_title:
                return p["id"]
    
    create_url = f"https://{CONFLUENCE_DOMAIN}/wiki/rest/api/content"
    payload = {
        "type": "page",
        "title": sec3_title,
        "space": {"key": SPACE_KEY},
        "ancestors": [{"id": ROOT_HOME_ID}],
        "body": {
            "storage": {
                "value": "<p>Enterprise SRE Observability, FinOps Scale-to-Zero, CI/CD Governance, and Master Root Cause Analyses (RCAs).</p>",
                "representation": "storage"
            }
        }
    }
    resp = make_request(create_url, "POST", payload)
    if resp:
        return resp["id"]
    return None

def move_page_to_parent(page_id, parent_id):
    get_url = f"https://{CONFLUENCE_DOMAIN}/wiki/rest/api/content/{page_id}?expand=body.storage,version"
    page_data = make_request(get_url)
    if not page_data:
        return False
    
    current_ver = page_data["version"]["number"]
    title = page_data["title"]
    body = page_data["body"]["storage"]["value"]

    payload = {
        "version": {"number": current_ver + 1},
        "title": title,
        "type": "page",
        "space": {"key": SPACE_KEY},
        "ancestors": [{"id": parent_id}],
        "body": {
            "storage": {
                "value": body,
                "representation": "storage"
            }
        }
    }
    update_url = f"https://{CONFLUENCE_DOMAIN}/wiki/rest/api/content/{page_id}"
    resp = make_request(update_url, "PUT", payload)
    if resp:
        print(f"[REORGANIZED] Moved '{title}' -> Parent ID: {parent_id}")
        return True
    return False

if __name__ == "__main__":
    if not TOKEN:
        print("Error: CONFLUENCE_API_TOKEN required.")
        sys.exit(1)

    sec3_id = get_or_create_section_3()
    if sec3_id:
        for pid in SECTION_3_PAGE_IDS:
            SECTION_MAPPING[pid] = sec3_id

    for page_id, parent_id in SECTION_MAPPING.items():
        move_page_to_parent(page_id, parent_id)
