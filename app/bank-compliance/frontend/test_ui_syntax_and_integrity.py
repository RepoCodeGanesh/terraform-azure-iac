"""
Frontend UI Integrity and Syntax Validation Test Suite
Tests JSX/JS components for balanced braces, valid relative imports,
component prop wiring, and architectural cohesion.
"""

import os
import re
import unittest

FRONTEND_SRC = os.path.dirname(os.path.abspath(__file__))
COMPONENTS_DIR = os.path.join(FRONTEND_SRC, "src", "components")
SRC_DIR = os.path.join(FRONTEND_SRC, "src")

class TestUIComponentsIntegrity(unittest.TestCase):

    def test_all_expected_component_files_exist(self):
        """Verify all core components exist in src/ and src/components/."""
        expected_src = ["App.jsx", "main.jsx", "index.css"]
        expected_components = [
            "ChatWindow.jsx",
            "CommandCenter.jsx",
            "GovernanceCenter.jsx",
            "GenAIOpsDashboard.jsx",
            "RedlineStudio.jsx",
            "ArchitectureInspectorModal.jsx",
            "CitationCard.jsx",
            "MarkdownRenderer.jsx",
            "PIIBanner.jsx",
            "ErrorBoundary.jsx"
        ]

        for fname in expected_src:
            fpath = os.path.join(SRC_DIR, fname)
            self.assertTrue(os.path.exists(fpath), f"Missing src file: {fname}")

        for fname in expected_components:
            fpath = os.path.join(COMPONENTS_DIR, fname)
            self.assertTrue(os.path.exists(fpath), f"Missing component file: {fname}")

    def test_architecture_inspector_modal_tabs(self):
        """Verify ArchitectureInspectorModal has all 5 learning tabs."""
        modal_path = os.path.join(COMPONENTS_DIR, "ArchitectureInspectorModal.jsx")
        with open(modal_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Check for 5 core frontier interview tabs
        self.assertIn("stategraph", content)
        self.assertIn("graphrag", content)
        self.assertIn("mcp", content)
        self.assertIn("dossier", content)
        self.assertIn("interview", content)

        # Check for 3 MCP tools
        self.assertIn("calculate_fldg_cap", content)
        self.assertIn("check_data_localization", content)
        self.assertIn("verify_vcip_identity_step", content)

        # Check for cryptographic SHA-256 digest reference
        self.assertIn("SHA-256", content)
        self.assertIn("dossier_digest", content)

    def test_app_jsx_wires_inspector_modal(self):
        """Verify App.jsx imports and passes onOpenInspector to ChatWindow and renders Modal."""
        app_path = os.path.join(SRC_DIR, "App.jsx")
        with open(app_path, "r", encoding="utf-8") as f:
            content = f.read()

        self.assertIn("ArchitectureInspectorModal", content)
        self.assertIn("isInspectorOpen", content)
        self.assertIn("onOpenInspector", content)
        self.assertIn("<ArchitectureInspectorModal", content)

    def test_chatwindow_wires_inspector_button(self):
        """Verify ChatWindow.jsx receives onOpenInspector and renders trigger buttons."""
        chat_path = os.path.join(COMPONENTS_DIR, "ChatWindow.jsx")
        with open(chat_path, "r", encoding="utf-8") as f:
            content = f.read()

        self.assertIn("onOpenInspector", content)
        self.assertTrue(
            "Architecture & Interview Inspector" in content or "Architecture &amp; Interview Inspector" in content,
            "ChatWindow should contain Architecture Inspector button text"
        )

    def test_balanced_jsx_braces_across_all_components(self):
        """Verify curly braces, brackets, and parentheses are well-balanced in all JSX files."""
        for root, _, files in os.walk(SRC_DIR):
            for file in files:
                if file.endswith((".jsx", ".js")):
                    fpath = os.path.join(root, file)
                    with open(fpath, "r", encoding="utf-8") as f:
                        text = f.read()

                    # Strip comments and string literals to test structural bracket balance
                    stripped = re.sub(r'//.*', '', text)
                    stripped = re.sub(r'/\*[\s\S]*?\*/', '', stripped)
                    stripped = re.sub(r'\'[^\'\\]*(?:\\.[^\'\\]*)*\'', "''", stripped)
                    stripped = re.sub(r'"[^"\\]*(?:\\.[^"\\]*)*"', '""', stripped)
                    stripped = re.sub(r'`[^`\\]*(?:\\.[^`\\]*)*`', '``', stripped)

                    counts = {
                        '{': stripped.count('{'),
                        '}': stripped.count('}'),
                        '(': stripped.count('('),
                        ')': stripped.count(')'),
                        '[': stripped.count('['),
                        ']': stripped.count(']')
                    }

                    self.assertEqual(
                        counts['{'], counts['}'],
                        f"{file} has unbalanced curly braces: {counts['{']} open vs {counts['}']} close"
                    )
                    self.assertEqual(
                        counts['('], counts[')'],
                        f"{file} has unbalanced parentheses: {counts['(']} open vs {counts[')']} close"
                    )
                    self.assertEqual(
                        counts['['], counts[']'],
                        f"{file} has unbalanced square brackets: {counts['[']} open vs {counts[']']} close"
                    )

    def test_internal_relative_imports_resolve(self):
        """Verify all internal relative import paths resolve to real files."""
        for root, _, files in os.walk(SRC_DIR):
            for file in files:
                if file.endswith((".jsx", ".js")):
                    fpath = os.path.join(root, file)
                    with open(fpath, "r", encoding="utf-8") as f:
                        lines = f.readlines()

                    for line in lines:
                        match = re.search(r'from\s+[\'"](\.[^\'"]+)[\'"]', line)
                        if match:
                            rel_import = match.group(1)
                            # Target could be .jsx, .js, or exact file like .css
                            base_target = os.path.normpath(os.path.join(root, rel_import))
                            resolved = False
                            for ext in ["", ".jsx", ".js", ".css"]:
                                if os.path.isfile(base_target + ext):
                                    resolved = True
                                    break
                            self.assertTrue(
                                resolved,
                                f"In {file}: Could not resolve import '{rel_import}' (target: {base_target})"
                            )

if __name__ == "__main__":
    unittest.main(verbosity=2)
