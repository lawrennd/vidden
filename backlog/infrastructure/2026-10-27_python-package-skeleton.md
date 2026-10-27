---
id: 2026-10-27_python-package-skeleton
title: Python package skeleton for vidden
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
- packaging
---

# Task: Python package skeleton

> Backlog task for [CIP-0001](../../cip/cip0001.md).

## Description

Create a setuptools `src/` package so the explorer has a home that is
not GPy: `pyproject.toml`, LICENSE, README, `src/vidden`.

## Acceptance Criteria

- [x] `pip install -e .` would install the `vidden` package
- [x] Core extra does not require GPy, Panel, or HoloViews
- [x] `explore` and `gpy` extras are declared

## Related

- CIP: 0001

## Progress Updates

### 2026-10-27

Skeleton written. Transfer of explorer code is the next task.
