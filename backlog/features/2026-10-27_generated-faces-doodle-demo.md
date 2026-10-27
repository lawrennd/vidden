---
id: 2026-10-27_generated-faces-doodle-demo
title: Generated-faces doodle explorer demo
status: Completed
priority: High
created: "2026-10-27"
last_updated: "2026-10-27"
category: features
related_cips:
- "0003"
owner: Neil Lawrence
dependencies:
- 2026-10-27_parameterise-latent-explorer
- 2026-10-27_doodle-view
tags:
- backlog
- visualization
- doodle
---

# Task: Generated-faces doodle demo

> Backlog task for [CIP-0003](../../cip/cip0003.md).

## Description

`doodle_explorer` plus `examples/doodle.py` on the smile × roundness
cartoon faces. Known factors so we can tell whether a latent click
moves the mouth and head. Same Optimize then click-to-track story as
the stick demo. Correspondence and user-drawn families are out of
scope.

## Acceptance Criteria

- [x] `panel serve examples/doodle.py --show` is the documented entry
- [x] Default data is generated faces, not `doodles/<family>/`
- [x] `doodle_explorer` uses `latent_explorer` and `DoodleView`
- [x] Explorer construction test `importorskip`s GPy / Panel

## Related

- CIP: 0003

## Progress Updates

### 2026-10-27

Task created when CIP-0003 was Accepted.

`doodle_explorer` plus `examples/doodle.py` on smile × roundness faces.
