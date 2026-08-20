import re
from pathlib import Path
from typing import List, Dict, Any, Tuple

STOP_WORDS = {
    "a", "about", "above", "after", "again", "against", "all", "am", "an", "and",
    "any", "are", "aren't", "as", "at", "be", "because", "been", "before", "being",
    "below", "between", "both", "but", "by", "can", "cannot", "could", "did", "do",
    "does", "doing", "don't", "down", "during", "each", "few", "for", "from",
    "further", "had", "has", "have", "having", "he", "her", "here", "hers", "herself",
    "him", "himself", "his", "how", "if", "in", "into", "is", "it", "its", "itself",
    "let's", "me", "more", "most", "must", "my", "myself", "no", "nor", "not", "of",
    "off", "on", "once", "only", "or", "other", "ought", "our", "ours", "ourselves",
    "out", "over", "own", "same", "she", "should", "so", "some", "such", "than",
    "that", "the", "their", "theirs", "them", "themselves", "then", "there", "these",
    "they", "this", "those", "through", "to", "too", "under", "until", "up", "very",
    "was", "we", "were", "what", "when", "where", "which", "while", "who", "whom",
    "why", "with", "would", "you", "your", "yours", "yourself", "yourselves", "shall"
}

def parse_frontmatter(content: str) -> Tuple[Dict[str, str], str]:
    metadata = {}
    body = content
    
    if content.startswith("---"):
        parts = content.split("---", 2)
        if len(parts) >= 3:
            fm_text = parts[1].strip()
            body = parts[2].strip()
            for line in fm_text.splitlines():
                if ":" in line:
                    k, v = line.split(":", 1)
                    metadata[k.strip()] = v.strip().strip('"\'')
    
    return metadata, body

def extract_keywords(text: str, max_keywords: int = 25) -> List[str]:
    words = re.findall(r'[a-zA-Z0-9\-_]+', text.lower())
    freq = {}
    for w in words:
        if len(w) > 2 and w not in STOP_WORDS and not w.isdigit():
            freq[w] = freq.get(w, 0) + 1
    
    # Priority for capitalized acronyms
    acronyms = set(re.findall(r'\b[A-Z0-9\-]{2,}\b', text))
    for ac in acronyms:
        freq[ac.lower()] = freq.get(ac.lower(), 0) + 8
        
    sorted_keywords = sorted(freq.keys(), key=lambda x: freq[x], reverse=True)
    return sorted_keywords[:max_keywords]

def chunk_rbi_markdown(file_path_or_text: str, circular_id: str = None, circular_title: str = None) -> List[Dict[str, Any]]:
    path = Path(file_path_or_text)
    if path.is_file():
        content = path.read_text(encoding="utf-8")
    else:
        content = file_path_or_text
        
    metadata, body = parse_frontmatter(content)
    
    circular_no = metadata.get("circular_no", circular_id or "RBI/GEN/2026")
    title = metadata.get("title", circular_title or "RBI Master Direction")
    category = metadata.get("category", "general_compliance")
    
    # Split across markdown headers (## or ###)
    sections = re.split(r'\n(?=#{2,3}\s+)', body)
    chunks = []
    current_chapter = title
    
    for section in sections:
        section = section.strip()
        if not section:
            continue
            
        header_match = re.match(r'^(#{2,3})\s+(.+)$', section, re.MULTILINE)
        if header_match:
            level = len(header_match.group(1))
            header_text = header_match.group(2).strip()
            if level == 2:
                current_chapter = header_text
                clause_header = header_text
            else:
                clause_header = f"{current_chapter} — {header_text}"
        else:
            clause_header = f"{title} - Overview"
            
        keywords = extract_keywords(f"{title} {clause_header} {section}")
        
        chunks.append({
            "circular_no": circular_no,
            "title": title,
            "category": category,
            "clause": clause_header,
            "text": section,
            "keywords": keywords
        })
        
    return chunks
