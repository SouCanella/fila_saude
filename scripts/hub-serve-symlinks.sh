#!/usr/bin/env bash
# Symlinks na raiz do projeto para servir Project Hub + painéis legados + mocks HTML.
set -euo pipefail
ROOT="${1:?usage: hub-serve-symlinks.sh REPO_ROOT}"
for leg in project-hub process-metrics quality-health; do
  target="${ROOT}/${leg}"
  if [[ -e "$target" && ! -L "$target" ]]; then
    rm -rf "$target"
  fi
  ln -sfn "docs/meta/${leg}" "$target"
done
