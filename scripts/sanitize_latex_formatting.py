"""
Sanitize LaTeX Formatting across Monorepo Markdown Files
=========================================================
Replaces all raw LaTeX math expressions (e.g. $\\rightarrow$, $$\\Delta W$$, etc.)
with clean, highly-readable standard text and Unicode arrows.
"""

from pathlib import Path
import re

DOCS_DIR = Path(__file__).resolve().parent.parent / "docs"

REPLACEMENTS = [
    (r"\$\\rightarrow\$", "➔"),
    (r"\$\\le\$", "<="),
    (r"\$\\ge\$", ">="),
    (r"\$\\approx\$", "~"),
    (r"\$\\sim\s*([0-9\.]+\s*(?:%|\w+))\$", r"~\1"),
    (r"\$\\sim\s*([0-9\.]+\\text\{\s*(\w+)\s*\})\$", r"~\1 \2"),
    (r"\$([0-9\.]+\\text\{\s*(\w+)\s*\})\$", r"\1 \2"),
    (r"\\text\{ MB\}", " MB"),
    (r"\\text\{ GB\}", " GB"),
    (r"\\text\{Cosine\}", "Cosine"),
    (r"\\ge", ">="),
    (r"\\le", "<="),
    (r"\\alpha", "alpha"),
    (r"\\Delta", "Delta_"),
    (r"\\cdot", "*"),
    (r"\$\$W = W_0 \+ \\Delta W\$\$", "```\nW = W0 + Delta_W\n```"),
    (r"\$\$\\Delta W = B \\cdot A\$\$", "```\nDelta_W = B * A\n```"),
    (r"\$W = W_0 \+ B \\cdot A\$", "W = W0 + B * A"),
    (r"\$W_0 \\in \\mathbb\{R\}\^\{d \\times k\}\$", "W0 matrix (d x k)"),
    (r"\$B \\in \\mathbb\{R\}\^\{d \\times r\}\$", "B matrix (d x r)"),
    (r"\$A \\in \\mathbb\{R\}\^\{r \\times k\}\$", "A matrix (r x k)"),
    (r"\$r \\ll \\min\(d, k\)\$", "r << min(d, k)"),
    (r"\$\\Delta W\$", "Delta_W"),
    (r"\$\$Format:.*?\$\$", ""),
    (r"\$\$\\text\{Format: \}.*?\$\$", ""),
]

def clean_file(file_path: Path):
    content = file_path.read_text(encoding="utf-8")
    original = content
    
    # Specific replacements
    content = content.replace("$\\rightarrow$", "➔")
    content = content.replace("$\\approx$", "~")
    content = content.replace("$\\ge$", ">=")
    content = content.replace("$\\le$", "<=")
    content = content.replace("($\\text{Cosine} \\ge 0.90$)", "(Cosine >= 0.90)")
    content = content.replace("($r=16, \\alpha=32$)", "(r=16, alpha=32)")
    content = content.replace("$$W = W_0 + \\Delta W$$", "`W = W0 + Delta_W`")
    content = content.replace("$$\\Delta W = B \\cdot A$$", "`Delta_W = B * A`")
    content = content.replace("$$W = W_0 + B \\cdot A$$", "`W = W0 + B * A`")
    content = content.replace("$W = W_0 + B \\cdot A$", "`W = W0 + B * A`")
    content = content.replace("$W_0 \\in \\mathbb{R}^{d \\times k}$", "W0 matrix (d x k)")
    content = content.replace("$B \\in \\mathbb{R}^{d \\times r}$", "B matrix (d x r)")
    content = content.replace("$A \\in \\mathbb{R}^{r \\times k}$", "A matrix (r x k)")
    content = content.replace("rank $r \\ll \\min(d, k)$", "rank r << min(d, k)")
    content = content.replace("$\\Delta W$", "Delta_W")
    content = content.replace("$\\sim 0.2\\%$", "~0.2%")
    content = content.replace("$\\sim 20\\text{ MB}$", "~20 MB")
    content = content.replace("$15\\text{ GB}$", "15 GB")
    
    # Clean up naming standards formulas
    content = re.sub(
        r'\$\$\\text\{Format: \}\s*\\mathbf\{\\langle resource\\_type\\rangle.*?\}\$\$',
        '`<resource_type>-<project>-<workload>-<environment>-<region_short>-<instance>`',
        content
    )
    content = re.sub(
        r'\$\$\\text\{Format: \}\s*\\mathbf\{\\langle resource\\_type\\rangle.*?\}\$\$',
        '`<resourcetype><project><workload><environment><region_short><instance>`',
        content
    )

    # General regex clean for any remaining $\rightarrow$
    content = re.sub(r'\\?\$\\rightarrow\\?\$', '➔', content)

    if content != original:
        file_path.write_text(content, encoding="utf-8")
        print(f"[SANITIZED] Cleaned LaTeX from {file_path.relative_to(DOCS_DIR.parent)}")

if __name__ == "__main__":
    print("Sanitizing all markdown documents in docs/ ...")
    for md_file in DOCS_DIR.rglob("*.md"):
        clean_file(md_file)
    print("LaTeX sanitization complete!")
