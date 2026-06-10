# Modelo — atalhos para validação e métricas de processo
SHELL := /bin/bash
# CURDIR suporta caminhos com espaços (ex.: ~/Projetos/Meu Produto)
ROOT  := $(CURDIR)
SCR   := $(ROOT)/scripts

# Executa script .sh com path entre aspas (espaços no diretório do projeto)
define RUN_SH
bash "$(SCR)/$(1)"
endef

define RUN_PY
python3 "$(SCR)/$(1)"
endef

.PHONY: help deps validate validate-strict ci ci-check-json ci-check-quality-json ci-check-hub-json \
        init-new-project reset-hub-activity create-project repair-product-config \
        metrics-build metrics-serve metrics-strict \
        metrics-demo-build metrics-demo-serve metrics-demo-validate \
        quality-build quality-serve quality-validate quality-validate-specs \
        quality-scaffold quality-scaffold-dry quality-scaffold-demo \
        quality-demo-build quality-demo-serve quality-demo-validate \
        validate-spawn-context test-api test-api-integration \
        hub-build hub-serve hub-validate hub-demo-build hub-demo-serve hub-demo-validate \
        hub-validate-complete hub-e2e-demo \
        benchmark-export benchmark-index report report-demo validate-phase-retros-strict

.DEFAULT_GOAL := help

help: ## Lista alvos disponíveis
	@grep -E '^[a-zA-Z0-9_.-]+:.*##' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*## "}; {printf "  make %-24s %s\n", $$1, $$2}'

deps: ## Instala PyYAML (build de métricas)
	pip install -r "$(SCR)/requirements-metrics.txt"

init-new-project: ## Após copiar template: zera entregas meta e rebuild hub
	$(call RUN_SH,init-new-project.sh)

reset-hub-activity: ## Zera horas/métricas e atividade recente no hub (timeline, log, quality)
	$(call RUN_SH,reset-hub-activity.sh)

create-project: ## Cria pasta irmã do Modelo (NAME= obrigatório; DIR= opcional; GIT_INIT=1)
	@test -n "$(NAME)" || (echo "ERRO: use make create-project NAME=\"Meu Produto\" [DIR=pasta] [GIT_INIT=1]" >&2; exit 1)
	bash "$(SCR)/create-project-from-modelo.sh" --name "$(NAME)" $(if $(DIR),--dir "$(DIR)",) $(if $(filter 1,$(GIT_INIT)),--git-init,)

repair-product-config: ## Repara cópia manual (NAME= obrigatório) — config produto + marcador
	@test -n "$(NAME)" || (echo "ERRO: use make repair-product-config NAME=\"Meu Produto\"" >&2; exit 1)
	bash "$(SCR)/repair-product-config.sh" --name "$(NAME)"

validate-spawn-context: ## Checa upstream vs produto spawnado (STRICT=1 falha em violação)
	STRICT=$(STRICT) $(call RUN_SH,validate-spawn-context.sh)

validate: ## Smoke: template, HTML, config, traceability, planning, métricas
	chmod +x "$(SCR)"/*.sh
	$(call RUN_SH,validate-template.sh)
	$(call RUN_SH,validate-spawn-context.sh)
	$(call RUN_PY,test_modelo_spawn.py)
	$(call RUN_PY,test_resolve_next_step_spawn.py)
	$(call RUN_SH,test_init_new_project_guard.sh)
	$(call RUN_SH,validate-html-prototype.sh)
	$(call RUN_SH,validate-config.sh)
	$(call RUN_SH,validate-traceability.sh)
	$(call RUN_SH,validate-planning.sh)
	$(call RUN_SH,build-process-metrics.sh)
	$(call RUN_SH,validate-process-metrics.sh)
	$(call RUN_SH,build-process-metrics-demo.sh)
	$(call RUN_SH,validate-process-metrics-demo.sh)
	$(call RUN_SH,validate-phase-retros.sh) || true
	$(call RUN_SH,aggregate-process-benchmarks.sh)
	$(call RUN_SH,build-quality-health.sh)
	$(call RUN_SH,validate-quality-health.sh)
	$(call RUN_SH,validate-quality-spec-plans.sh)
	$(call RUN_SH,build-quality-health-demo.sh)
	$(call RUN_SH,validate-quality-health-demo.sh)
	$(call RUN_SH,build-project-hub.sh)
	$(call RUN_SH,validate-project-hub.sh)
	$(call RUN_SH,build-project-hub-demo.sh)
	$(call RUN_SH,validate-project-hub-demo.sh)

validate-strict: ## validate + métricas em modo STRICT
	$(MAKE) validate
	PROCESS_METRICS_STRICT=1 $(call RUN_SH,validate-process-metrics.sh)

ci-check-json: metrics-build ## Falha se JSON divergir do HEAD (ignora built_at)
	$(call RUN_PY,check_process_metrics_json.py)

ci-check-quality-json: quality-build ## Falha se JSON qualidade divergir do HEAD
	$(call RUN_PY,check_quality_health_json.py)

ci-check-hub-json: hub-build ## Falha se hub JSON divergir do HEAD (12 arquivos)
	HUB_JSON_STRICT=all $(call RUN_PY,check_hub_json.py)

ci: validate-strict ci-check-json ci-check-quality-json ci-check-hub-json ## Pipeline local (≈ GitHub Actions)

metrics-build: ## Gera docs/meta/process-metrics/process-metrics.data.json
	$(call RUN_SH,build-process-metrics.sh)

metrics-serve: hub-serve ## Alias → Project Hub (:8090/project-hub/#process)

metrics-strict: metrics-build ## Validação estrita do JSON (raiz)
	PROCESS_METRICS_STRICT=1 $(call RUN_SH,validate-process-metrics.sh)

metrics-demo-build: ## Build JSON do demo (examples/process-metrics-demo)
	$(call RUN_SH,build-process-metrics-demo.sh)

metrics-demo-serve: metrics-demo-build ## Painel demo http://localhost:8091/process-metrics/
	$(call RUN_SH,serve-process-metrics-demo.sh)

metrics-demo-validate: metrics-demo-build
	$(call RUN_SH,validate-process-metrics-demo.sh)

benchmark-export: metrics-build ## Snapshot em docs/meta/process-benchmarks/snapshots/
	$(call RUN_SH,export-process-benchmark.sh)

benchmark-index: ## Regenera docs/meta/process-benchmarks/index.md
	$(call RUN_SH,aggregate-process-benchmarks.sh)

report: metrics-build ## HTML estático do relatório (raiz)
	$(call RUN_SH,export-process-report.sh)

report-demo: metrics-demo-build ## HTML estático do demo
	$(call RUN_SH,export-process-report.sh) --demo

quality-build: ## Gera docs/meta/quality-health/quality-health.data.json
	$(call RUN_SH,build-quality-health.sh)

quality-serve: hub-serve ## Alias → Project Hub (:8090/project-hub/#quality)

quality-validate:
	$(call RUN_SH,validate-quality-health.sh)

quality-validate-specs: ## Camadas [x] ↔ plano TDD (QUALITY_SPEC_STRICT=1 exige Arquivo teste)
	$(call RUN_SH,validate-quality-spec-plans.sh)

quality-scaffold: ## Stubs TDD a partir das specs (REQ=REQ-001 opcional)
	$(call RUN_SH,scaffold-quality-tests.sh) $(if $(REQ),--req $(REQ),)

quality-scaffold-dry: ## Preview do scaffold
	$(call RUN_SH,scaffold-quality-tests.sh) --dry-run $(if $(REQ),--req $(REQ),)

quality-scaffold-demo: ## Scaffold no demo (faltantes pending com --include-pending)
	$(call RUN_PY,scaffold_quality_tests.py) --root examples/quality-health-demo \
	  --backlog examples/quality-health-demo/backlog/mvp-backlog.md \
	  --specs-dir examples/quality-health-demo/specs --include-pending

quality-demo-build: ## Build demo qualidade (JSON + painel)
	$(call RUN_SH,build-quality-health-demo.sh)

quality-demo-serve: quality-demo-build ## Demo http://localhost:8093/quality-health/
	$(call RUN_SH,serve-quality-health-demo.sh)

quality-demo-validate: quality-demo-build
	$(call RUN_SH,validate-quality-health-demo.sh)

hub-build: ## Gera docs/meta/project-hub/data/*.json
	$(call RUN_SH,build-project-hub.sh)

hub-serve: hub-build ## Project Hub (HUB_PORT=8090 padrão) http://localhost:PORT/project-hub/
	HUB_PORT=$(or $(HUB_PORT),8090) $(call RUN_SH,serve-project-hub.sh)

hub-validate:
	$(call RUN_SH,validate-project-hub.sh)

hub-demo-build:
	$(call RUN_SH,build-project-hub-demo.sh)

hub-demo-serve: hub-demo-build ## Demo http://localhost:8091/project-hub/
	$(call RUN_SH,serve-project-hub-demo.sh)

hub-demo-validate: hub-demo-build
	$(call RUN_SH,validate-project-hub-demo.sh)

hub-validate-complete: hub-build hub-demo-build ## Validação mestre Hub Evolução (HUB_VALIDATE_WAVE=0|1|2|3|all)
	chmod +x "$(SCR)/validate-hub-complete.sh" "$(SCR)/build-hub-embeds.sh" "$(SCR)/check-hub-embeds.sh" "$(SCR)/sync-card-github.sh"
	HUB_VALIDATE_WAVE=$(HUB_VALIDATE_WAVE) $(call RUN_SH,validate-hub-complete.sh)

# PoC: hub-e2e-demo opcional — não roda em CI (Playwright adiado)
hub-e2e-demo: hub-demo-build ## Playwright E2E smoke no demo hub (manual)
	$(call RUN_SH,run-hub-e2e-demo.sh)

validate-phase-retros-strict: ## Retro index sem || true (RETRO_STRICT=1)
	RETRO_STRICT=1 $(call RUN_SH,validate-phase-retros.sh)

test-api: ## Unit tests Go (apps/api)
	cd apps/api && go test ./internal/...

test-api-integration: ## Integration tests (requer docker compose + env)
	cd apps/api && go test -tags=integration ./tests/integration/...
