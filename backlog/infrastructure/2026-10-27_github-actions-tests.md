---
id: 2026-10-27_github-actions-tests
title: GitHub Actions tests for vidden
status: Completed
priority: High
created: "2026-10-27"
last_updated: "2026-10-27"
category: infrastructure
related_cips:
- "0001"
owner: Neil Lawrence
dependencies: []
tags:
- backlog
- ci
- github-actions
---

# Task: GitHub Actions tests

> Backlog task for [CIP-0001](../../cip/cip0001.md).

## Description

Run pytest on push and pull request to `main`. Install `[dev,explore]`
so Bokeh view tests run. GPy stays optional: those tests skip when the
inference library is not installed, so CI does not take on GPy's Cython
build.

## Acceptance Criteria

- [x] Workflow file at `.github/workflows/test.yml`
- [x] Python 3.11 and 3.12 on Ubuntu
- [x] README badge points at the workflow

## Related

- CIP: 0001

## Progress Updates

### 2026-10-27

Workflow added. GPy extra left out of CI on purpose.
