#!/usr/bin/env python3
"""Servidor Project Hub — docs/meta/ + API refresh/run-tests."""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path


class ProjectHubHandler(SimpleHTTPRequestHandler):
    repo_root: Path = Path(".")
    serve_dir: Path = Path(".")
    build_script: Path | None = None
    run_script: Path | None = None

    def log_message(self, fmt: str, *args) -> None:
        if self.path.startswith("/api/"):
            sys.stderr.write(f"[hub-api] {self.address_string()} {fmt % args}\n")
        elif not self.path.endswith((".data.json", ".css", ".js")):
            super().log_message(fmt, *args)

    def end_headers(self) -> None:
        self.send_header("Cache-Control", "no-store")
        super().end_headers()

    def do_OPTIONS(self) -> None:
        self.send_response(204)
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_POST(self) -> None:
        if self.path == "/api/refresh":
            self._handle_refresh()
        elif self.path == "/api/run-tests":
            self._handle_run_tests()
        else:
            self.send_error(404, "Not found")

    def _send_json(self, code: int, payload: dict) -> None:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _run_script(self, script: Path | None) -> tuple[bool, str]:
        if not script or not script.is_file():
            return False, "Script não configurado"
        proc = subprocess.run(
            [str(script)],
            cwd=self.repo_root,
            capture_output=True,
            text=True,
        )
        out = (proc.stdout or "") + (proc.stderr or "")
        if proc.returncode != 0:
            return False, out.strip() or f"exit {proc.returncode}"
        return True, out.strip()

    def _handle_refresh(self) -> None:
        ok, msg = self._run_script(self.build_script)
        self._send_json(200 if ok else 500, {"ok": ok, "action": "refresh", "message": msg})

    def _handle_run_tests(self) -> None:
        if self.run_script and self.run_script.is_file():
            ok, msg = self._run_script(self.run_script)
            if not ok:
                self._send_json(500, {"ok": False, "action": "run-tests", "message": msg})
                return
        ok, msg = self._run_script(self.build_script)
        self._send_json(
            200 if ok else 500,
            {"ok": ok, "action": "run-tests", "message": msg or "Testes simulados e hub atualizado"},
        )


def main() -> int:
    p = argparse.ArgumentParser(description="Servidor Project Hub")
    p.add_argument("--repo-root", type=Path, required=True)
    p.add_argument("--serve-dir", type=Path, required=True)
    p.add_argument("--port", type=int, default=8090)
    p.add_argument("--build-script", type=Path)
    p.add_argument("--run-script", type=Path)
    args = p.parse_args()

    repo = args.repo_root.resolve()
    serve = args.serve_dir.resolve()
    if not serve.is_dir():
        print(f"ERRO: serve-dir ausente: {serve}", file=sys.stderr)
        return 1

    handler = ProjectHubHandler
    handler.repo_root = repo
    handler.build_script = args.build_script.resolve() if args.build_script else None
    handler.run_script = args.run_script.resolve() if args.run_script else None

    class RootedHandler(ProjectHubHandler):
        def __init__(self, *a, **kw):
            super().__init__(*a, directory=str(serve), **kw)

    httpd = ThreadingHTTPServer(("", args.port), RootedHandler)
    print(f"Project Hub: http://localhost:{args.port}/project-hub/")
    print(f"API:         POST /api/refresh · POST /api/run-tests")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nEncerrado.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
