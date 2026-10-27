---
id: 2026-10-27_split-views-from-panel-host
title: Split StickView from the Panel host
status: Completed
priority: High
created: "2026-10-27"
last_updated: "2026-10-27"
category: features
related_cips:
- "0002"
owner: Neil Lawrence
dependencies: []
tags:
- backlog
- visualization
- panel
---

# Task: Split views from the Panel host

> Backlog task for [CIP-0002](../../cip/cip0002.md).

## Description

Move `StickView` to `vidden.views.stick` and `stick_explorer` to
`vidden.host.panel`. Keep `vidden.explore` as compatibility re-exports.
`examples/stick.py` is the only `servable()` call.

## Acceptance Criteria

- [x] `from vidden.views import StickView`
- [x] `from vidden.host.panel import stick_explorer`
- [x] `vidden.explore.stick_explorer` is the same function
- [x] Importing views does not call `servable()`

## Related

- CIP: 0002

## Progress Updates

### 2026-10-27

Split done with CIP-0002 Accepted.
