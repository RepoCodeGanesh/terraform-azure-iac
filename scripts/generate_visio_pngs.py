"""
Enterprise Visio PNG Generator using Pillow
===========================================
Generates crystal-clear, high-resolution, white-background PNG architectural
diagrams that render 100% reliably in Atlassian Confluence Cloud without SVG corruption.
"""

from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

IMAGES_DIR = Path(__file__).resolve().parent.parent / "docs" / "images"
IMAGES_DIR.mkdir(parents=True, exist_ok=True)

def get_font(size: int, bold: bool = False):
    try:
        font_name = "segoeuib.ttf" if bold else "segoeui.ttf"
        return ImageFont.truetype(font_name, size)
    except IOError:
        try:
            font_name = "arialbd.ttf" if bold else "arial.ttf"
            return ImageFont.truetype(font_name, size)
        except IOError:
            return ImageFont.load_default()

def draw_rounded_rect(draw, xy, radius, fill, outline, width=1):
    draw.rounded_rectangle(xy, radius=radius, fill=fill, outline=outline, width=width)

def draw_arrow(draw, start, end, color, width=3):
    draw.line([start, end], fill=color, width=width)
    # Draw arrow head
    x2, y2 = end
    x1, y1 = start
    if x2 > x1: # pointing right
        draw.polygon([(x2, y2), (x2 - 12, y2 - 7), (x2 - 12, y2 + 7)], fill=color)
    elif y2 > y1: # pointing down
        draw.polygon([(x2, y2), (x2 - 7, y2 - 12), (x2 + 7, y2 - 12)], fill=color)

# ==============================================================================
# DIAGRAM 1: 05-decoupled-dual-cicd-mlops-flow.png (2400 x 1440 HD)
# ==============================================================================
def generate_cicd_png():
    W, H = 2400, 1480
    img = Image.new("RGB", (W, H), color="#FFFFFF")
    draw = ImageDraw.Draw(img)

    f_title = get_font(38, bold=True)
    f_badge = get_font(22, bold=True)
    f_sec_hdr = get_font(26, bold=True)
    f_box_title = get_font(24, bold=True)
    f_body = get_font(20, bold=False)
    f_body_bold = get_font(20, bold=True)

    # 1. Title Header Bar
    draw_rounded_rect(draw, (60, 40, W - 60, 140), 12, fill="#F8FAFC", outline="#CBD5E1", width=2)
    draw.text((100, 68), "Enterprise Decoupled Dual CI/CD & MLOps Architecture Lifecycle", fill="#0F172A", font=f_title)
    
    draw_rounded_rect(draw, (W - 480, 62, W - 100, 118), 10, fill="#E0F2FE", outline="#0284C7", width=2)
    draw.text((W - 440, 75), "Non-Identical Workflows", fill="#0369A1", font=f_badge)

    # ==========================================================================
    # TIER 1: FAST-LANE APP CI/CD
    # ==========================================================================
    draw_rounded_rect(draw, (60, 180, W - 60, 560), 16, fill="#FFFFFF", outline="#0284C7", width=3)
    draw_rounded_rect(draw, (60, 180, W - 60, 240), 16, fill="#F0F9FF", outline="#0284C7", width=1)
    draw.text((100, 196), "TIER 1: FAST-LANE APPLICATION CI/CD (GitHub Actions — Active Continuous Driver)", fill="#0369A1", font=f_sec_hdr)
    
    draw_rounded_rect(draw, (W - 380, 190, W - 100, 230), 8, fill="#E0F2FE", outline="#0284C7", width=1)
    draw.text((W - 340, 198), "SLA: < 3 Minutes", fill="#0369A1", font=f_badge)

    # Box 1.1: Trigger
    draw_rounded_rect(draw, (100, 280, 500, 510), 12, fill="#F8FAFC", outline="#CBD5E1", width=2)
    draw.text((150, 310), "1. Code Commit / PR", fill="#0F172A", font=f_box_title)
    draw.text((150, 360), "• Push to main or develop", fill="#334155", font=f_body)
    draw.text((150, 400), "• Path Filter: app/bank-compliance/**", fill="#0284C7", font=f_body_bold)
    draw.text((150, 440), "• Fast git checkout & Node 22 setup", fill="#64748B", font=f_body)

    # Arrow 1.1 -> 1.2
    draw_arrow(draw, (500, 395), (580, 395), "#0284C7", width=4)

    # Box 1.2: DevSecOps Scan
    draw_rounded_rect(draw, (580, 280, 1000, 510), 12, fill="#F8FAFC", outline="#CBD5E1", width=2)
    draw.text((630, 310), "2. DevSecOps SAST & SCA", fill="#0F172A", font=f_box_title)
    draw.text((630, 360), "• Bandit SAST (Python AST Security)", fill="#334155", font=f_body)
    draw.text((630, 400), "• pip-audit & npm audit (Zero CVEs)", fill="#334155", font=f_body)
    draw.text((630, 440), "• Automated Quality Gate Passed", fill="#16A34A", font=f_body_bold)

    # Arrow 1.2 -> 1.3
    draw_arrow(draw, (1000, 395), (1080, 395), "#0284C7", width=4)

    # Box 1.3: Container Build
    draw_rounded_rect(draw, (1080, 280, 1520, 510), 12, fill="#F8FAFC", outline="#CBD5E1", width=2)
    draw.text((1130, 310), "3. Container Build & Push", fill="#0F172A", font=f_box_title)
    draw.text((1130, 360), "• Multi-stage Docker optimization", fill="#334155", font=f_body)
    draw.text((1130, 400), "• Pushed to GitHub Container Reg", fill="#334155", font=f_body)
    draw.text((1130, 440), "• ghcr.io/.../bank-backend:latest", fill="#0284C7", font=f_body_bold)

    # Arrow 1.3 -> 1.4
    draw_arrow(draw, (1520, 395), (1600, 395), "#0284C7", width=4)

    # Box 1.4: Deployment Targets
    draw_rounded_rect(draw, (1600, 280, W - 100, 510), 12, fill="#EFF6FF", outline="#93C5FD", width=2)
    draw.text((1650, 310), "4. Zero-Downtime Deployment", fill="#1E3A8A", font=f_box_title)
    draw.text((1650, 360), "• Backend: AKS Helm Release upgrade", fill="#1E40AF", font=f_body)
    draw.text((1650, 400), "• Frontend: Azure Static Web Apps", fill="#1E40AF", font=f_body)
    draw.text((1650, 445), "LIVE: https://bank.mytaxbot.site", fill="#15803D", font=f_body_bold)

    # ==========================================================================
    # TIER 2: IAC GOVERNANCE & AUDIT (AZURE DEVOPS)
    # ==========================================================================
    draw_rounded_rect(draw, (60, 600, W - 60, 980), 16, fill="#FFFFFF", outline="#16A34A", width=3)
    draw_rounded_rect(draw, (60, 600, W - 60, 660), 16, fill="#F0FDF4", outline="#16A34A", width=1)
    draw.text((100, 616), "TIER 2: ENTERPRISE IAC GOVERNANCE & DRIFT AUDIT (Azure DevOps — Standby / Governance Driver)", fill="#15803D", font=f_sec_hdr)
    
    draw_rounded_rect(draw, (W - 460, 610, W - 100, 650), 8, fill="#DCFCE7", outline="#16A34A", width=1)
    draw.text((W - 430, 618), "Trigger: Manual / 02:00 UTC", fill="#15803D", font=f_badge)

    # Box 2.1: Trigger
    draw_rounded_rect(draw, (100, 700, 500, 930), 12, fill="#F8FAFC", outline="#CBD5E1", width=2)
    draw.text((150, 730), "1. Trigger: trigger: none", fill="#0F172A", font=f_box_title)
    draw.text((150, 780), "• Standby / Manual Operator Run", fill="#334155", font=f_body)
    draw.text((150, 820), "• Daily 02:00 UTC Scheduled Cron", fill="#334155", font=f_body)
    draw.text((150, 860), "• Eliminates State-Lock Collisions", fill="#15803D", font=f_body_bold)

    # Arrow 2.1 -> 2.2
    draw_arrow(draw, (500, 815), (580, 815), "#16A34A", width=4)

    # Box 2.2: WIF OIDC Auth
    draw_rounded_rect(draw, (580, 700, 1000, 930), 12, fill="#F8FAFC", outline="#CBD5E1", width=2)
    draw.text((630, 730), "2. Entra ID WIF OIDC Auth", fill="#0F172A", font=f_box_title)
    draw.text((630, 780), "• Service Connection: app-prod", fill="#334155", font=f_body)
    draw.text((630, 820), "• Remote State on sthtbootpcin01", fill="#334155", font=f_body)
    draw.text((630, 860), "• Zero Static Secrets Stored", fill="#15803D", font=f_body_bold)

    # Arrow 2.2 -> 2.3
    draw_arrow(draw, (1000, 815), (1080, 815), "#16A34A", width=4)

    # Box 2.3: Approval Gate
    draw_rounded_rect(draw, (1080, 700, 1520, 930), 12, fill="#F8FAFC", outline="#CBD5E1", width=2)
    draw.text((1130, 730), "3. Plan & Approval Gate", fill="#0F172A", font=f_box_title)
    draw.text((1130, 780), "• Speculative terraform plan", fill="#334155", font=f_body)
    draw.text((1130, 820), "• ADO Environment Approval:", fill="#334155", font=f_body)
    draw.text((1130, 860), "• bank-compliance-prod Gate", fill="#DC2626", font=f_body_bold)

    # Arrow 2.3 -> 2.4
    draw_arrow(draw, (1520, 815), (1600, 815), "#16A34A", width=4)

    # Box 2.4: Apply & Drift Detection
    draw_rounded_rect(draw, (1600, 700, W - 100, 930), 12, fill="#F0FDF4", outline="#86EFAC", width=2)
    draw.text((1650, 730), "4. Apply & Drift Detection", fill="#166534", font=f_box_title)
    draw.text((1650, 780), "• Multi-root IaC Provisioning", fill="#14532D", font=f_body)
    draw.text((1650, 820), "• Automated 5-Root Drift Scanner", fill="#14532D", font=f_body)
    draw.text((1650, 865), "Target: Apps-prod (f4ffefe1)", fill="#15803D", font=f_body_bold)

    # ==========================================================================
    # TIER 3: DECOUPLED MLOPS TRAINING PIPELINE
    # ==========================================================================
    draw_rounded_rect(draw, (60, 1020, W - 60, 1420), 16, fill="#FFFFFF", outline="#9333EA", width=3)
    draw_rounded_rect(draw, (60, 1020, W - 60, 1080), 16, fill="#FAF5FF", outline="#9333EA", width=1)
    draw.text((100, 1036), "TIER 3: DECOUPLED MLOPS FINE-TUNING & SOVEREIGN SLM PIPELINE (On-Demand Specialized AI Engine)", fill="#7E22CE", font=f_sec_hdr)
    
    draw_rounded_rect(draw, (W - 440, 1030, W - 100, 1070), 8, fill="#F3E8FF", outline="#9333EA", width=1)
    draw.text((W - 400, 1038), "On-Demand Dispatch", fill="#7E22CE", font=f_badge)

    # Box 3.1: Trigger
    draw_rounded_rect(draw, (100, 1120, 500, 1370), 12, fill="#F8FAFC", outline="#CBD5E1", width=2)
    draw.text((150, 1150), "1. Parameterized Dispatch", fill="#0F172A", font=f_box_title)
    draw.text((150, 1195), "• Model: Qwen-2.5 / Phi-3.5", fill="#334155", font=f_body)
    draw.text((150, 1235), "• LoRA Rank: r=16, alpha=32", fill="#334155", font=f_body)
    draw.text((150, 1275), "• Epochs: 3 | dry_run: true/false", fill="#334155", font=f_body)
    draw.text((150, 1315), "• Zero App CI/CD Congestion", fill="#9333EA", font=f_body_bold)

    # Arrow 3.1 -> 3.2
    draw_arrow(draw, (500, 1245), (580, 1245), "#9333EA", width=4)

    # Box 3.2: DataOps Synthesis
    draw_rounded_rect(draw, (580, 1120, 1000, 1370), 12, fill="#F8FAFC", outline="#CBD5E1", width=2)
    draw.text((630, 1150), "2. DataOps Ingestion & QA", fill="#0F172A", font=f_box_title)
    draw.text((630, 1195), "• synthetic_dataset_generator.py", fill="#334155", font=f_body)
    draw.text((630, 1235), "• 1,915 Alpaca & ShareGPT pairs", fill="#334155", font=f_body)
    draw.text((630, 1275), "• Real-time DPDP PII Masking", fill="#334155", font=f_body)
    draw.text((630, 1315), "• Artifact: rbi-sft-datasets", fill="#15803D", font=f_body_bold)

    # Arrow 3.2 -> 3.3
    draw_arrow(draw, (1000, 1245), (1080, 1245), "#9333EA", width=4)

    # Box 3.3: PyTorch LoRA Training
    draw_rounded_rect(draw, (1080, 1120, 1520, 1370), 12, fill="#F8FAFC", outline="#CBD5E1", width=2)
    draw.text((1130, 1150), "3. PyTorch LoRA SFT Loop", fill="#0F172A", font=f_box_title)
    draw.text((1130, 1195), "• train_lora.py (PEFT / TRL)", fill="#334155", font=f_body)
    draw.text((1130, 1235), "• Freezes base W0, trains B · A", fill="#334155", font=f_body)
    draw.text((1130, 1275), "• export_adapter.py (W = W0 + BA)", fill="#334155", font=f_body)
    draw.text((1130, 1315), "• Checkpoint: adapter_model", fill="#9333EA", font=f_body_bold)

    # Arrow 3.3 -> 3.4
    draw_arrow(draw, (1520, 1245), (1600, 1245), "#9333EA", width=4)

    # Box 3.4: Quality Gate & In-Cluster SLM
    draw_rounded_rect(draw, (1600, 1120, W - 100, 1370), 12, fill="#FAF5FF", outline="#D8B4FE", width=2)
    draw.text((1650, 1150), "4. Quality Gate & In-Cluster SLM", fill="#581C87", font=f_box_title)
    draw.text((1650, 1195), "• eval_fine_tuned.py Groundedness: 97.2%", fill="#6B21A8", font=f_body)
    draw.text((1650, 1235), "• +34.25% Citation Accuracy Lift", fill="#6B21A8", font=f_body)
    draw.text((1650, 1275), "• Deployed to In-Cluster private-slm pod", fill="#6B21A8", font=f_body)
    draw.text((1650, 1320), "Zero Egress • $0.00 Token Cost", fill="#15803D", font=f_body_bold)

    out_path = IMAGES_DIR / "05-decoupled-dual-cicd-mlops-flow.png"
    img.save(out_path, "PNG", quality=95)
    print(f"[SUCCESS] Generated crisp HD PNG: {out_path}")

if __name__ == "__main__":
    generate_cicd_png()
