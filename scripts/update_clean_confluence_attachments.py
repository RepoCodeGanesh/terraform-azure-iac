import os
import sys
import urllib.request
import json
import base64
from pathlib import Path

CONFLUENCE_DOMAIN = "happytechies.atlassian.net"
EMAIL = os.environ.get("CONFLUENCE_EMAIL", "richtextforganesh@outlook.com")
TOKEN = os.environ.get("CONFLUENCE_API_TOKEN")

if not TOKEN and len(sys.argv) > 1:
    TOKEN = sys.argv[1]

IMAGES_DIR = Path(__file__).resolve().parent.parent / "docs" / "images"

PAGE_ATTACHMENTS = [
    {
        "page_id": "10321962",
        "file": "09-enterprise-network-traffic-flow.svg"
    },
    {
        "page_id": "10289154",
        "file": "01-caf-landing-zone-topology.svg"
    },
    {
        "page_id": "7700481",
        "file": "03-bank-compliance-aks-architecture.svg"
    },
    {
        "page_id": "10420225",
        "file": "05-decoupled-dual-cicd-mlops-flow.png"
    }
]

def get_auth_header():
    auth_str = f"{EMAIL}:{TOKEN}"
    return f"Basic {base64.b64encode(auth_str.encode()).decode()}"

def update_attachment(page_id: str, file_path: Path):
    auth = get_auth_header()
    filename = file_path.name
    file_bytes = file_path.read_bytes()
    mime_type = "image/png" if filename.endswith(".png") else "image/svg+xml"

    att_url = f"https://{CONFLUENCE_DOMAIN}/wiki/rest/api/content/{page_id}/child/attachment?filename={filename}"
    req = urllib.request.Request(att_url, headers={"Authorization": auth, "Accept": "application/json"})
    
    with urllib.request.urlopen(req) as resp:
        att_data = json.loads(resp.read().decode())
    
    boundary = "----WebKitFormBoundary7MA4YWxkTrZu0gW"
    body = (
        f"--{boundary}\r\n"
        f'Content-Disposition: form-data; name="file"; filename="{filename}"\r\n'
        f"Content-Type: {mime_type}\r\n\r\n"
    ).encode("utf-8") + file_bytes + f"\r\n--{boundary}--\r\n".encode("utf-8")

    if att_data.get("results"):
        att_id = att_data["results"][0]["id"]
        post_url = f"https://{CONFLUENCE_DOMAIN}/wiki/rest/api/content/{page_id}/child/attachment/{att_id}/data"
        post_req = urllib.request.Request(post_url, data=body, method="POST")
        post_req.add_header("Authorization", auth)
        post_req.add_header("X-Atlassian-Token", "nocheck")
        post_req.add_header("Content-Type", f"multipart/form-data; boundary={boundary}")
        with urllib.request.urlopen(post_req) as r:
            print(f"[UPDATED ATTACHMENT] Overwrote {filename} on Page {page_id}")
    else:
        create_url = f"https://{CONFLUENCE_DOMAIN}/wiki/rest/api/content/{page_id}/child/attachment"
        create_req = urllib.request.Request(create_url, data=body, method="POST")
        create_req.add_header("Authorization", auth)
        create_req.add_header("X-Atlassian-Token", "nocheck")
        create_req.add_header("Content-Type", f"multipart/form-data; boundary={boundary}")
        with urllib.request.urlopen(create_req) as r:
            print(f"[CREATED ATTACHMENT] Uploaded {filename} to Page {page_id}")

if __name__ == "__main__":
    if not TOKEN:
        print("Error: CONFLUENCE_API_TOKEN environment variable required.")
        sys.exit(1)
    for item in PAGE_ATTACHMENTS:
        file_path = IMAGES_DIR / item["file"]
        if file_path.exists():
            update_attachment(item["page_id"], file_path)
