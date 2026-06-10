#!/usr/bin/env python3
"""CHANGELOG + git tags → release.data.json."""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def load_yaml(path: Path) -> dict:
    if not path.exists():
        return {}
    try:
        import yaml  # type: ignore
    except ImportError:
        return {}
    with path.open(encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}
    return data if isinstance(data, dict) else {}


def resolve_changelog(root: Path, cfg: dict) -> Path:
    rel = ((cfg.get("git") or {}).get("release") or {}).get("changelog") or "CHANGELOG.md"
    p = root / rel
    return p if p.exists() else root / "CHANGELOG.md"


def git_latest_tag(root: Path, prefix: str = "v") -> dict | None:
    try:
        out = subprocess.check_output(
            ["git", "describe", "--tags", "--abbrev=0"],
            cwd=root,
            text=True,
            stderr=subprocess.DEVNULL,
        ).strip()
        if not out:
            return None
        date_out = subprocess.check_output(
            ["git", "log", "-1", "--format=%aI", out],
            cwd=root,
            text=True,
            stderr=subprocess.DEVNULL,
        ).strip()
        return {"tag": out, "date": date_out or None}
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None


def changelog_preview(path: Path, limit: int = 400) -> str:
    if not path.exists():
        return ""
    text = path.read_text(encoding="utf-8")
    m = re.search(r"^##\s+\[?[^\]\n]+\]?", text, re.M)
    if m:
        chunk = text[m.start() : m.start() + limit]
        return chunk.strip()
    return text[:limit].strip()


def build_payload(root: Path, config_path: Path) -> dict:
    cfg = load_yaml(config_path)
    release_cfg = (cfg.get("git") or {}).get("release") or {}
    changelog_path = resolve_changelog(root, cfg)
    tag_info = git_latest_tag(root, release_cfg.get("tag_prefix", "v"))
    initial = release_cfg.get("initial_version", "0.1.0")
    return {
        "built_at": datetime.now(timezone.utc).isoformat(),
        "changelog_path": str(changelog_path.relative_to(root)) if changelog_path.is_relative_to(root) else str(changelog_path),
        "report": {
            "last_version": tag_info["tag"].lstrip("v") if tag_info else initial,
            "last_tag": tag_info["tag"] if tag_info else None,
            "last_tag_date": tag_info["date"] if tag_info else None,
            "changelog_preview": changelog_preview(changelog_path),
            "strategy": release_cfg.get("strategy", "semver"),
        },
    }


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--root", type=Path, default=ROOT)
    p.add_argument("--config", type=Path)
    p.add_argument("--json", type=Path, required=True)
    args = p.parse_args()
    root = args.root.resolve()
    config = args.config or root / "project.config.yaml"
    payload = build_payload(root, config)
    args.json.parent.mkdir(parents=True, exist_ok=True)
    args.json.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"OK: {args.json}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
