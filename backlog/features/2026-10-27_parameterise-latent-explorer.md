---
id: 2026-10-27_parameterise-latent-explorer
title: Parameterise latent_explorer on a reconstruction view
status: Ready
priority: High
created: "2026-10-27"
last_updated: "2026-10-27"
category: features
related_cips:
- "0003"
owner: Neil Lawrence
dependencies: []
tags:
- backlog
- visualization
- panel
---

# Task: Parameterise the Panel host on a view

> Backlog task for [CIP-0003](../../cip/cip0003.md).

## Description

Extract `latent_explorer(model, view)` from `stick_explorer`. The view
must supply `.fig` and `.modify(y)`. `stick_explorer` becomes a wrapper
that builds `StickView` and calls the host.

## Acceptance Criteria

- [ ] `latent_explorer(model, view)` returns a Panel layout
- [ ] `stick_explorer()` still builds without serving
- [ ] Pointer motion calls `view.modify` with `reconstruct_mean`
- [ ] No second copy of the click-to-track / ARD-bar logic

## Related

- CIP: 0003

## Progress Updates

### 2026-10-27

Task created when CIP-0003 was Accepted.
