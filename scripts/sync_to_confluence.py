"""
HappyTechies Cloud & AI Platform -- Enterprise Confluence Publisher
==================================================================
Converts Markdown documents into native Atlassian Confluence Storage
XHTML format with rich tables, structured code macros, info panels,
and clean ASCII diagrams, then updates Space [HT] via REST API.
"""

import os
import sys
import json
import base64
import re
import subprocess
import urllib.request
import urllib.error
import markdown
from pathlib import Path

# Ensure UTF-8 output on Windows console
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

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

HOMEPAGE_STORAGE = """
<ac:structured-macro ac:name="panel">
    <ac:parameter ac:name="bgColor">#F4F5F7</ac:parameter>
    <ac:rich-text-body>
        <h2><strong>HappyTechies Cloud &amp; AI Platform -- Enterprise Engineering Wiki</strong></h2>
        <p>Production enterprise documentation suite for the Microsoft Cloud Adoption Framework (CAF) multi-subscription Azure Landing Zone, Multi-Root Terraform IaC infrastructure, Zero-Trust security governance, FinOps scale-to-zero engine, and AI copilot workloads (TaxBot India &amp; BankCompliance AI).</p>
    </ac:rich-text-body>
</ac:structured-macro>

<hr />

<h2>Enterprise AI Applications (Workloads)</h2>
<table class="wrapped confluenceTable">
    <tbody>
        <tr>
            <th class="confluenceTh" style="background-color: #f4f5f7; font-weight: bold; border: 1px solid #dfe1e6;">Workload</th>
            <th class="confluenceTh" style="background-color: #f4f5f7; font-weight: bold; border: 1px solid #dfe1e6;">Production Endpoint</th>
            <th class="confluenceTh" style="background-color: #f4f5f7; font-weight: bold; border: 1px solid #dfe1e6;">Architecture</th>
            <th class="confluenceTh" style="background-color: #f4f5f7; font-weight: bold; border: 1px solid #dfe1e6;">Specification Document</th>
        </tr>
        <tr>
            <td class="confluenceTd" style="border: 1px solid #dfe1e6; padding: 6px 10px;"><strong>TaxBot India</strong></td>
            <td class="confluenceTd" style="border: 1px solid #dfe1e6; padding: 6px 10px;"><a href="https://www.mytaxbot.site">https://www.mytaxbot.site</a></td>
            <td class="confluenceTd" style="border: 1px solid #dfe1e6; padding: 6px 10px;">Serverless PaaS (Python Function App Y1 + OpenAI + AI Search + Cosmos DB)</td>
            <td class="confluenceTd" style="border: 1px solid #dfe1e6; padding: 6px 10px;"><ac:link><ri:page ri:content-title="02. Workload 1: TaxBot India (Serverless PaaS Architecture)" /><ac:plain-text-link-body><![CDATA[02. Workload 1: TaxBot India]]></ac:plain-text-link-body></ac:link></td>
        </tr>
        <tr>
            <td class="confluenceTd" style="border: 1px solid #dfe1e6; padding: 6px 10px;"><strong>BankCompliance AI</strong></td>
            <td class="confluenceTd" style="border: 1px solid #dfe1e6; padding: 6px 10px;"><a href="https://bank.mytaxbot.site">https://bank.mytaxbot.site</a></td>
            <td class="confluenceTd" style="border: 1px solid #dfe1e6; padding: 6px 10px;">Cloud-Native Kubernetes (AKS Free Tier + Qdrant 4GB CSI + LiteLLM Gateway)</td>
            <td class="confluenceTd" style="border: 1px solid #dfe1e6; padding: 6px 10px;"><ac:link><ri:page ri:content-title="03. Workload 2: BankCompliance AI (Cloud-Native AKS Copilot)" /><ac:plain-text-link-body><![CDATA[03. Workload 2: BankCompliance AI]]></ac:plain-text-link-body></ac:link></td>
        </tr>
    </tbody>
</table>

<hr />

<h2>Documentation Sections &amp; Specifications Matrix</h2>

<h3>Section 1: Enterprise Cloud, Network &amp; Security Foundation</h3>
<table class="wrapped confluenceTable">
    <tbody>
        <tr>
            <th class="confluenceTh" style="background-color: #f4f5f7; font-weight: bold; border: 1px solid #dfe1e6;">#</th>
            <th class="confluenceTh" style="background-color: #f4f5f7; font-weight: bold; border: 1px solid #dfe1e6;">Document Title</th>
            <th class="confluenceTh" style="background-color: #f4f5f7; font-weight: bold; border: 1px solid #dfe1e6;">Key Architecture Focus</th>
        </tr>
        <tr>
            <td class="confluenceTd" style="border: 1px solid #dfe1e6; padding: 6px 10px;">01</td>
            <td class="confluenceTd" style="border: 1px solid #dfe1e6; padding: 6px 10px;"><ac:link><ri:page ri:content-title="01. Azure AI Landing Zone & Enterprise Copilots Overview" /></ac:link></td>
            <td class="confluenceTd" style="border: 1px solid #dfe1e6; padding: 6px 10px;">4-Subscription CAF Model, Management Groups, Remote State Map</td>
        </tr>
        <tr>
            <td class="confluenceTd" style="border: 1px solid #dfe1e6; padding: 6px 10px;">08</td>
            <td class="confluenceTd" style="border: 1px solid #dfe1e6; padding: 6px 10px;"><ac:link><ri:page ri:content-title="08. Cloud & AI Platform Technical Strategy" /></ac:link></td>
            <td class="confluenceTd" style="border: 1px solid #dfe1e6; padding: 6px 10px;">Multi-Root Terraform Architecture, Monorepo State Isolation</td>
        </tr>
        <tr>
            <td class="confluenceTd" style="border: 1px solid #dfe1e6; padding: 6px 10px;">09</td>
            <td class="confluenceTd" style="border: 1px solid #dfe1e6; padding: 6px 10px;"><ac:link><ri:page ri:content-title="09. Enterprise Network Topology, Packet Routing & DNS Spec" /></ac:link></td>
            <td class="confluenceTd" style="border: 1px solid #dfe1e6; padding: 6px 10px;">Cloudflare Full SSL, APIM Ingress, Azure CNI Overlay, ClusterIP Zero-Egress</td>
        </tr>
        <tr>
            <td class="confluenceTd" style="border: 1px solid #dfe1e6; padding: 6px 10px;">06</td>
            <td class="confluenceTd" style="border: 1px solid #dfe1e6; padding: 6px 10px;"><ac:link><ri:page ri:content-title="06. Enterprise Naming & Tagging Standards Specification" /></ac:link></td>
            <td class="confluenceTd" style="border: 1px solid #dfe1e6; padding: 6px 10px;">CAF Naming Dictionaries, Hyphenated/Compact Rules, Tag Initiatives</td>
        </tr>
        <tr>
            <td class="confluenceTd" style="border: 1px solid #dfe1e6; padding: 6px 10px;">07</td>
            <td class="confluenceTd" style="border: 1px solid #dfe1e6; padding: 6px 10px;"><ac:link><ri:page ri:content-title="07. Enterprise Security, Zero-Trust Architecture & Governance" /></ac:link></td>
            <td class="confluenceTd" style="border: 1px solid #dfe1e6; padding: 6px 10px;">DPDP Act PII Sanitizer, Azure AI Content Safety, OPA Gatekeeper</td>
        </tr>
    </tbody>
</table>

<h3>Section 2: Enterprise CI/CD, FinOps &amp; SRE Post-Mortems</h3>
<table class="wrapped confluenceTable">
    <tbody>
        <tr>
            <th class="confluenceTh" style="background-color: #f4f5f7; font-weight: bold; border: 1px solid #dfe1e6;">#</th>
            <th class="confluenceTh" style="background-color: #f4f5f7; font-weight: bold; border: 1px solid #dfe1e6;">Document Title</th>
            <th class="confluenceTh" style="background-color: #f4f5f7; font-weight: bold; border: 1px solid #dfe1e6;">Key Architecture Focus</th>
        </tr>
        <tr>
            <td class="confluenceTd" style="border: 1px solid #dfe1e6; padding: 6px 10px;">05</td>
            <td class="confluenceTd" style="border: 1px solid #dfe1e6; padding: 6px 10px;"><ac:link><ri:page ri:content-title="05. Dual CI/CD, Workload Identity & Operations Runbook" /></ac:link></td>
            <td class="confluenceTd" style="border: 1px solid #dfe1e6; padding: 6px 10px;">Entra ID WIF OIDC Exchange, 3-Tier Decoupled CI/CD, Caller/Called Pattern</td>
        </tr>
        <tr>
            <td class="confluenceTd" style="border: 1px solid #dfe1e6; padding: 6px 10px;">04</td>
            <td class="confluenceTd" style="border: 1px solid #dfe1e6; padding: 6px 10px;"><ac:link><ri:page ri:content-title="04. FinOps & Near-Zero Idle Cost Strategy" /></ac:link></td>
            <td class="confluenceTd" style="border: 1px solid #dfe1e6; padding: 6px 10px;">Master Cost Matrix ($0.00 Idle), Ephemeral OS, KEDA Scale-to-Zero</td>
        </tr>
        <tr>
            <td class="confluenceTd" style="border: 1px solid #dfe1e6; padding: 6px 10px;">10</td>
            <td class="confluenceTd" style="border: 1px solid #dfe1e6; padding: 6px 10px;"><ac:link><ri:page ri:content-title="10. Master Incident Post-Mortems & Root Cause Analysis (RCA)" /></ac:link></td>
            <td class="confluenceTd" style="border: 1px solid #dfe1e6; padding: 6px 10px;">26 Production SRE Incident Post-Mortems (5-Whys, Diffs, Permanent Fixes)</td>
        </tr>
        <tr>
            <td class="confluenceTd" style="border: 1px solid #dfe1e6; padding: 6px 10px;">11</td>
            <td class="confluenceTd" style="border: 1px solid #dfe1e6; padding: 6px 10px;"><ac:link><ri:page ri:content-title="11. BankCompliance AI: Engineering Learnings & Troubleshooting" /></ac:link></td>
            <td class="confluenceTd" style="border: 1px solid #dfe1e6; padding: 6px 10px;">AKS Pod Troubleshooting, APIM URL Rewriting, CSI Volume Locks</td>
        </tr>
    </tbody>
</table>

<h3>Section 3: Enterprise AI Workloads, MLOps &amp; Sovereign Inference</h3>
<table class="wrapped confluenceTable">
    <tbody>
        <tr>
            <th class="confluenceTh" style="background-color: #f4f5f7; font-weight: bold; border: 1px solid #dfe1e6;">#</th>
            <th class="confluenceTh" style="background-color: #f4f5f7; font-weight: bold; border: 1px solid #dfe1e6;">Document Title</th>
            <th class="confluenceTh" style="background-color: #f4f5f7; font-weight: bold; border: 1px solid #dfe1e6;">Key Architecture Focus</th>
        </tr>
        <tr>
            <td class="confluenceTd" style="border: 1px solid #dfe1e6; padding: 6px 10px;">02</td>
            <td class="confluenceTd" style="border: 1px solid #dfe1e6; padding: 6px 10px;"><ac:link><ri:page ri:content-title="02. Workload 1: TaxBot India (Serverless PaaS Architecture)" /></ac:link></td>
            <td class="confluenceTd" style="border: 1px solid #dfe1e6; padding: 6px 10px;">Function App Y1 + OpenAI gpt-5.4-nano + AI Search + Cosmos DB on mytaxbot.site</td>
        </tr>
        <tr>
            <td class="confluenceTd" style="border: 1px solid #dfe1e6; padding: 6px 10px;">03</td>
            <td class="confluenceTd" style="border: 1px solid #dfe1e6; padding: 6px 10px;"><ac:link><ri:page ri:content-title="03. Workload 2: BankCompliance AI (Cloud-Native AKS Copilot)" /></ac:link></td>
            <td class="confluenceTd" style="border: 1px solid #dfe1e6; padding: 6px 10px;">AKS Free Tier + Qdrant 4GB CSI + LiteLLM Gateway on bank.mytaxbot.site</td>
        </tr>
        <tr>
            <td class="confluenceTd" style="border: 1px solid #dfe1e6; padding: 6px 10px;">12</td>
            <td class="confluenceTd" style="border: 1px solid #dfe1e6; padding: 6px 10px;"><ac:link><ri:page ri:content-title="12. Parameter-Efficient Fine-Tuning (LoRA), Sovereign SLMs & GenAIOps" /></ac:link></td>
            <td class="confluenceTd" style="border: 1px solid #dfe1e6; padding: 6px 10px;">LoRA SFT Training Engine, In-Cluster Sovereign SLM (CPU), RAG vs LoRA Matrix</td>
        </tr>
    </tbody>
</table>
"""

SECTION_PAGES_STORAGE = {
    "Section 1: Cloud Platform and IaC Infrastructure": """
<h1>Cloud Platform and IaC Infrastructure Hub</h1>
<p>This section documents the enterprise-grade foundation of the <strong>HappyTechies Azure AI Landing Zone</strong>, including multi-subscription topology, Multi-Root Terraform IaC state governance, Zero-Trust security benchmarks, and automated FinOps engines.</p>
<hr />
<h2>Key Governance and Platform Areas</h2>
<table class="wrapped confluenceTable"><tbody>
<tr><th class="confluenceTh" style="background-color: #f4f5f7; font-weight: bold; border: 1px solid #dfe1e6;">Area</th><th class="confluenceTh" style="background-color: #f4f5f7; font-weight: bold; border: 1px solid #dfe1e6;">Description</th></tr>
<tr><td class="confluenceTd" style="border: 1px solid #dfe1e6; padding: 6px 10px;"><strong>Multi-Subscription Architecture</strong></td><td class="confluenceTd" style="border: 1px solid #dfe1e6; padding: 6px 10px;">Decoupled Bootstrap, Hub-prod, Shared-services, and Apps-prod subscriptions.</td></tr>
<tr><td class="confluenceTd" style="border: 1px solid #dfe1e6; padding: 6px 10px;"><strong>Multi-Root Terraform IaC</strong></td><td class="confluenceTd" style="border: 1px solid #dfe1e6; padding: 6px 10px;">Independent state files with zero blast-radius coupling.</td></tr>
<tr><td class="confluenceTd" style="border: 1px solid #dfe1e6; padding: 6px 10px;"><strong>Enterprise Naming &amp; Tagging</strong></td><td class="confluenceTd" style="border: 1px solid #dfe1e6; padding: 6px 10px;">Strict deterministic CAF abbreviation schemas and mandatory FinOps tags.</td></tr>
<tr><td class="confluenceTd" style="border: 1px solid #dfe1e6; padding: 6px 10px;"><strong>Zero-Trust Security &amp; IAM</strong></td><td class="confluenceTd" style="border: 1px solid #dfe1e6; padding: 6px 10px;">Passwordless Workload Identity Federation (WIF / OIDC) and OPA Gatekeeper.</td></tr>
<tr><td class="confluenceTd" style="border: 1px solid #dfe1e6; padding: 6px 10px;"><strong>FinOps &amp; Idle Cost Optimization</strong></td><td class="confluenceTd" style="border: 1px solid #dfe1e6; padding: 6px 10px;">Near-zero running cost (~$0.25/month idle) with automated cluster scheduling.</td></tr>
</tbody></table>
""",
    "Section 2: Enterprise AI Applications (Workloads)": """
<h1>Enterprise AI Applications Portfolio</h1>
<p>This section documents the business copilot applications deployed on the HappyTechies Cloud Platform. Each application is decoupled into its own standalone repository with dedicated CI/CD pipelines, runtime compute, and custom domain endpoints.</p>
<hr />
<h2>Active AI Copilots</h2>
<table class="wrapped confluenceTable"><tbody>
<tr><th class="confluenceTh" style="background-color: #f4f5f7; font-weight: bold; border: 1px solid #dfe1e6;">Application</th><th class="confluenceTh" style="background-color: #f4f5f7; font-weight: bold; border: 1px solid #dfe1e6;">Live Production URL</th><th class="confluenceTh" style="background-color: #f4f5f7; font-weight: bold; border: 1px solid #dfe1e6;">Compute Runtime</th><th class="confluenceTh" style="background-color: #f4f5f7; font-weight: bold; border: 1px solid #dfe1e6;">Vector DB / Storage</th></tr>
<tr><td class="confluenceTd" style="border: 1px solid #dfe1e6; padding: 6px 10px;"><strong>TaxBot India</strong></td><td class="confluenceTd" style="border: 1px solid #dfe1e6; padding: 6px 10px;"><a href="https://www.mytaxbot.site">https://www.mytaxbot.site</a></td><td class="confluenceTd" style="border: 1px solid #dfe1e6; padding: 6px 10px;">Python Linux Function App (Serverless Y1)</td><td class="confluenceTd" style="border: 1px solid #dfe1e6; padding: 6px 10px;">Azure AI Search &amp; Cosmos DB</td></tr>
<tr><td class="confluenceTd" style="border: 1px solid #dfe1e6; padding: 6px 10px;"><strong>BankCompliance AI</strong></td><td class="confluenceTd" style="border: 1px solid #dfe1e6; padding: 6px 10px;"><a href="https://bank.mytaxbot.site">https://bank.mytaxbot.site</a></td><td class="confluenceTd" style="border: 1px solid #dfe1e6; padding: 6px 10px;">Azure Kubernetes Service (AKS Free Tier)</td><td class="confluenceTd" style="border: 1px solid #dfe1e6; padding: 6px 10px;">Self-Hosted Qdrant (4GB CSI Managed Disk)</td></tr>
</tbody></table>
""",
    "Section 3: SRE, FinOps, MLOps & Incident Post-Mortems": """
<h1>SRE, FinOps, MLOps &amp; Incident Post-Mortems Hub</h1>
<p>Enterprise SRE Observability, FinOps Scale-to-Zero, CI/CD Governance, and Master Root Cause Analyses (RCAs).</p>
<hr />
<h2>Key SRE &amp; FinOps Governance Areas</h2>
<table class="wrapped confluenceTable"><tbody>
<tr><th class="confluenceTh" style="background-color: #f4f5f7; font-weight: bold; border: 1px solid #dfe1e6;">Domain</th><th class="confluenceTh" style="background-color: #f4f5f7; font-weight: bold; border: 1px solid #dfe1e6;">Focus Area</th><th class="confluenceTh" style="background-color: #f4f5f7; font-weight: bold; border: 1px solid #dfe1e6;">Reference Document</th></tr>
<tr><td class="confluenceTd" style="border: 1px solid #dfe1e6; padding: 6px 10px;"><strong>Post-Mortems</strong></td><td class="confluenceTd" style="border: 1px solid #dfe1e6; padding: 6px 10px;">26 Production SRE Incident RCAs with 5-Whys and permanent code diffs</td><td class="confluenceTd" style="border: 1px solid #dfe1e6; padding: 6px 10px;"><ac:link><ri:page ri:content-title="10. Master Incident Post-Mortems & Root Cause Analysis (RCA)" /></ac:link></td></tr>
<tr><td class="confluenceTd" style="border: 1px solid #dfe1e6; padding: 6px 10px;"><strong>FinOps Strategy</strong></td><td class="confluenceTd" style="border: 1px solid #dfe1e6; padding: 6px 10px;">Near-Zero Idle Cost ($0.00 compute idle, $0.15/mo storage)</td><td class="confluenceTd" style="border: 1px solid #dfe1e6; padding: 6px 10px;"><ac:link><ri:page ri:content-title="04. FinOps & Near-Zero Idle Cost Strategy" /></ac:link></td></tr>
<tr><td class="confluenceTd" style="border: 1px solid #dfe1e6; padding: 6px 10px;"><strong>Dual CI/CD</strong></td><td class="confluenceTd" style="border: 1px solid #dfe1e6; padding: 6px 10px;">GitHub Actions &amp; Azure DevOps Workload Identity Federation runbook</td><td class="confluenceTd" style="border: 1px solid #dfe1e6; padding: 6px 10px;"><ac:link><ri:page ri:content-title="05. Dual CI/CD, Workload Identity & Operations Runbook" /></ac:link></td></tr>
<tr><td class="confluenceTd" style="border: 1px solid #dfe1e6; padding: 6px 10px;"><strong>Engineering Learnings</strong></td><td class="confluenceTd" style="border: 1px solid #dfe1e6; padding: 6px 10px;">AKS pod networking, Oryx BOM fixes, APIM CORS, Reasoning models</td><td class="confluenceTd" style="border: 1px solid #dfe1e6; padding: 6px 10px;"><ac:link><ri:page ri:content-title="11. BankCompliance AI: Engineering Learnings & Troubleshooting" /></ac:link></td></tr>
</tbody></table>
"""
}

def get_token_from_az() -> str:
    token = os.environ.get("CONFLUENCE_API_TOKEN")
    if not token:
        try:
            cmd = "az keyvault secret show --vault-name kv-ht-ss-p-cin-01 --name confluence-api-token --subscription 859a785c-bd38-402d-b595-1f44f40fb9bf --query value -o tsv"
            result = subprocess.run(cmd, capture_output=True, text=True, check=True, shell=True)
            token = result.stdout.strip()
        except Exception as e:
            print(f"Notice: unable to query keyvault directly: {e}")
    return token

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

    html = re.sub(r'<p>\s*<img [^>]*src=[\"\'](.*?)[\"\'][^>]*\s*/?>\s*</p>', replace_image_tag, html)
    html = re.sub(r'<img [^>]*src=[\"\'](.*?)[\"\'][^>]*\s*/?>', replace_image_tag, html)
    html = re.sub(r'<blockquote>\s*<p>(.*?)</p>\s*</blockquote>', replace_callout, html, flags=re.DOTALL)
    return html

def get_auth_header(email: str, api_token: str) -> str:
    auth_str = f"{email}:{api_token}"
    b64_val = base64.b64encode(auth_str.encode("utf-8")).decode("utf-8")
    return f"Basic {b64_val}"

def make_request(url: str, method: str, headers: dict, data: dict = None):
    req = urllib.request.Request(url, method=method)
    for k, v in headers.items():
        req.add_header(k, v)
    if data:
        json_data = json.dumps(data).encode("utf-8")
        req.data = json_data
        req.add_header("Content-Type", "application/json; charset=utf-8")
    try:
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        err_body = e.read().decode("utf-8")
        print(f"HTTP Error {e.code} on {url}: {err_body}")
        return None

def publish_all(email: str, api_token: str):
    docs_dir = Path(__file__).resolve().parent.parent / "docs" / "confluence"
    auth = get_auth_header(email, api_token)
    headers = {"Authorization": auth, "Accept": "application/json"}

    print("=================================================================")
    print(f"  HappyTechies Confluence Cloud Publisher -> Space [{SPACE_KEY}]")
    print("=================================================================")

    list_url = f"https://{CONFLUENCE_DOMAIN}/wiki/rest/api/content?spaceKey={SPACE_KEY}&limit=100&expand=version"
    res = make_request(list_url, "GET", headers)
    existing_pages = {}
    if res and "results" in res:
        for p in res["results"]:
            existing_pages[p["title"].strip()] = {
                "id": p["id"],
                "version": p["version"]["number"]
            }

    # 1. Update Homepage (Page 7602285 / HappyTechies Cloud and AI Platform Home)
    homepage_title = "HappyTechies Cloud and AI Platform Home"
    if homepage_title in existing_pages:
        page_id = existing_pages[homepage_title]["id"]
        current_ver = existing_pages[homepage_title]["version"]
        update_url = f"https://{CONFLUENCE_DOMAIN}/wiki/rest/api/content/{page_id}"
        payload = {
            "version": {"number": current_ver + 1},
            "title": homepage_title,
            "type": "page",
            "space": {"key": SPACE_KEY},
            "body": {
                "storage": {
                    "value": HOMEPAGE_STORAGE,
                    "representation": "storage"
                }
            }
        }
        resp = make_request(update_url, "PUT", headers, payload)
        if resp:
            print(f"[HOMEPAGE UPDATED] {homepage_title} (v{current_ver + 1})")

    # 2. Update Section Pages
    for sec_title, sec_html in SECTION_PAGES_STORAGE.items():
        if sec_title in existing_pages:
            page_id = existing_pages[sec_title]["id"]
            current_ver = existing_pages[sec_title]["version"]
            update_url = f"https://{CONFLUENCE_DOMAIN}/wiki/rest/api/content/{page_id}"
            payload = {
                "version": {"number": current_ver + 1},
                "title": sec_title,
                "type": "page",
                "space": {"key": SPACE_KEY},
                "body": {
                    "storage": {
                        "value": sec_html,
                        "representation": "storage"
                    }
                }
            }
            resp = make_request(update_url, "PUT", headers, payload)
            if resp:
                print(f"[SECTION UPDATED] {sec_title} (v{current_ver + 1})")

    # 3. Update all 12 Documentation Pages
    for item in PAGES_MAP:
        file_path = docs_dir / item["file"]
        if not file_path.exists():
            print(f"Warning: {file_path} not found.")
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
                print(f"[DOC UPDATED] {item['num']}. {title} (v{current_ver + 1})")
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
                print(f"[DOC CREATED] {item['num']}. {title} (ID: {resp.get('id')})")

    print("\nConfluence Synchronization Completed Successfully.")

if __name__ == "__main__":
    email = os.environ.get("CONFLUENCE_EMAIL", DEFAULT_EMAIL)
    token = os.environ.get("CONFLUENCE_API_TOKEN")
    
    if not token:
        token = get_token_from_az()
        
    if not token and len(sys.argv) > 1:
        token = sys.argv[1]
        
    if not token:
        print("Error: Confluence API token required via CONFLUENCE_API_TOKEN env, Key Vault, or command argument.")
        sys.exit(1)

    publish_all(email, token)
