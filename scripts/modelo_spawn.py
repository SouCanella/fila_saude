#!/usr/bin/env python3
"""Spawn de produto: pasta irmã obrigatória ao lado do Modelo upstream."""
from __future__ import annotations

import argparse
import fnmatch
import json
import re
import shutil
import sys
import unicodedata
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TEMPLATE_PRODUCT = ROOT / "templates/new-project/template-product.yaml"

# Pastas/arquivos exclusivos do upstream Modelo — não copiar no spawn de produto.
SPAWN_TOP_LEVEL_EXCLUDES = frozenset(
    {
        ".git",
        ".github",
        ".modelo-upstream",
        "exports",
        "examples",
        "node_modules",
        "FilaSaude-Project-Hub-monitoria-premium-mockups",
    }
)
SPAWN_PATH_SEGMENT_EXCLUDES = frozenset({"__pycache__", ".pytest_cache"})
SPAWN_FILE_EXCLUDES = frozenset({"EVOLUCAO-MODELO.md"})
SPAWN_GLOB_EXCLUDES = ("*.pyc",)

# Caminhos exatos ou glob (relativos à raiz) — demos, testes CI do upstream, meta do template.
SPAWN_REL_PATH_EXCLUDES = frozenset(
    {
        "docs/meta/improving-the-template.md",
    }
)
SPAWN_REL_GLOB_PATTERNS = (
    "scripts/*demo*",
    "scripts/test_spawn_e2e.sh",
    "scripts/test_modelo_spawn.py",
    "scripts/test_resolve_next_step_spawn.py",
    "scripts/test_init_new_project_guard.sh",
    "scripts/validate-template.sh",
    "scripts/create-project-from-modelo.sh",
    "docs/meta/process-benchmarks/snapshots/benchmark-*.json",
)
# Pastas upstream removidas no prune (nunca .git — repo do produto)
SPAWN_PRUNE_DIRS = frozenset(
    {
        ".github",
        ".modelo-upstream",
        "examples",
        "exports",
        "FilaSaude-Project-Hub-monitoria-premium-mockups",
    }
)


def load_yaml(path: Path) -> dict:
    if not path.exists():
        return {}
    try:
        import yaml  # type: ignore
    except ImportError:
        print("ERRO: PyYAML necessário", file=sys.stderr)
        sys.exit(1)
    with path.open(encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}
    return data if isinstance(data, dict) else {}


def slugify(name: str) -> str:
    text = unicodedata.normalize("NFKD", name)
    text = text.encode("ascii", "ignore").decode("ascii")
    text = re.sub(r"[^\w\s-]", "", text).strip().lower()
    text = re.sub(r"[-\s]+", "-", text)
    return text or "novo-projeto"


def is_upstream_root(root: Path) -> bool:
    root = root.resolve()
    cfg = load_yaml(root / "project.config.yaml")
    template = cfg.get("template") or {}
    if template.get("is_upstream") is True:
        return True
    return (root / ".modelo-upstream").is_file()


def is_product_root(root: Path) -> bool:
    root = root.resolve()
    if (root / ".modelo-product-workspace").is_file():
        return True
    cfg = load_yaml(root / "project.config.yaml")
    return (cfg.get("template") or {}).get("is_upstream") is False


def resolve_sibling_dest(modelo_root: Path, folder_name: str) -> Path:
    if not folder_name or "/" in folder_name or "\\" in folder_name or folder_name in (".", ".."):
        raise ValueError("nome de pasta inválido (use apenas o nome da pasta irmã, sem /)")
    modelo_root = modelo_root.resolve()
    parent = modelo_root.parent
    dest = (parent / folder_name).resolve()

    if dest == modelo_root:
        raise ValueError("destino não pode ser a própria pasta Modelo")
    if dest.parent != parent.resolve():
        raise ValueError("destino deve ser pasta irmã (mesmo diretório pai do Modelo)")
    try:
        dest.relative_to(modelo_root)
        raise ValueError("destino não pode ficar dentro da pasta Modelo")
    except ValueError as exc:
        if "destino não pode" in str(exc):
            raise
    return dest


def build_product_template_block(product_name: str, upstream_root: Path) -> str:
    """Gera bloco template canônico de produto (substitui seção inteira no config)."""
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    upstream_name = upstream_root.resolve().name
    upstream_path = str(upstream_root.resolve())

    if TEMPLATE_PRODUCT.is_file():
        raw = TEMPLATE_PRODUCT.read_text(encoding="utf-8")
        lines = [ln for ln in raw.splitlines() if ln.strip() and not ln.strip().startswith("#")]
        block = "\n".join(lines) + "\n"
    else:
        block = (
            "template:\n"
            "  is_upstream: false\n"
            "  sibling_spawn_required: false\n"
            "  upstream_dev_mode: false\n"
            "  spawned_from: null\n"
            "  spawned_at: null\n"
            "  upstream_path: null\n"
        )

    block = block.replace("spawned_from: null", f"spawned_from: {upstream_name}")
    block = block.replace('spawned_at: null', f'spawned_at: "{now}"')
    block = block.replace('upstream_path: null', f'upstream_path: "{upstream_path}"')
    return block


def _replace_yaml_section(text: str, section: str, new_body: str) -> str:
    """Substitui seção de primeiro nível (ex.: template:) preservando o resto."""
    pattern = rf"^{re.escape(section)}:\n(?:  .*\n)*"
    if re.search(pattern, text, re.M):
        return re.sub(pattern, new_body, text, count=1, flags=re.M)
    return new_body + "\n" + text


def patch_product_config(dest: Path, product_name: str, upstream_root: Path) -> None:
    cfg_path = dest / "project.config.yaml"
    if not cfg_path.exists():
        raise FileNotFoundError(f"project.config.yaml ausente em {dest}")

    text = cfg_path.read_text(encoding="utf-8")
    template_block = build_product_template_block(product_name, upstream_root)
    text = _replace_yaml_section(text, "template", template_block)

    quoted_name = json.dumps(product_name, ensure_ascii=False)
    if re.search(r"^  name:", text, re.M):
        text = re.sub(r"^  name:.*$", f"  name: {quoted_name}", text, count=1, flags=re.M)
    else:
        text = re.sub(r"(^project:\s*\n)", rf"\1  name: {quoted_name}\n", text, count=1, flags=re.M)

    cfg_path.write_text(text, encoding="utf-8")


def _matches_spawn_rel_pattern(rel_posix: str) -> bool:
    if rel_posix in SPAWN_REL_PATH_EXCLUDES:
        return True
    return any(fnmatch.fnmatch(rel_posix, pattern) for pattern in SPAWN_REL_GLOB_PATTERNS)


def should_exclude_spawn_relpath(rel: Path) -> bool:
    """True se o caminho relativo não deve ir para a pasta irmã do produto."""
    if not rel.parts:
        return False
    if rel.parts[0] in SPAWN_TOP_LEVEL_EXCLUDES:
        return True
    if rel.name in SPAWN_FILE_EXCLUDES:
        return True
    if any(part in SPAWN_PATH_SEGMENT_EXCLUDES for part in rel.parts):
        return True
    rel_posix = rel.as_posix()
    if rel_posix.startswith(".cursor/projects") or "/.cursor/projects/" in f"/{rel_posix}/":
        return True
    if _matches_spawn_rel_pattern(rel_posix):
        return True
    return any(fnmatch.fnmatch(rel.name, pattern) for pattern in SPAWN_GLOB_EXCLUDES)


def get_spawn_rsync_excludes() -> list[str]:
    """Lista de padrões excluídos no spawn (dry-run/documentação)."""
    items = sorted(SPAWN_TOP_LEVEL_EXCLUDES | SPAWN_FILE_EXCLUDES | SPAWN_REL_PATH_EXCLUDES)
    items.extend(sorted(SPAWN_PATH_SEGMENT_EXCLUDES))
    items.extend(SPAWN_REL_GLOB_PATTERNS)
    items.extend(SPAWN_GLOB_EXCLUDES)
    items.append(".cursor/projects")
    return items


def _remove_spawn_path(path: Path, dest: Path, removed: list[str]) -> None:
    if not path.exists():
        return
    rel = path.relative_to(dest).as_posix()
    if path.is_dir():
        shutil.rmtree(path)
        removed.append(f"{rel}/")
    else:
        path.unlink()
        removed.append(rel)


def _spawn_copy_ignore(upstream: Path):
    def ignore(directory: str, names: list[str]) -> set[str]:
        ignored: set[str] = set()
        base = Path(directory)
        for name in names:
            rel = (base / name).relative_to(upstream)
            if should_exclude_spawn_relpath(rel):
                ignored.add(name)
        return ignored

    return ignore


def spawn_copy_upstream(upstream: Path, dest: Path) -> None:
    """Copia upstream → pasta irmã preservando symlinks e excluindo artefatos do Modelo."""
    upstream = upstream.resolve()
    dest = dest.resolve()
    if dest.exists():
        raise FileExistsError(f"destino já existe: {dest}")
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(upstream, dest, ignore=_spawn_copy_ignore(upstream), symlinks=True)


def prune_upstream_artifacts(dest: Path) -> list[str]:
    """Remove resíduos do upstream após cópia manual ou spawn anterior."""
    dest = dest.resolve()
    removed: list[str] = []

    for rel in sorted(SPAWN_FILE_EXCLUDES | SPAWN_REL_PATH_EXCLUDES):
        _remove_spawn_path(dest / rel, dest, removed)

    for rel in sorted(SPAWN_PRUNE_DIRS):
        path = dest / rel
        if path.exists():
            if path.is_dir():
                shutil.rmtree(path)
                removed.append(f"{rel}/")
            else:
                path.unlink()
                removed.append(rel)

    for pattern in SPAWN_REL_GLOB_PATTERNS:
        for path in sorted(dest.glob(pattern)):
            _remove_spawn_path(path, dest, removed)

    # dedupe preservando ordem
    seen: set[str] = set()
    unique: list[str] = []
    for item in removed:
        if item not in seen:
            seen.add(item)
            unique.append(item)
    return unique


def write_product_marker(dest: Path, upstream_root: Path | None = None) -> None:
    src = ROOT / "templates/new-project/modelo-product-workspace"
    if src.is_file():
        (dest / ".modelo-product-workspace").write_text(src.read_text(encoding="utf-8"), encoding="utf-8")
    else:
        (dest / ".modelo-product-workspace").write_text(
            "# workspace de produto (spawn)\n", encoding="utf-8"
        )
    (dest / ".modelo-upstream").unlink(missing_ok=True)


def main() -> int:
    p = argparse.ArgumentParser(description="Valida spawn irmão do Modelo")
    p.add_argument("--root", type=Path, default=ROOT)
    p.add_argument("--name", help="Nome do produto")
    p.add_argument("--dir", help="Nome da pasta irmã (default: slug do nome)")
    p.add_argument("--json", action="store_true")
    p.add_argument("--check-upstream", action="store_true")
    p.add_argument("--list-excludes", action="store_true", help="Lista padrões excluídos no spawn")
    p.add_argument("--copy-to", type=Path, help="Copia upstream (--root) para destino irmão")
    p.add_argument("--prune", type=Path, help="Remove artefatos upstream-only em DEST")
    args = p.parse_args()

    if args.list_excludes:
        for item in get_spawn_rsync_excludes():
            print(item)
        return 0

    if args.prune:
        removed = prune_upstream_artifacts(args.prune.resolve())
        for item in removed:
            print(f"OK: removido {item}")
        if not removed:
            print("OK: nada a remover")
        return 0

    if args.copy_to:
        upstream = args.root.resolve()
        if not is_upstream_root(upstream):
            print("ERRO: --copy-to exige pasta Modelo upstream", file=sys.stderr)
            return 2
        try:
            spawn_copy_upstream(upstream, args.copy_to.resolve())
            prune_upstream_artifacts(args.copy_to.resolve())
        except FileExistsError as exc:
            print(f"ERRO: {exc}", file=sys.stderr)
            return 1
        print(f"OK: copiado {upstream} → {args.copy_to.resolve()}")
        return 0

    if not args.name:
        print("ERRO: informe --name ou use --list-excludes / --copy-to / --prune", file=sys.stderr)
        return 1

    root = args.root.resolve()
    folder = args.dir or slugify(args.name)

    if args.check_upstream and not is_upstream_root(root):
        print("ERRO: não é pasta Modelo upstream (template.is_upstream ou .modelo-upstream)", file=sys.stderr)
        return 2

    try:
        dest = resolve_sibling_dest(root, folder)
    except ValueError as e:
        print(f"ERRO: {e}", file=sys.stderr)
        return 1

    out = {
        "upstream_root": str(root),
        "product_name": args.name,
        "folder_name": folder,
        "dest_path": str(dest),
        "parent_dir": str(root.parent),
        "is_upstream": is_upstream_root(root),
    }
    if args.json:
        print(json.dumps(out, ensure_ascii=False, indent=2))
    else:
        print(dest)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
