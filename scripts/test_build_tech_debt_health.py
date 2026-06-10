#!/usr/bin/env python3
"""Tests for build_tech_debt_health.py"""
from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

from build_tech_debt_health import build_payload, is_critical_open  # noqa: E402


class TestTechDebt(unittest.TestCase):
    def test_critical_open(self):
        self.assertTrue(is_critical_open({"risk": "Crítica", "status": "open"}))
        self.assertFalse(is_critical_open({"risk": "Crítica", "status": "resolved"}))

    def test_empty_table(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "docs").mkdir()
            (root / "docs/tech-debt.md").write_text(
                "| ID | Descrição | Motivo | Risco | REQ | Data | Prazo | Status |\n|---|---|---|---|---|---|---|---|\n",
                encoding="utf-8",
            )
            p = build_payload(root)
            self.assertEqual(p["report"]["critical_open_count"], 0)


if __name__ == "__main__":
    unittest.main()
