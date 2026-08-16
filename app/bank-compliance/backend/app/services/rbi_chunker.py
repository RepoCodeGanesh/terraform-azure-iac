import re
from typing import List, Dict

CLAUSE_PATTERN = re.compile(r'^(Section|Clause|Chapter)\s+([0-9\.\(\)\w]+)', re.MULTILINE)

def chunk_rbi_markdown(text: str, circular_id: str, circular_title: str) -> List[Dict]:
    """
    Splits legal RBI Master Directions along section and clause boundaries.
    """
    chunks = []
    matches = list(CLAUSE_PATTERN.finditer(text))
    
    for i, match in enumerate(matches):
        start_idx = match.start()
        end_idx = matches[i+1].start() if i+1 < len(matches) else len(text)
        
        clause_header = match.group(0)
        clause_body = text[start_idx:end_idx].strip()
        
        chunks.append({
            "circular_no": circular_id,
            "title": circular_title,
            "clause": clause_header,
            "text": clause_body
        })
        
    return chunks
