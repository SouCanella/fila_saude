#!/usr/bin/env python3
"""Gera stubs de teste a partir do plano TDD nas specs (quality-health)."""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from quality_spec_parser import (  # noqa: E402
    LAYER_LABELS,
    _CTX,
    iter_plan_cases,
    set_paths,
)


def _slug(text: str, max_len: int = 48) -> str:
    s = re.sub(r"[^a-zA-Z0-9]+", " ", text or "case").strip().lower()
    s = "_".join(s.split())[:max_len] or "case"
    return s


def _escape_comment(s: str | None) -> str:
    return (s or "").replace("*/", "* /").replace("\n", " ")


def stub_content(case: dict) -> str:
    req = case["req_id"]
    layer = case["layer"]
    scenario = case.get("scenario") or case.get("business_flow") or "cenário"
    title = case.get("business_flow") or scenario
    persona = case.get("persona")
    steps = case.get("steps_summary")
    expected = case.get("expected_result")
    meta = [
        f" * {req} — {_escape_comment(title)}",
        f" * Camada: {LAYER_LABELS.get(layer, layer)}",
    ]
    if persona:
        meta.append(f" * Persona: {_escape_comment(persona)}")
    if steps:
        meta.append(f" * Passos: {_escape_comment(steps)}")
    if expected:
        meta.append(f" * Resultado: {_escape_comment(expected)}")
    meta.append(f" * @req {req}")
    header = "/**\n" + "\n".join(meta) + "\n * TDD red — implementar conforme spec\n */"

    if layer == "e2e":
        name = _escape_comment(title).replace("'", "\\'")
        return f"""import {{ test, expect }} from '@playwright/test';

{header}
test('{name} @req {req}', async ({{ page }}) => {{
  test.fail(true, 'TDD red — implementar conforme docs/specs');
  await page.goto('/');
  expect(true).toBe(false);
}});
"""

    if layer == "unit_front" or (case.get("file") or "").endswith(".tsx"):
        it_name = _escape_comment(scenario).replace("'", "\\'")
        return f"""import {{ describe, it, expect }} from 'vitest';

{header}
describe('{req}', () => {{
  it('{it_name}', () => {{
    expect(true).toBe(false); // TDD red
  }});
}});
"""

    if layer in ("integration", "contract"):
        it_name = _escape_comment(scenario).replace("'", "\\'")
        return f"""import {{ describe, it, expect }} from 'vitest';

{header}
describe('{req} — {layer}', () => {{
  it('{it_name}', async () => {{
    expect(true).toBe(false); // TDD red
  }});
}});
"""

    it_name = _escape_comment(scenario).replace("'", "\\'")
    return f"""import {{ describe, it, expect }} from 'vitest';

{header}
describe('{req}', () => {{
  it('{it_name}', () => {{
    expect(true).toBe(false); // TDD red
  }});
}});
"""


def main() -> int:
    p = argparse.ArgumentParser(description="Scaffold test files from REQ specs")
    p.add_argument("--root", type=Path)
    p.add_argument("--backlog", type=Path)
    p.add_argument("--specs-dir", type=Path)
    p.add_argument("--req", dest="req_id", help="Só este REQ (ex. REQ-001)")
    p.add_argument("--dry-run", action="store_true")
    p.add_argument("--include-pending", action="store_true", help="Inclui linhas com status pending na spec")
    args = p.parse_args()

    if args.root:
        _CTX["root"] = args.root.resolve()
    set_paths(root=args.root, backlog=args.backlog, specs_dir=args.specs_dir)

    root = _CTX["root"]
    created = 0
    skipped = 0

    for case in iter_plan_cases(args.req_id):
        if case.get("spec_status") in ("n/a",) and not args.include_pending:
            continue
        if case.get("spec_status") == "pending" and not args.include_pending:
            continue
        fp = case.get("file")
        if not fp:
            print(f"PULAR: {case['req_id']} [{case['layer']}] sem arquivo na spec — {case.get('scenario')}")
            skipped += 1
            continue
        target = root / fp
        if target.exists():
            print(f"EXISTE: {fp}")
            skipped += 1
            continue
        content = stub_content(case)
        if args.dry_run:
            print(f"CRIARIA: {fp} ({case['req_id']} / {case['layer']})")
            created += 1
            continue
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")
        print(f"CRIADO: {fp}")
        created += 1

    print(f"OK: {created} arquivo(s) {'(dry-run)' if args.dry_run else 'criado(s)'}, {skipped} ignorado(s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
