#!/usr/bin/env python3
"""Tests for build_openapi_health.py"""
from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

from build_openapi_health import build_payload, validate_openapi_doc  # noqa: E402


class TestOpenApiHealth(unittest.TestCase):
    def test_stub_invalid_when_bootstrap_complete(self):
        doc = {"openapi": "3.1.0", "paths": {}}
        cfg = {"openapi": {"contract_first": True}, "bootstrap": {"status": "complete"}}
        rep = validate_openapi_doc(doc, cfg, True)
        self.assertFalse(rep["valid"])
        self.assertTrue(rep["stub"])

    def test_stub_invalid_when_bootstrap_incomplete(self):
        doc = {"openapi": "3.1.0", "paths": {}}
        cfg = {"openapi": {"contract_first": True}, "bootstrap": {"status": "incomplete"}}
        rep = validate_openapi_doc(doc, cfg, False)
        self.assertFalse(rep["valid"])
        self.assertTrue(rep["stub"])

    def test_with_path_valid(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            api = root / "docs/api"
            api.mkdir(parents=True)
            (api / "openapi.yaml").write_text(
                "openapi: 3.1.0\ninfo:\n  title: T\n  version: 1.0.0\npaths:\n  /x:\n    get:\n      responses:\n        '200':\n          description: ok\n",
                encoding="utf-8",
            )
            (root / "project.config.yaml").write_text(
                "openapi:\n  path: docs/api/openapi.yaml\n  contract_first: true\nbootstrap:\n  status: complete\n",
                encoding="utf-8",
            )
            p = build_payload(root, root / "project.config.yaml")
            self.assertTrue(p["report"]["valid"])
            self.assertEqual(p["report"]["path_count"], 1)


if __name__ == "__main__":
    unittest.main()
