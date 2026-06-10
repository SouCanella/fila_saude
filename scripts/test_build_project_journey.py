#!/usr/bin/env python3
"""Tests for build_project_journey.py"""
from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

from build_delivery_history import parse_delivery_log  # noqa: E402
from build_project_journey import (  # noqa: E402
    bootstrap_progress,
    build_activity,
    build_lifecycle_phases,
    card_effort_from_timeline,
    detect_data_mode,
    enrich_deliveries,
    has_tracked_process_activity,
    parse_vision_review,
    phase_milestone_dates,
)


class TestDeliveryParse(unittest.TestCase):
    def test_parse_enriched_fields(self):
        text = """---
## Entrega: [CARD-001] - Login

Status: Concluída

Data/hora início: 2026-06-01 10:00
Branch: feature/x
PR/MR: #1

### Card

- Fase: FASE-1
"""
        with tempfile.NamedTemporaryFile("w", suffix=".md", delete=False) as f:
            f.write(text)
            path = Path(f.name)
        entries = parse_delivery_log(path)
        path.unlink()
        self.assertEqual(entries[0]["card_id"], "CARD-001")
        self.assertEqual(entries[0]["phase"], "FASE-1")
        self.assertEqual(entries[0]["branch"], "feature/x")


class TestDataMode(unittest.TestCase):
    def test_template_uses_showcase(self):
        backlog = ROOT / "docs/backlog/mvp-backlog.md"
        mode = detect_data_mode(ROOT, backlog, ROOT / "docs/specs")
        self.assertEqual(mode, "showcase")

    def test_mixed_real_backlog_showcase_specs(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            real_backlog = root / "backlog.md"
            real_backlog.write_text("| REQ-Hub-Evolucao | SETUP | … |\n", encoding="utf-8")
            showcase_specs = ROOT / "docs/examples/hub-showcase/specs"
            mode = detect_data_mode(root, real_backlog, showcase_specs)
            self.assertEqual(mode, "mixed")


class TestLifecycle(unittest.TestCase):
    def test_discovery_pending(self):
        cfg = {
            "discovery": {"status": "pending"},
            "bootstrap": {"status": "incomplete", "sections": {"A_identidade": "pending"}},
            "mvp_planning": {"status": "pending"},
            "project": {"has_frontend": False},
        }
        phases = build_lifecycle_phases(cfg, [], [], [], {})
        self.assertEqual(phases[0]["id"], "discovery")
        self.assertEqual(phases[0]["status"], "pending")


class TestEnrichDeliveries(unittest.TestCase):
    def test_merge_card_and_log(self):
        entries = [{"card_id": "CARD-001", "title": "T", "status": "Concluída", "req_ids": ["REQ-001"]}]
        cards = [{"id": "CARD-001", "status": "done", "phase": "FASE-1", "title": "T", "req_ids": ["REQ-001"]}]
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            cards_dir = root / "cards"
            cards_dir.mkdir()
            (cards_dir / "CARD-001.md").write_text(
                "---\nid: CARD-001\nphase: FASE-1\nstatus: done\nreq_ids: [REQ-001]\n---\n",
                encoding="utf-8",
            )
            specs_dir = root / "specs"
            specs_dir.mkdir()
            timeline = {"rounds": [{"card_id": "CARD-001", "human_active_seconds": 100, "ai_execution_seconds": 50}]}
            out = enrich_deliveries(root, entries, cards, cards_dir, specs_dir, {}, timeline)
            self.assertEqual(len(out), 1)
            self.assertEqual(out[0]["phase"], "FASE-1")
            self.assertEqual(out[0]["effort"]["human_active_seconds"], 100)


class TestBootstrapComplete(unittest.TestCase):
    def test_empty_sections_complete(self):
        done, total, pending = bootstrap_progress({"bootstrap": {"status": "complete", "sections": {}}})
        self.assertIsNone(total)
        self.assertIsNone(pending)


class TestMilestoneDates(unittest.TestCase):
    def test_fase_dates(self):
        ms = [
            {"activity": "phase_delivery_start", "phase": "FASE-1", "started_at": "2026-01-01"},
            {"activity": "phase_delivery_end", "phase": "FASE-1", "ended_at": "2026-01-05"},
        ]
        d = phase_milestone_dates(ms, "FASE-1")
        self.assertEqual(d["started_at"], "2026-01-01")
        self.assertEqual(d["ended_at"], "2026-01-05")


class TestCardEffort(unittest.TestCase):
    def test_sum_rounds(self):
        tl = {"rounds": [{"card_id": "CARD-001", "human_active_seconds": 10, "ai_execution_seconds": 5}]}
        e = card_effort_from_timeline(tl, "CARD-001")
        self.assertEqual(e["human_active_seconds"], 10)


class TestActivityFeed(unittest.TestCase):
    def test_virgin_project_skips_artifact_events(self):
        self.assertFalse(has_tracked_process_activity({}, [], []))
        acts = build_activity(ROOT, [{"path": "x", "resolved": ROOT / "README.md", "label": "X"}], {}, [], [])
        self.assertEqual(acts, [])

    def test_round_enables_artifact_events(self):
        timeline = {"rounds": [{"at": "2026-01-01", "source": "agent_turn", "activity": "discovery"}]}
        self.assertTrue(has_tracked_process_activity(timeline, [], []))
        acts = build_activity(
            ROOT,
            [{"path": "README.md", "resolved": ROOT / "README.md", "label": "Readme", "phase": "bootstrap"}],
            timeline,
            [],
            [],
        )
        self.assertTrue(any(a.get("source") == "artifact" for a in acts))


class TestVisionReview(unittest.TestCase):
    def test_checklist_items(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            disc = root / "docs/discovery"
            disc.mkdir(parents=True)
            (disc / "vision-review.md").write_text("- [x] Item ok\n- [ ] Item pendente\n", encoding="utf-8")
            vr = parse_vision_review(root)
            self.assertEqual(len(vr["items"]), 2)
            self.assertFalse(vr["checklist_ok"])


if __name__ == "__main__":
    unittest.main()
