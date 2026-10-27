---
id: 2026-10-27_doodle-view
title: DoodleView Visualise/Modify for packed stroke vectors
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
tags:
- backlog
- visualization
- doodle
---

# Task: DoodleView

> Backlog task for [CIP-0003](../../cip/cip0003.md).

## Description

Bokeh reconstruction view for a packed doodle: stroke specs unpack a
`Y` row into polylines. Init freezes axis limits. `modify` only writes
the ColumnDataSource. NaN strokes are omitted. Closed strokes close.

## Acceptance Criteria

- [x] `modify` does not change axis ranges
- [x] A stroke that is all-NaN (or contains NaN) is not drawn at the origin
- [x] Closed specs repeat the first vertex
- [x] Creating the view does not call `servable()`

## Related

- CIP: 0003
- Depends: 2026-10-27_parameterise-latent-explorer

## Progress Updates

### 2026-10-27

Task created when CIP-0003 was Accepted.

`DoodleView` in `vidden.views.doodle`. Packed `Y` plus `StrokeSpec`s.
