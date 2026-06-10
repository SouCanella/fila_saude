#!/usr/bin/env python3
"""Embute JSON do protótipo para fetch offline (file://)."""
from __future__ import annotations

import json
import sys
from pathlib import Path


def collect_json(root: Path) -> dict[str, object]:
    store: dict[str, object] = {}
    hub_data = root / "project-hub" / "data"
    for p in sorted(hub_data.glob("*.json")):
        store[p.name] = json.loads(p.read_text(encoding="utf-8"))
    for sub, name in [
        ("process-metrics", "process-metrics.data.json"),
        ("quality-health", "quality-health.data.json"),
    ]:
        p = root / sub / name
        if p.exists():
            store[f"{sub}/{name}"] = json.loads(p.read_text(encoding="utf-8"))
    return store


def main() -> None:
    root = Path(sys.argv[1]).resolve()
    store = collect_json(root)
    bundle = root / "project-hub" / "shared" / "embed.bundle.js"
    bundle.write_text(
        "window.__HUB_EMBED__ = "
        + json.dumps(store, ensure_ascii=False)
        + ";\n",
        encoding="utf-8",
    )
    shim = root / "project-hub" / "shared" / "offline-fetch.js"
    shim.write_text(
        """/* Intercepta fetch de *.json para protótipo offline */
(function () {
  const data = window.__HUB_EMBED__ || {};
  const orig = window.fetch.bind(window);
  function resolveKey(url) {
    const u = String(url).split("?")[0];
    const name = u.split("/").pop();
    if (data[name]) return name;
    if (u.includes("process-metrics") && data["process-metrics/process-metrics.data.json"])
      return "process-metrics/process-metrics.data.json";
    if (u.includes("quality-health") && data["quality-health/quality-health.data.json"])
      return "quality-health/quality-health.data.json";
    return null;
  }
  window.fetch = function (input, init) {
    const url = typeof input === "string" ? input : input.url;
    const key = resolveKey(url);
    if (key) {
      return Promise.resolve({
        ok: true,
        status: 200,
        json: () => Promise.resolve(data[key]),
        text: () => Promise.resolve(JSON.stringify(data[key])),
      });
    }
    return orig(input, init);
  };
})();
""",
        encoding="utf-8",
    )
    # Injeta scripts no index.html do hub
    index = root / "project-hub" / "index.html"
    html = index.read_text(encoding="utf-8")
    inject = (
        '  <script src="shared/embed.bundle.js"></script>\n'
        '  <script src="shared/offline-fetch.js"></script>\n'
    )
    if "embed.bundle.js" not in html:
        html = html.replace("<script src=\"shared/theme-init.js\"></script>", inject + '  <script src="shared/theme-init.js"></script>')
        index.write_text(html, encoding="utf-8")
    # Process + quality embeds
    for sub in ("process-metrics", "quality-health"):
        idx = root / sub / "index.html"
        if not idx.exists():
            continue
        h = idx.read_text(encoding="utf-8")
        rel = "../project-hub/shared/"
        inj = (
            f'  <script src="{rel}embed.bundle.js"></script>\n'
            f'  <script src="{rel}offline-fetch.js"></script>\n'
        )
        if "embed.bundle.js" not in h:
            marker = "<script"
            pos = h.find(marker)
            if pos >= 0:
                h = h[:pos] + inj + h[pos:]
                idx.write_text(h, encoding="utf-8")
    print(f"OK: embed {len(store)} JSON → {bundle.relative_to(root)}")


if __name__ == "__main__":
    main()
