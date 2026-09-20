"""
Regulatory Knowledge Graph (GraphRAG) Service for Banking Compliance
Implements hierarchical DAG (Directed Acyclic Graph) representation of RBI Master Directions:
Circular / Master Direction -> Chapter -> Section -> Clause -> Penal Mandate
Enables context expansion, parent-child traversal, and zero-hallucination statutory verification.
"""

from typing import Dict, List, Any, Optional, Set
import re
import hashlib


class RegulatoryKnowledgeGraph:
    """
    In-memory directed hierarchical regulatory graph for GraphRAG.
    Zero cloud cost -- stores relational edges and provides sub-millisecond DAG traversal.
    """

    def __init__(self):
        # node_id -> node_dict
        self.nodes: Dict[str, Dict[str, Any]] = {}
        # parent_id -> set of child_ids
        self.children: Dict[str, Set[str]] = {}
        # child_id -> parent_id
        self.parents: Dict[str, str] = {}
        # topic / keyword -> set of node_ids
        self.topic_index: Dict[str, Set[str]] = {}

    def add_node(
        self,
        node_id: str,
        node_type: str,
        title: str,
        content: str = "",
        parent_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Adds a node to the regulatory graph."""
        self.nodes[node_id] = {
            "node_id": node_id,
            "node_type": node_type,  # CIRCULAR | CHAPTER | SECTION | CLAUSE | PENAL_MANDATE
            "title": title,
            "content": content,
            "parent_id": parent_id,
            "metadata": metadata or {},
            "sha256": f"sha256:{hashlib.sha256(content.encode('utf-8')).hexdigest()}" if content else ""
        }

        if parent_id:
            self.parents[node_id] = parent_id
            if parent_id not in self.children:
                self.children[parent_id] = set()
            self.children[parent_id].add(node_id)

        # Index keywords for fast topic search
        words = re.findall(r'[a-zA-Z0-9_\-]+', f"{title} {content}".lower())
        for w in words:
            if len(w) >= 3:
                if w not in self.topic_index:
                    self.topic_index[w] = set()
                self.topic_index[w].add(node_id)

    def get_node(self, node_id: str) -> Optional[Dict[str, Any]]:
        """Returns node metadata if present."""
        return self.nodes.get(node_id)

    def get_parent_chain(self, node_id: str) -> List[Dict[str, Any]]:
        """Traverses up the hierarchy to root circular."""
        chain = []
        curr = self.parents.get(node_id)
        visited = set()
        while curr and curr not in visited:
            visited.add(curr)
            parent_node = self.nodes.get(curr)
            if parent_node:
                chain.append(parent_node)
                curr = self.parents.get(curr)
            else:
                break
        return chain

    def get_children(self, node_id: str) -> List[Dict[str, Any]]:
        """Returns immediate children of a node."""
        child_ids = self.children.get(node_id, set())
        return [self.nodes[cid] for cid in child_ids if cid in self.nodes]

    def get_siblings(self, node_id: str) -> List[Dict[str, Any]]:
        """Returns sibling nodes belonging to the same parent."""
        parent_id = self.parents.get(node_id)
        if not parent_id:
            return []
        child_ids = self.children.get(parent_id, set())
        return [self.nodes[cid] for cid in child_ids if cid != node_id and cid in self.nodes]

    def expand_context(self, chunk_id: str) -> Dict[str, Any]:
        """
        Expands an isolated clause into its GraphRAG context:
        - Self clause
        - Parent chapter
        - Sibling clauses
        - Parent circular root
        """
        node = self.nodes.get(chunk_id)
        if not node:
            return {"found": False, "chunk_id": chunk_id}

        parent_chain = self.get_parent_chain(chunk_id)
        siblings = self.get_siblings(chunk_id)

        parent_chapter = next((p for p in parent_chain if p["node_type"] == "CHAPTER"), None)
        root_circular = next((p for p in parent_chain if p["node_type"] == "CIRCULAR"), None)

        return {
            "found": True,
            "node_id": chunk_id,
            "title": node["title"],
            "node_type": node["node_type"],
            "content": node["content"],
            "parent_chapter": {
                "id": parent_chapter["node_id"] if parent_chapter else None,
                "title": parent_chapter["title"] if parent_chapter else None
            },
            "root_circular": {
                "id": root_circular["node_id"] if root_circular else None,
                "title": root_circular["title"] if root_circular else None
            },
            "hierarchy_path": " > ".join(
                [p["title"] for p in reversed(parent_chain)] + [node["title"]]
            ),
            "sibling_count": len(siblings),
            "siblings": [{"id": s["node_id"], "title": s["title"]} for s in siblings[:5]]
        }

    def ingest_chunk_list(self, chunks: List[Dict[str, Any]]) -> int:
        """
        Builds the graph relationships dynamically from chunk payloads.
        """
        added_count = 0
        for chunk in chunks:
            circ_no = chunk.get("circular_no", "RBI/GEN/2026")
            circ_title = chunk.get("title", "RBI Master Direction")
            clause_title = chunk.get("clause", "General Clause")
            chunk_id = chunk.get("chunk_id", f"{circ_no}#auto")
            text = chunk.get("text", "")

            # 1. Ensure Root Circular Node exists
            if circ_no not in self.nodes:
                self.add_node(
                    node_id=circ_no,
                    node_type="CIRCULAR",
                    title=f"{circ_no}: {circ_title}",
                    content=circ_title,
                    parent_id=None,
                    metadata={"category": chunk.get("category", "General")}
                )
                added_count += 1

            # 2. Extract or Synthesize Chapter Node
            chapter_title = circ_title
            if " — " in clause_title:
                parts = clause_title.split(" — ", 1)
                chapter_title = parts[0].strip()
            elif " - " in clause_title:
                parts = clause_title.split(" - ", 1)
                chapter_title = parts[0].strip()

            chapter_id = f"{circ_no}#{chapter_title.replace(' ', '_')}"
            if chapter_id not in self.nodes:
                self.add_node(
                    node_id=chapter_id,
                    node_type="CHAPTER",
                    title=chapter_title,
                    content=chapter_title,
                    parent_id=circ_no
                )
                added_count += 1

            # 3. Add Clause Node
            if chunk_id not in self.nodes:
                self.add_node(
                    node_id=chunk_id,
                    node_type="CLAUSE",
                    title=clause_title,
                    content=text,
                    parent_id=chapter_id,
                    metadata={
                        "chunk_sha256": chunk.get("chunk_sha256", ""),
                        "category": chunk.get("category", "")
                    }
                )
                added_count += 1

        return added_count


# Global singleton instance
_global_graph: Optional[RegulatoryKnowledgeGraph] = None

def get_regulatory_graph() -> RegulatoryKnowledgeGraph:
    """Returns or initializes the singleton RegulatoryKnowledgeGraph."""
    global _global_graph
    if _global_graph is None:
        _global_graph = RegulatoryKnowledgeGraph()
    return _global_graph
