# Gerado no bootstrap — ajustar paths conforme stack
name: CI

on:
  push:
    branches: [main, develop]
  pull_request:

jobs:
  quality:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - name: Install Python deps
        run: pip install pyyaml
      - name: OpenAPI validate
        run: |
          chmod +x scripts/validate-openapi.sh
          ./scripts/validate-openapi.sh || true
      - name: Build Project Hub
        run: |
          chmod +x scripts/build-project-hub.sh scripts/build-hub-embeds.sh
          make hub-build
      - name: Hub journey tests
        run: python3 scripts/test_build_project_journey.py -v && python3 scripts/test_resolve_next_step_retro.py -v
      - name: Lint
        run: echo "Configure lint no bootstrap"
      - name: Unit tests
        run: echo "Configure unit tests"
      - name: Coverage
        run: echo "Threshold {{COVERAGE_THRESHOLD}}%"
      - name: OpenAPI validate
        run: echo "Validate {{OPENAPI_PATH}}"
      - name: Integration tests
        run: echo "Configure API integration tests"
      - name: Security scan
        run: echo "Configure SAST/deps/secrets"
      - name: Export quality run
        if: always()
        run: |
          chmod +x scripts/export-quality-run.sh
          ./scripts/export-quality-run.sh \
            --junit-unit-back "${JUNIT_UNIT_BACK:-}" \
            --junit-unit-front "${JUNIT_UNIT_FRONT:-}" \
            --junit-integration "${JUNIT_INTEGRATION:-}" \
            --junit-contract "${JUNIT_CONTRACT:-}" \
            --junit-e2e "${JUNIT_E2E:-}" \
            --coverage-backend "${COVERAGE_BACKEND:-}" \
            --coverage-frontend "${COVERAGE_FRONTEND:-}" \
            --commit "${{ github.sha }}" \
            --ci-job "github-actions" || true
      - name: Build quality health dashboard
        run: ./scripts/build-quality-health.sh || true
      - name: Build Project Hub (quality + overview)
        if: always()
        run: |
          chmod +x scripts/build-project-hub.sh
          ./scripts/build-project-hub.sh
      - name: Validate quality spec plans
        run: ./scripts/validate-quality-spec-plans.sh || true
      # Release (bloco O bootstrap): descomente se git.release.ci_automation == github_release
      # - name: Release
      #   if: github.ref == 'refs/heads/main'
      #   run: echo "Configure release workflow — ver docs/operations/release-policy.md"
