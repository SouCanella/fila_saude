#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
CONFIG="${ROOT}/project.config.yaml"
ERR=0

fail() { echo "ERRO: $1"; ERR=1; }

if [[ ! -f "$CONFIG" ]]; then
  fail "project.config.yaml não encontrado"
  exit 1
fi

for section in discovery mvp_planning bootstrap project design coverage i18n e2e ci openapi tracking process_metrics quality_health project_hub git agent_automation; do
  if ! grep -q "^${section}:" "$CONFIG"; then
    fail "seção ausente: ${section}"
  fi
done

if ! grep -q "sections:" "$CONFIG"; then
  fail "bootstrap.sections ausente"
fi

for key in A_identidade B_stack C_infra D_testes E_ci F_contratos G_observabilidade \
           H_design I_seguranca J_rastreio K_i18n L_e2e M_ambientes N_privacidade O_entrega; do
  if ! grep -q "${key}:" "$CONFIG"; then
    fail "bootstrap.sections.${key} ausente"
  fi
done

if ! grep -q "^agent_automation:" "$CONFIG"; then
  fail "seção agent_automation ausente"
fi

BOOT_STATUS=$(grep -A1 "^bootstrap:" "$CONFIG" | grep "status:" | head -1 | awk '{print $2}' || true)
if [[ -z "$BOOT_STATUS" ]]; then
  fail "bootstrap.status ausente"
fi

DISC_STATUS=$(grep -A5 "^discovery:" "$CONFIG" | grep "status:" | head -1 | awk '{print $2}' || true)
MVP_STATUS=$(grep -A5 "^mvp_planning:" "$CONFIG" | grep "status:" | head -1 | awk '{print $2}' || true)
if [[ -z "$DISC_STATUS" ]]; then
  fail "discovery.status ausente"
fi
if [[ -z "$MVP_STATUS" ]]; then
  fail "mvp_planning.status ausente"
fi

if [[ "$DISC_STATUS" == "pending" ]]; then
  echo "AVISO: discovery.status pending — iniciar fase 0 (docs/DISCOVERY.md)"
fi
if [[ "$MVP_STATUS" == "pending" ]]; then
  echo "AVISO: mvp_planning.status pending — após bootstrap (+ design se front)"
fi

PM_ENABLED=$(grep -A8 "^process_metrics:" "$CONFIG" | grep "enabled:" | head -1 | awk '{print $2}' || true)
if [[ "$PM_ENABLED" == "true" ]]; then
  if [[ ! -f "${ROOT}/docs/meta/process-timeline.yaml" ]]; then
    fail "process_metrics.enabled mas docs/meta/process-timeline.yaml ausente"
  fi
fi

if [[ "$BOOT_STATUS" == "incomplete" ]]; then
  echo "AVISO: bootstrap.status ainda incomplete (OK para template Modelo)"
fi

if ! grep -q "^  cards:" "$CONFIG"; then
  fail "tracking.cards ausente"
fi

if ! grep -A20 "^  cards:" "$CONFIG" | grep -q "required: true"; then
  fail "tracking.cards.required deve ser true"
fi

CARDS_PROVIDER=$(grep -A5 "^  cards:" "$CONFIG" | grep "provider:" | head -1 | awk '{print $2}' || true)
if [[ -z "$CARDS_PROVIDER" ]]; then
  fail "tracking.cards.provider ausente"
fi

if ! grep -A5 "^  cards:" "$CONFIG" | grep -q "mirror_in_repo: true"; then
  fail "tracking.cards.mirror_in_repo deve ser true"
fi

if [[ $ERR -eq 1 ]]; then
  exit 1
fi

echo "OK: project.config.yaml estrutura válida (discovery=${DISC_STATUS}, mvp_planning=${MVP_STATUS}, bootstrap=${BOOT_STATUS}, cards.provider=${CARDS_PROVIDER})"
