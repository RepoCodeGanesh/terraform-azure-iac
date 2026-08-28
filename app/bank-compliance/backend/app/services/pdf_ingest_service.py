import os
import io
import re
import hashlib
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

# Try importing pypdf
try:
    import pypdf
    PYPDF_AVAILABLE = True
except ImportError:
    PYPDF_AVAILABLE = False
    logger.warning("pypdf is not installed. PDF text extraction will fallback to text extraction.")

class PDFIngestService:
    """Multi-Model Regulatory Document Parser & PDF Ingestion Engine."""

    @classmethod
    def compute_sha256(cls, file_bytes: bytes) -> str:
        """Computes cryptographic SHA-256 hash for legal provenance."""
        return hashlib.sha256(file_bytes).hexdigest()

    @classmethod
    def extract_text_from_pdf_bytes(cls, file_bytes: bytes) -> List[Dict[str, Any]]:
        """
        Extracts pages and text from raw PDF bytes.
        Returns a list of dicts with page number and page text.
        """
        pages_data = []
        if PYPDF_AVAILABLE:
            try:
                reader = pypdf.PdfReader(io.BytesIO(file_bytes))
                for idx, page in enumerate(reader.pages):
                    text = page.extract_text() or ""
                    pages_data.append({
                        "page_number": idx + 1,
                        "text": text.strip()
                    })
                return pages_data
            except Exception as e:
                logger.error("Failed extracting PDF with pypdf: %s", e)

        # Fallback: Attempt simple latin-1 or utf-8 decode
        try:
            raw_text = file_bytes.decode("utf-8", errors="ignore")
        except Exception:
            raw_text = file_bytes.decode("latin-1", errors="ignore")
        
        pages_data.append({
            "page_number": 1,
            "text": raw_text.strip()
        })
        return pages_data

    @classmethod
    def parse_pdf_document(cls, file_bytes: bytes, filename: str) -> Dict[str, Any]:
        """
        Parses a native RBI Master Direction PDF into a structured document model
        with sections, page references, and cryptographic provenance hash.
        """
        sha256_hash = cls.compute_sha256(file_bytes)
        pages = cls.extract_text_from_pdf_bytes(file_bytes)
        full_text = "\n\n".join([f"--- Page {p['page_number']} ---\n" + p['text'] for p in pages])
        
        # Detect circular number using RBI pattern (e.g. RBI/2023-24/108 or RBI/DBR/2016-17/14)
        circular_match = re.search(r'RBI\/[A-Z0-9\-\/]+', full_text, re.IGNORECASE)
        circular_no = circular_match.group(0) if circular_match else filename.replace(".pdf", "").upper()

        # Detect Title
        title = filename.replace(".pdf", "").replace("-", " ").replace("_", " ").title()
        for page in pages[:2]:
            lines = [l.strip() for l in page["text"].split("\n") if l.strip()]
            for line in lines:
                if any(k in line.lower() for k in ["master direction", "guidelines on", "framework for", "directions,"]):
                    title = line
                    break
            if title != filename:
                break

        # Categorize
        category = cls._detect_category(filename + " " + full_text[:500])

        # Extract sections and clauses from pages
        sections: List[Dict[str, Any]] = []
        current_section = {"title": "Preamble & General Provisions", "clauses": [], "raw_text": "", "page": 1}
        
        for p in pages:
            page_num = p["page_number"]
            page_text = p["text"]
            lines = page_text.split("\n")
            
            for line in lines:
                line_str = line.strip()
                if not line_str:
                    continue
                    
                # Check for Chapter or Section headings
                if re.match(r'^(CHAPTER|SECTION|PART)\s+[IVXLCDM0-9]+', line_str, re.IGNORECASE) or (len(line_str) < 60 and line_str.isupper() and len(line_str.split()) > 1):
                    if current_section["clauses"] or current_section["raw_text"].strip():
                        sections.append(current_section)
                    current_section = {
                        "title": line_str,
                        "clauses": [],
                        "raw_text": f"[Page {page_num}]\n",
                        "page": page_num
                    }
                # Check for numbered clauses (e.g. "12.", "12.1", "Clause 4", "(a)")
                elif re.match(r'^(\d+\.|\d+\.\d+|Clause\s+\d+|\([a-z]\))\s+', line_str):
                    clause_id = f"p{page_num}-c{len(current_section['clauses']) + 1}"
                    current_section["clauses"].append({
                        "id": clause_id,
                        "header": line_str[:100],
                        "preview": line_str,
                        "page": page_num
                    })
                    current_section["raw_text"] += line_str + "\n"
                else:
                    current_section["raw_text"] += line_str + "\n"

        if current_section["clauses"] or current_section["raw_text"].strip():
            sections.append(current_section)

        return {
            "document_id": filename.replace(".pdf", ""),
            "filename": filename,
            "title": title,
            "circular_no": circular_no,
            "category": category,
            "provenance_hash": f"sha256:{sha256_hash[:16]}",
            "full_sha256": sha256_hash,
            "total_pages": len(pages),
            "total_sections": len(sections),
            "total_characters": len(full_text),
            "last_updated": datetime.utcnow().isoformat() + "Z",
            "content": full_text,
            "sections": sections,
            "source_url": f"https://rbidocs.rbi.org.in/rdocs/notification/PDFs/{filename}"
        }

    @classmethod
    def _detect_category(cls, text_sample: str) -> str:
        s = text_sample.lower()
        if "kyc" in s or "aml" in s or "customer due diligence" in s or "v-cip" in s:
            return "KYC & AML Compliance"
        elif "cybersecurity" in s or "it governance" in s or "information security" in s:
            return "IT Governance & Cybersecurity"
        elif "outsourcing" in s or "cloud computing" in s or "material outsourcing" in s:
            return "IT Outsourcing & FinTech Risk"
        elif "tokenisation" in s or "payment" in s or "card-on-file" in s:
            return "Digital Payments & Tokenisation"
        elif "credit card" in s or "debit card" in s or "co-branding" in s:
            return "Cards & Payment Instruments"
        elif "digital lending" in s or "fldg" in s or "default loss guarantee" in s:
            return "Digital Lending & RE Norms"
        return "General Banking Regulations"

    @classmethod
    def parse_markdown_document(cls, file_path: Path) -> Dict[str, Any]:
        """
        Parses a structured RBI Master Direction markdown file into a full document
        model with sections, clauses, and metadata for the interactive UI viewer.
        """
        if not file_path.exists():
            raise FileNotFoundError(f"Document not found at: {file_path}")

        content = file_path.read_text(encoding="utf-8")
        file_bytes = file_path.read_bytes()
        sha256_hash = cls.compute_sha256(file_bytes)

        lines = content.split("\n")
        title = "Reserve Bank of India Master Direction"
        circular_no = file_path.stem
        sections: List[Dict[str, Any]] = []
        current_section = {"title": "Introduction", "clauses": [], "raw_text": "", "page": 1}

        for line in lines:
            if line.startswith("# ") and title == "Reserve Bank of India Master Direction":
                title = line.replace("# ", "").strip()
            elif line.startswith("## "):
                if current_section["clauses"] or current_section["raw_text"].strip():
                    sections.append(current_section)
                current_section = {
                    "title": line.replace("## ", "").strip(),
                    "clauses": [],
                    "raw_text": "",
                    "page": 1
                }
            elif line.startswith("### ") or line.startswith("* **Clause") or line.startswith("- **Clause") or line.startswith("#### "):
                clause_header = line.strip().replace("### ", "").replace("#### ", "").replace("* ", "").replace("- ", "")
                clause_id = f"clause-{len(current_section['clauses']) + 1}"
                current_section["clauses"].append({
                    "id": clause_id,
                    "header": clause_header,
                    "preview": line.strip(),
                    "page": 1
                })
                current_section["raw_text"] += line + "\n"
            else:
                current_section["raw_text"] += line + "\n"

        if current_section["clauses"] or current_section["raw_text"].strip():
            sections.append(current_section)

        category = cls._detect_category(file_path.stem + " " + title)

        return {
            "document_id": file_path.stem,
            "filename": file_path.name,
            "title": title,
            "circular_no": circular_no,
            "category": category,
            "provenance_hash": f"sha256:{sha256_hash[:16]}",
            "full_sha256": sha256_hash,
            "total_pages": 1,
            "total_sections": len(sections),
            "total_characters": len(content),
            "last_updated": datetime.utcnow().isoformat() + "Z",
            "content": content,
            "sections": sections,
            "source_url": f"https://www.rbi.org.in/Scripts/BS_ViewMasDirections.aspx?id={file_path.stem}"
        }

    @classmethod
    def get_document_by_id(cls, doc_id: str, docs_dir: Path) -> Optional[Dict[str, Any]]:
        """Finds and parses a document by circular ID or filename stem across .pdf and .md."""
        clean_id = doc_id.lower().replace(".md", "").replace(".pdf", "")
        
        # Check for PDF files first
        raw_pdf_dir = docs_dir.parent / "raw_pdfs"
        if not raw_pdf_dir.exists():
            raw_pdf_dir = docs_dir / "raw_pdfs"
            
        if raw_pdf_dir.exists():
            for pdf_file in raw_pdf_dir.glob("*.pdf"):
                if clean_id in pdf_file.stem.lower() or pdf_file.stem.lower().startswith(clean_id):
                    return cls.parse_pdf_document(pdf_file.read_bytes(), pdf_file.name)

        # Check for markdown files
        for file_path in docs_dir.glob("*.md"):
            if clean_id in file_path.stem.lower() or file_path.stem.lower().startswith(clean_id):
                return cls.parse_markdown_document(file_path)

        # Fallback: check first available document
        first_pdf = next(raw_pdf_dir.glob("*.pdf"), None) if raw_pdf_dir.exists() else None
        if first_pdf:
            return cls.parse_pdf_document(first_pdf.read_bytes(), first_pdf.name)

        first_md = next(docs_dir.glob("*.md"), None)
        if first_md:
            return cls.parse_markdown_document(first_md)

        return None

