"""
2026/2027 Frontier Test Suite for BankCompliance AI
Validates the 3 next-generation capabilities:
1. GraphRAG Hierarchical Regulatory Knowledge Mesh (DAG Traversal)
2. Model Context Protocol (MCP) Agent Tool Federation (JSON-RPC)
3. Algorithmic Compliance Attestation Dossier (EU AI Act & RBI Conformity)
Zero cloud cost -- executes in-memory.
"""

import sys
import unittest
from pathlib import Path

# Add backend directory to sys.path
BACKEND_DIR = Path(__file__).resolve().parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app.services.graph_rag import RegulatoryKnowledgeGraph, get_regulatory_graph
from app.services.mcp_bridge import MCPToolBridge, get_mcp_bridge, MCP_PROTOCOL_VERSION
from app.services.compliance_dossier import ComplianceDossierGenerator, get_compliance_dossier_generator
from app.services.qdrant_service import search_with_graph_hierarchy


class TestGraphRAGKnowledgeMesh(unittest.TestCase):
    """Pillar 1: Tests for GraphRAG Hierarchical Knowledge Mesh."""

    def setUp(self):
        self.graph = RegulatoryKnowledgeGraph()
        self.sample_chunks = [
            {
                "circular_no": "RBI/2023-24/53",
                "title": "Default Loss Guarantee in Digital Lending",
                "clause": "Chapter II — Eligibility of REs and LSPs",
                "chunk_id": "RBI/2023-24/53#c1",
                "text": "REs shall enter into DLG arrangements only with LSPs with which they have an outsourcing arrangement.",
                "category": "Digital Lending"
            },
            {
                "circular_no": "RBI/2023-24/53",
                "title": "Default Loss Guarantee in Digital Lending",
                "clause": "Chapter II — Cap on DLG - 5% Maximum",
                "chunk_id": "RBI/2023-24/53#c2",
                "text": "RE shall ensure that total amount of DLG cover on any outstanding loan portfolio shall not exceed 5%.",
                "category": "Digital Lending"
            },
            {
                "circular_no": "RBI/2023-24/53",
                "title": "Default Loss Guarantee in Digital Lending",
                "clause": "Chapter III — Invocation of DLG",
                "chunk_id": "RBI/2023-24/53#c3",
                "text": "The RE shall invoke DLG within a maximum period of 120 days of overdue, unless made good by the borrower.",
                "category": "Digital Lending"
            }
        ]
        self.graph.ingest_chunk_list(self.sample_chunks)

    def test_01_graph_ingestion_node_count(self):
        """Graph ingests circular, chapter, and clause nodes."""
        self.assertGreaterEqual(len(self.graph.nodes), 4)

    def test_02_circular_root_node_exists(self):
        """Circular root node is created with correct type."""
        root = self.graph.get_node("RBI/2023-24/53")
        self.assertIsNotNone(root)
        self.assertEqual(root["node_type"], "CIRCULAR")

    def test_03_clause_parent_chain(self):
        """Clause traverses up to Chapter and Circular."""
        chain = self.graph.get_parent_chain("RBI/2023-24/53#c2")
        self.assertGreaterEqual(len(chain), 2)
        node_types = [n["node_type"] for n in chain]
        self.assertIn("CHAPTER", node_types)
        self.assertIn("CIRCULAR", node_types)

    def test_04_sibling_clause_retrieval(self):
        """Clauses in the same chapter discover siblings."""
        siblings = self.graph.get_siblings("RBI/2023-24/53#c2")
        self.assertGreaterEqual(len(siblings), 1)
        sibling_ids = [s["node_id"] for s in siblings]
        self.assertIn("RBI/2023-24/53#c1", sibling_ids)

    def test_05_expand_context_hierarchy_path(self):
        """expand_context returns formatted hierarchy breadcrumbs."""
        expanded = self.graph.expand_context("RBI/2023-24/53#c2")
        self.assertTrue(expanded["found"])
        self.assertIn("RBI/2023-24/53", expanded["hierarchy_path"])
        self.assertIn("Chapter II", expanded["hierarchy_path"])

    def test_06_nonexistent_node_expansion(self):
        """Gracefully handles missing chunk IDs."""
        res = self.graph.expand_context("UNKNOWN#c999")
        self.assertFalse(res["found"])

    def test_07_search_with_graph_hierarchy_qdrant(self):
        """Integration with Qdrant service injects graph_rag metadata."""
        results = search_with_graph_hierarchy("What is the maximum FLDG guarantee allowed?", limit=2)
        self.assertIsInstance(results, list)
        if len(results) > 0:
            top = results[0]
            self.assertIn("graph_rag", top)


class TestMCPToolBridge(unittest.TestCase):
    """Pillar 2: Tests for Model Context Protocol (MCP) Tool Bridge."""

    def setUp(self):
        self.bridge = MCPToolBridge()

    def test_08_mcp_tools_manifest(self):
        """MCP manifest lists all 3 compliance tools."""
        manifest = self.bridge.list_tools()
        self.assertEqual(manifest["protocol_version"], MCP_PROTOCOL_VERSION)
        tool_names = [t["name"] for t in manifest["tools"]]
        self.assertIn("calculate_fldg_cap", tool_names)
        self.assertIn("check_data_localization", tool_names)
        self.assertIn("verify_vcip_identity_step", tool_names)

    def test_09_calculate_fldg_cap_compliant(self):
        """5% or less FLDG guarantee is compliant."""
        res = self.bridge.call_tool("calculate_fldg_cap", {
            "total_portfolio_inr": 100000000.0,
            "guarantee_amount_inr": 4500000.0  # 4.5%
        })
        self.assertTrue(res["compliant"])
        self.assertEqual(res["actual_percentage"], 4.5)
        self.assertEqual(res["excess_amount_inr"], 0.0)

    def test_10_calculate_fldg_cap_violation(self):
        """Excess guarantee over 5% flags violation and computes exact excess amount."""
        res = self.bridge.call_tool("calculate_fldg_cap", {
            "total_portfolio_inr": 100000000.0,
            "guarantee_amount_inr": 7000000.0  # 7.0%
        })
        self.assertFalse(res["compliant"])
        self.assertEqual(res["actual_percentage"], 7.0)
        self.assertEqual(res["excess_amount_inr"], 2000000.0)
        self.assertIn("deduct excess 100%", res["action_required"])

    def test_11_check_data_localization_onshore(self):
        """Indian storage region passes data localization."""
        res = self.bridge.call_tool("check_data_localization", {
            "data_category": "card_payment_data",
            "storage_region": "Central India (Pune/Mumbai)"
        })
        self.assertTrue(res["compliant"])
        self.assertEqual(res["status"], "APPROVED_ONSHORE")

    def test_12_check_data_localization_offshore_violation(self):
        """Offshore storage flags localization violation."""
        res = self.bridge.call_tool("check_data_localization", {
            "data_category": "upi_transaction_logs",
            "storage_region": "Singapore (East Asia)"
        })
        self.assertFalse(res["compliant"])
        self.assertEqual(res["status"], "VIOLATION_OFFSHORE_STORAGE")

    def test_13_verify_vcip_identity_success(self):
        """Full V-CIP verification passes."""
        res = self.bridge.call_tool("verify_vcip_identity_step", {
            "live_geotag_in_india": True,
            "facial_liveness_verified": True,
            "aadhaar_xml_or_digilocker": True
        })
        self.assertTrue(res["compliant"])
        self.assertEqual(res["status"], "V_CIP_VERIFIED")

    def test_14_verify_vcip_identity_failure(self):
        """Missing geotag or liveness blocks V-CIP."""
        res = self.bridge.call_tool("verify_vcip_identity_step", {
            "live_geotag_in_india": False,
            "facial_liveness_verified": True,
            "aadhaar_xml_or_digilocker": True
        })
        self.assertFalse(res["compliant"])
        self.assertIn("Live Geolocation inside India", res["failed_checks"])

    def test_15_mcp_jsonrpc_handler(self):
        """Standard JSON-RPC 2.0 dispatch for tools/call."""
        rpc_req = {
            "jsonrpc": "2.0",
            "id": "req-001",
            "method": "tools/call",
            "params": {
                "name": "calculate_fldg_cap",
                "arguments": {
                    "total_portfolio_inr": 50000000.0,
                    "guarantee_amount_inr": 2500000.0
                }
            }
        }
        resp = self.bridge.handle_jsonrpc(rpc_req)
        self.assertEqual(resp["id"], "req-001")
        self.assertIn("result", resp)
        self.assertFalse(resp["result"]["isError"])


class TestComplianceDossier(unittest.TestCase):
    """Pillar 3: Tests for Algorithmic Compliance Attestation Dossier."""

    def setUp(self):
        self.generator = ComplianceDossierGenerator()

    def test_16_dossier_compilation_schema(self):
        """Compiles regulator-ready audit dossier with mandatory top-level keys."""
        dossier = self.generator.compile_dossier()
        required_keys = [
            "dossier_id", "dossier_version", "generated_at", "organization",
            "regulatory_frameworks", "cryptographic_integrity",
            "governance_scorecard", "artifacts"
        ]
        for k in required_keys:
            self.assertIn(k, dossier)

    def test_17_dossier_cryptographic_digest(self):
        """Dossier includes valid SHA-256 integrity hash."""
        dossier = self.generator.compile_dossier()
        digest = dossier["cryptographic_integrity"]["dossier_digest"]
        self.assertTrue(digest.startswith("sha256:"))
        self.assertEqual(len(digest), 71)  # sha256: + 64 hex chars

    def test_18_dossier_includes_model_card(self):
        """Dossier integrates LoRA Model Card v1.0.0."""
        dossier = self.generator.compile_dossier()
        artifacts = dossier["artifacts"]
        self.assertIn("model_card", artifacts)
        self.assertIn("base_model", artifacts["model_card"])

    def test_19_dossier_includes_pyrit_redteam(self):
        """Dossier incorporates PyRIT red team security attestation."""
        dossier = self.generator.compile_dossier()
        artifacts = dossier["artifacts"]
        self.assertIn("redteam_security_attestation", artifacts)
        redteam = artifacts["redteam_security_attestation"]
        self.assertEqual(redteam.get("resilience_rate_percent"), 100.0)

    def test_20_dossier_governance_scorecard(self):
        """Dossier governance scorecard reflects approved statutory status."""
        dossier = self.generator.compile_dossier()
        scorecard = dossier["governance_scorecard"]
        self.assertEqual(scorecard["overall_status"], "STATUTORY_APPROVED")
        self.assertEqual(scorecard["idle_cloud_cost"], "$0.00 / month")


if __name__ == "__main__":
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    suite.addTests(loader.loadTestsFromTestCase(TestGraphRAGKnowledgeMesh))
    suite.addTests(loader.loadTestsFromTestCase(TestMCPToolBridge))
    suite.addTests(loader.loadTestsFromTestCase(TestComplianceDossier))

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    sys.exit(0 if result.wasSuccessful() else 1)
