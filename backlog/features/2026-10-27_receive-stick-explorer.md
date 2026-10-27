---
id: 2026-10-27_receive-stick-explorer
title: Receive GPy stick explorer into vidden.explore
status: Completed
priority: High
created: "2026-10-27"
last_updated: "2026-10-27"
category: features
related_cips:
- "0001"
owner: Neil Lawrence
dependencies: []
tags:
- backlog
- visualization
- panel
---

# Task: Receive the GPy stick explorer

> Backlog task for [CIP-0001](../../cip/cip0001.md).

## Description

Move `GPy/examples/stick_explorer_spike.py` to `vidden.explore`. Duck-type
the model. Serve from `examples/stick.py`, not from library import.
Move tests to `tests/test_explore.py`.

## Acceptance Criteria

- [x] `from vidden.explore import stick_explorer` works
- [x] `panel serve examples/stick.py --show` is the documented entry
- [x] Importing `vidden.explore` does not call `servable()`
- [x] Pytest geometry tests pass without GPy
- [x] GPLVM tests skip if GPy is missing

## Implementation Notes

Do not import `VariationalPosterior`. Use `X.mean` only when it is an
array. Bokeh right-click remains `context_menu` + `MenuItemClick`.

## Related

- CIP: 0001
- Source: GPy CIP-000B spike

## Progress Updates

### 2026-10-27

Task created with CIP-0001. Transfer starts immediately.

Explorer lives in `vidden.explore`. 29 tests passed, including duck-typed
models that do not import GPy.
