#!/usr/bin/env python3
"""Tests for resolve_next_step retro per phase."""
from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

from resolve_next_step import pending_retro_phase, resolve_next_step  # noqa: E402


class TestRetroPerPhase(unittest.TestCase):
    def test_pending_retro_when_phase_complete(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            cards_dir = root / "docs/tracking/cards"
            cards_dir.mkdir(parents=True)
            planning = root / "docs/planning"
            planning.mkdir(parents=True)
            (planning / "mvp-phases.md").write_text(
                "| Fase | Objetivo | Ordem |\n|------|----------|-------|\n| FASE-1 | Core | 1 |\n",
                encoding="utf-8",
            )
            retro = root / "docs/meta/retrospectives"
            retro.mkdir(parents=True)
            (retro / "index.md").write_text(
                "| Fase | Status |\n|------|--------|\n| FASE-1 | pending |\n",
                encoding="utf-8",
            )
            for cid in ("CARD-001", "CARD-002"):
                (cards_dir / f"{cid}.md").write_text(
                    f"---\nid: {cid}\nphase: FASE-1\nstatus: done\n---\n",
                    encoding="utf-8",
                )
            cards = [
                {"id": "CARD-001", "status": "done", "phase": "FASE-1", "path": str(cards_dir / "CARD-001.md")},
                {"id": "CARD-002", "status": "done", "phase": "FASE-1", "path": str(cards_dir / "CARD-002.md")},
            ]
            self.assertEqual(pending_retro_phase(cards, root), "FASE-1")

    def test_resolve_prioritizes_retro_over_open_card(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            cfg = root / "project.config.yaml"
            cfg.write_text(
                "discovery:\n  status: complete\nbootstrap:\n  status: complete\n"
                "mvp_planning:\n  status: complete\nproject:\n  has_frontend: false\n",
                encoding="utf-8",
            )
            cards_dir = root / "docs/tracking/cards"
            cards_dir.mkdir(parents=True)
            planning = root / "docs/planning"
            planning.mkdir(parents=True)
            (planning / "mvp-phases.md").write_text(
                "| Fase | Objetivo | Ordem |\n|------|----------|-------|\n| FASE-1 | Core | 1 |\n",
                encoding="utf-8",
            )
            retro = root / "docs/meta/retrospectives"
            retro.mkdir(parents=True)
            (retro / "index.md").write_text(
                "| Fase | Status |\n|------|--------|\n| FASE-1 | pending |\n",
                encoding="utf-8",
            )
            (cards_dir / "CARD-001.md").write_text(
                "---\nid: CARD-001\nphase: FASE-1\nstatus: done\n---\n",
                encoding="utf-8",
            )
            (cards_dir / "CARD-002.md").write_text(
                "---\nid: CARD-002\nphase: FASE-2\nstatus: open\n---\n",
                encoding="utf-8",
            )
            result = resolve_next_step(root, cfg, cards_dir, root / "docs/specs", None)
            self.assertEqual(result["phase"], "retro")
            self.assertIn("FASE-1", result["label"])


if __name__ == "__main__":
    unittest.main()
