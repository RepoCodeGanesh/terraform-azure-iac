"""
HappyTechies Cloud & AI Platform — Enterprise Confluence Publisher
==================================================================
Converts Markdown documents into native Atlassian Confluence Storage
XHTML format with rich tables, structured code macros, info panels,
and clean Visio diagrams, then updates Space [HT] via REST API.
"""

import os
import sys
import json
import base64
import re
import urllib.request
import urllib.error
import markdown
from pathlib import Path

CONFLUENCE_DOMAIN = "happytechies.atlassian.net"
SPACE_KEY = "HT"
DEFAULT_EMAIL = "richtextforganesh@outlook.com"

PAGES_MAP = [
    {"num": "01", "file": "01-space-overview-architecture.md", "title": "01. Azure AI Landing Zone & Enterprise Copilots Overview"},
    {"num": "02", "file": "02-workload-taxbot-india.md", "title": "02. Workload 1: TaxBot India (Serverless PaaS Architecture)"},
    {"num": "03", "file": "03-workload-bank-compliance-aks.md", "title": "03. Workload 2: BankCompliance AI (Cloud-Native AKS Copilot)"},
    {"num": "04", "file": "04-finops-and-zero-cost-strategy.md", "title": "04. FinOps & Near-Zero Idle Cost Strategy"},
    {"num": "05", "file": "05-cicd-wif-operations-runbook.md", "title": "05. Dual CI/CD, Workload Identity & Operations Runbook"},
    {"num": "06", "file": "06-enterprise-naming-and-tagging-standards.md", "title": "06. Enterprise Naming & Tagging Standards Specification"},
    {"num": "07", "file": "07-security-governance-zero-trust.md", "title": "07. Enterprise Security, Zero-Trust Architecture & Governance"},
    {"num": "08", "file": "08-cloud-platform-technical-strategy.md", "title": "08. Cloud & AI Platform Technical Strategy"},
    {"num": "09", "file": "09-enterprise-network-and-traffic-flow.md", "title": "09. Enterprise Network Topology, Packet Routing & DNS Spec"},
    {"num": "10", "file": "10-incident-post-mortems-and-rca-knowledge-base.md", "title": "10. Master Incident Post-Mortems & Root Cause Analysis (RCA)"},
    {"num": "11", "file": "11-bank-compliance-troubleshooting-learnings.md", "title": "11. BankCompliance AI: Engineering Learnings & Troubleshooting"},
    {"num": "12", "file": "12-fine-tuning-and-private-slm-guide.md", "title": "12. Parameter-Efficient Fine-Tuning (LoRA), Sovereign SLMs & GenAIOps"}
]

def markdown_to_confluence_xhtml(md_text: str) -> str:
    code_blocks = []
    def save_code_block(match):
        lang = (match.group(1) or "none").strip().lower()
        if lang in ["text", "ascii", ""]:
            lang = "none"
        elif lang in ["bash", "sh", "powershell", "shell", "posh"]:
            lang = "bash"
        elif lang in ["python", "py"]:
            lang = "python"
        elif lang in ["json"]:
            lang = "json"
        elif lang in ["yaml", "yml"]:
            lang = "yaml"
        elif lang in ["xml", "html"]:
            lang = "xml"
        elif lang in ["diff"]:
            lang = "diff"
        
        code = match.group(2)
        idx = len(code_blocks)
        code_blocks.append((lang, code))
        return f"___CODE_BLOCK_{idx}___"

    processed_md = re.sub(r'```([a-zA-Z0-9_-]*)\r?\n(.*?)```', save_code_block, md_text, flags=re.DOTALL)

    html = markdown.markdown(processed_md, extensions=['tables', 'sane_lists'])

    for idx, (lang, code) in enumerate(code_blocks):
        clean_code = code.replace("]]>", "]]]]><![CDATA[>")
        macro = (
            f'<ac:structured-macro ac:name="code">'
            f'<ac:parameter ac:name="language">{lang}</ac:parameter>'
            f'<ac:parameter ac:name="theme">Midnight</ac:parameter>'
            f'<ac:parameter ac:name="linenumbers">false</ac:parameter>'
            f'<ac:plain-text-body><![CDATA[{clean_code}]]></ac:plain-text-body>'
            f'</ac:structured-macro>'
        )
        html = html.replace(f"<p>___CODE_BLOCK_{idx}___</p>", macro)
        html = html.replace(f"___CODE_BLOCK_{idx}___", macro)

    html = html.replace('<table>', '<table class="wrapped confluenceTable">')
    html = html.replace('<th>', '<th class="confluenceTh" style="background-color: #f4f5f7; font-weight: bold; border: 1px solid #dfe1e6;">')
    html = html.replace('<td>', '<td class="confluenceTd" style="border: 1px solid #dfe1e6; padding: 6px 10px;">')

    def replace_callout(match):
        content = match.group(1)
        macro_type = "info"
        title = "Note"
        if "[!WARNING]" in content or "[!CAUTION]" in content:
            macro_type = "warning"
            title = "Warning"
            content = re.sub(r'\[!(WARNING|CAUTION)\]', '', content)
        elif "[!IMPORTANT]" in content:
            macro_type = "info"
            title = "Important"
            content = re.sub(r'\[!IMPORTANT\]', '', content)
        elif "[!TIP]" in content:
            macro_type = "tip"
            title = "Tip"
            content = re.sub(r'\[!TIP\]', '', content)
        elif "[!NOTE]" in content:
            macro_type = "info"
            title = "Note"
        return (
            f'<ac:structured-macro ac:name="{macro_type}">'
            f'<ac:parameter ac:name="title">{title}</ac:parameter>'
            f'<ac:rich-text-body><p>{content.strip()}</p></ac:rich-text-body>'
            f'</ac:structured-macro>'
        )

    def replace_image_tag(match):
        img_src = match.group(1)
        filename = Path(img_src).name
        return f'<p style="text-align: center;"><ac:image ac:align="center" ac:layout="center" ac:width="950"><ri:attachment ri:filename="{filename}" /></ac:image></p>'

    # Convert HTML img tags generated by markdown into native Confluence image macros
    html = re.sub(r'<p>\s*<img [^>]*src=[\"\'](.*?)[\"\'][^>]*\s*/?>\s*</p>', replace_image_tag, html)
    html = re.sub(r'<img [^>]*src=[\"\'](.*?)[\"\'][^>]*\s*/?>', replace_image_tag, html)
    html = re.sub(r'<blockquote>\s*<p>(.*?)</p>\s*</blockquote>', replace_callout, html, flags=re.DOTALL)
    return html

def get_auth_header(email: str, api_token: str) -> str:
    auth_str = f"{email}:{api_token}"
    b64_val = base64.b64encode(auth_str.encode()).decode()
    return f"Basic {b64_val}"

def make_request(url: str, method: str, headers: dict, data: dict = None):
    req = urllib.request.Request(url, method=method)
    for k, v in headers.items():
        req.add_header(k, v)
    if data:
        json_data = json.dumps(data).encode("utf-8")
        req.data = json_data
        req.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        err_body = e.read().decode()
        print(f"HTTP Error {e.code}: {err_body}")
        return None

def publish_all(email: str, api_token: str):
    docs_dir = Path(__file__).resolve().parent.parent / "docs" / "confluence"
    auth = get_auth_header(email, api_token)
    headers = {"Authorization": auth, "Accept": "application/json"}

    print(f"=================================================================")
    print(f"  HappyTechies Confluence Cloud Publisher -> Space [{SPACE_KEY}]")
    print(f"=================================================================")

    list_url = f"https://{CONFLUENCE_DOMAIN}/wiki/rest/api/content?spaceKey={SPACE_KEY}&limit=100&expand=version"
    res = make_request(list_url, "GET", headers)
    existing_pages = {}
    if res and "results" in res:
        for p in res["results"]:
            existing_pages[p["title"].strip()] = {
                "id": p["id"],
                "version": p["version"]["number"]
            }

    for item in PAGES_MAP:
        file_path = docs_dir / item["file"]
        if not file_path.exists():
            continue

        raw_md = file_path.read_text(encoding="utf-8")
        storage_html = markdown_to_confluence_xhtml(raw_md)
        title = item["title"]

        if title in existing_pages:
            page_id = existing_pages[title]["id"]
            current_ver = existing_pages[title]["version"]
            update_url = f"https://{CONFLUENCE_DOMAIN}/wiki/rest/api/content/{page_id}"
            payload = {
                "version": {"number": current_ver + 1},
                "title": title,
                "type": "page",
                "space": {"key": SPACE_KEY},
                "body": {
                    "storage": {
                        "value": storage_html,
                        "representation": "storage"
                    }
                }
            }
            resp = make_request(update_url, "PUT", headers, payload)
            if resp:
                print(f"[UPDATED] {item['num']}. {title} (v{current_ver + 1})")
        else:
            create_url = f"https://{CONFLUENCE_DOMAIN}/wiki/rest/api/content"
            payload = {
                "type": "page",
                "title": title,
                "space": {"key": SPACE_KEY},
                "body": {
                    "storage": {
                        "value": storage_html,
                        "representation": "storage"
                    }
                }
            }
            resp = make_request(create_url, "POST", headers, payload)
            if resp:
                print(f"[CREATED] {item['num']}. {title} (ID: {resp.get('id')})")

    print("Confluence Synchronization Completed Successfully.")

if __name__ == "__main__":
    email = os.environ.get("CONFLUENCE_EMAIL", DEFAULT_EMAIL)
    token = os.environ.get("CONFLUENCE_API_TOKEN")
    
    if not token and len(sys.argv) > 1:
        token = sys.argv[1]
        
    if not token:
        print("Error: Confluence API token required via CONFLUENCE_API_TOKEN env or command line argument.")
        sys.exit(1)

    publish_all(email, token)
