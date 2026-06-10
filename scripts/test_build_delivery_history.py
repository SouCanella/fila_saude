#!/usr/bin/env python3
"""Tests for build_delivery_history.parse_delivery_log"""
from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

from build_delivery_history import is_placeholder_entry, parse_delivery_log  # noqa: E402


class TestDeliverySlug(unittest.TestCase):
    def test_card_hub_evolucao(self):
        text = """---
## Entrega: [CARD-Hub-Evolucao] - Hub Evolução Completa P0–P2

Status: Concluída

Data/hora início: 2026-06-04 10:00
Data/hora fim: 2026-06-04 18:00

### Card

- ID: CARD-Hub-Evolucao
- Fase: SETUP

### Requisitos cobertos (REQs)

- REQ-Hub-Evolucao — spec: docs/specs/REQ-Hub-Evolucao-hub-evolucao.md
"""
        with tempfile.NamedTemporaryFile("w", suffix=".md", delete=False, encoding="utf-8") as f:
            f.write(text)
            path = Path(f.name)
        entries = parse_delivery_log(path)
        path.unlink()
        self.assertEqual(len(entries), 1)
        self.assertEqual(entries[0]["card_id"], "CARD-HUB-EVOLUCAO")
        self.assertIn("REQ-HUB-EVOLUCAO", entries[0]["req_ids"])
        self.assertEqual(entries[0]["phase"], "SETUP")


    def test_placeholder_card_xxx_skipped(self):
        text = """---
## Entrega: [CARD-XXX] - [Nome do card]

Status: Em andamento | Concluída | Bloqueada | Cancelada

Data/hora início: YYYY-MM-DD HH:mm
Data/hora fim: YYYY-MM-DD HH:mm

### Card

- ID: CARD-XXX
- Fase: FASE-1

### Requisitos cobertos (REQs)

- REQ-001 — spec: docs/specs/REQ-001-nome.md
"""
        with tempfile.NamedTemporaryFile("w", suffix=".md", delete=False, encoding="utf-8") as f:
            f.write(text)
            path = Path(f.name)
        entries = parse_delivery_log(path)
        path.unlink()
        self.assertEqual(entries, [])

    def test_is_placeholder_entry(self):
        self.assertTrue(is_placeholder_entry("CARD-XXX", "Concluída", "2026-01-01", "Foo"))
        self.assertTrue(
            is_placeholder_entry("CARD-001", "Em andamento | Concluída", None, "Bar")
        )
        self.assertFalse(is_placeholder_entry("CARD-001", "Concluída", "2026-01-01", "Bar"))


if __name__ == "__main__":
    unittest.main()
