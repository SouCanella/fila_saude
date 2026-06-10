# Gerado no bootstrap
stages:
  - lint
  - test
  - security
  - build

variables:
  COVERAGE_THRESHOLD: "{{COVERAGE_THRESHOLD}}"
  OPENAPI_PATH: "{{OPENAPI_PATH}}"

lint:
  stage: lint
  script:
    - echo "Configure lint"

test:unit:
  stage: test
  script:
    - echo "Unit tests + coverage >= ${COVERAGE_THRESHOLD}%"

test:integration:
  stage: test
  script:
    - echo "API integration + contract"

security:
  stage: security
  script:
    - echo "SAST, deps, secrets"

build:
  stage: build
  script:
    - echo "Build"
