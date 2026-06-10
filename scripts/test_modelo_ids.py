#!/usr/bin/env python3
"""Tests for modelo_ids.py"""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

from modelo_ids import (  # noqa: E402
    DELIVERY_HEADER_RE,
    find_card_ids,
    find_req_ids,
    normalize_req_id,
    parse_phase_from_block,
)


class TestModeloIds(unittest.TestCase):
    def test_card_numeric_and_slug(self):
        self.assertEqual(find_card_ids("CARD-001 e CARD-Hub-Evolucao"), ["CARD-001", "CARD-HUB-EVOLUCAO"])

    def test_req_slug(self):
        self.assertIn("REQ-HUB-POC-READY", find_req_ids("spec REQ-Hub-PoC-Ready ok"))

    def test_no_false_card(self):
        self.assertEqual(find_card_ids("CARD only word"), [])

    def test_normalize_numeric(self):
        self.assertEqual(normalize_req_id("req-1"), "REQ-001")

    def test_normalize_slug(self):
        self.assertEqual(normalize_req_id("REQ-Hub-Evolucao"), "REQ-HUB-EVOLUCAO")

    def test_delivery_header_slug(self):
        block = "## Entrega: [CARD-Hub-Evolucao] - Hub Evolução"
        m = DELIVERY_HEADER_RE.search(block)
        self.assertIsNotNone(m)
        self.assertEqual(m.group(1).upper(), "CARD-HUB-EVOLUCAO")

    def test_phase_setup(self):
        block = "### Card\n\n- Fase: SETUP\n"
        self.assertEqual(parse_phase_from_block(block), "SETUP")


if __name__ == "__main__":
    unittest.main()
