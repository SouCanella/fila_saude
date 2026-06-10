#!/usr/bin/env python3
"""Atualiza campos no frontmatter YAML de CARD MD."""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


def update_frontmatter(path: Path, updates: dict[str, str], dry_run: bool = False) -> str:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---"):
        raise ValueError("sem frontmatter")
    end = text.find("---", 3)
    if end < 0:
        raise ValueError("frontmatter inválido")
    fm = text[3:end]
    body = text[end + 3 :]
    lines = fm.splitlines()
    out_lines = []
    seen = set()
    for line in lines:
        key = line.split(":", 1)[0].strip() if ":" in line else ""
        if key in updates:
            out_lines.append(f"{key}: {updates[key]}")
            seen.add(key)
        else:
            out_lines.append(line)
    for key, val in updates.items():
        if key not in seen:
            out_lines.append(f"{key}: {val}")
    new_fm = "\n".join(out_lines).rstrip() + "\n"
    new_text = f"---\n{new_fm}---{body}"
    if dry_run:
        return new_text
    path.write_text(new_text, encoding="utf-8")
    return new_text


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("card_path", type=Path)
    p.add_argument("--set", action="append", default=[], help="key=value")
    p.add_argument("--dry-run", action="store_true")
    args = p.parse_args()
    updates = {}
    for item in args.set:
        k, _, v = item.partition("=")
        updates[k.strip()] = v.strip()
    result = update_frontmatter(args.card_path, updates, dry_run=args.dry_run)
    if args.dry_run:
        print(result)
    return 0


if __name__ == "__main__":
    sys.exit(main())
