#!/usr/bin/env python3
"""Tests sync-card-github frontmatter helper (dry-run)."""
from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

from update_card_frontmatter import update_frontmatter  # noqa: E402


class TestSyncFrontmatter(unittest.TestCase):
    def test_dry_run_sets_external_url(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "CARD-001.md"
            path.write_text("---\nid: CARD-001\nstatus: open\n---\n# T\n", encoding="utf-8")
            out = update_frontmatter(
                path,
                {"external_url": "https://github.com/o/r/issues/42"},
                dry_run=True,
            )
            self.assertIn("external_url: https://github.com/o/r/issues/42", out)
            self.assertNotIn("external_url", path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
