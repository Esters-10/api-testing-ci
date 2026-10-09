# api-testing-ci

[![API Tests](https://github.com/tomiwaadisa/api-testing-ci/actions/workflows/api-tests.yml/badge.svg)](https://github.com/tomiwaadisa/api-testing-ci/actions/workflows/api-tests.yml)

This repository runs API checks against the GoRest public API using GitHub Actions.

## CI workflow

The workflow triggers on:
- push to main
- pull requests
- a scheduled daily run
- manual dispatch

It includes:
- a smoke-test job for fast PR feedback
- a full regression job for scheduled/manual runs
- a fail-fast check that ensures `GOREST_TOKEN` is configured
- test report uploads for both jobs

## Required secret

Create a GitHub repository secret named `GOREST_TOKEN` with a valid API token before running the workflow.

## Local checks

```bash
pip install -r requirements.txt
GOREST_TOKEN=your_token_here pytest -q
```
