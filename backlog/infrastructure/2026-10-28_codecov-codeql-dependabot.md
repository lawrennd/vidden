---
id: 2026-10-28_codecov-codeql-dependabot
title: Codecov, CodeQL, and Dependabot for vidden
status: Completed
priority: High
created: "2026-10-28"
last_updated: "2026-10-28"
category: infrastructure
related_cips:
- "0007"
owner: Neil Lawrence
dependencies: []
tags:
- backlog
- ci
- codecov
- codeql
- dependabot
---

# Task: Codecov, CodeQL, and Dependabot

> Backlog task for [CIP-0007](../../cip/cip0007.md).

## Description

Add a coverage upload (informational Codecov statuses), a CodeQL
advanced-setup workflow for Python and Actions, and Dependabot for
Actions and pip. Keep the existing pytest matrix unchanged.

## Acceptance Criteria

- [x] Coverage job on Ubuntu 3.12 uploads `coverage.xml`
- [x] `codecov.yml` project/patch statuses are informational
- [x] CodeQL workflow analyses `python` and `actions`
- [x] Dependabot config for `pip` and `github-actions`
- [x] README Codecov badge

## Related

- CIP: 0007

## Progress Updates

### 2026-10-28

Implemented with CIP-0007.
