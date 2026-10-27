---
id: 2026-10-27_vector-view
title: VectorView Visualise/Modify for a packed observation vector
status: Ready
priority: High
created: "2026-10-27"
last_updated: "2026-10-27"
category: features
related_cips:
- "0004"
owner: Neil Lawrence
dependencies: []
tags:
- backlog
- visualization
- oil
---

# Task: VectorView

> Backlog task for [CIP-0004](../../cip/cip0004.md).

## Description

Bokeh line: index against value, as GPy `vector_show`. Init freezes
y-limits from the training range. `modify` only writes the
ColumnDataSource. Creating the view does not call `servable()`.

## Acceptance Criteria

- [ ] `modify` does not change axis ranges
- [ ] Line length equals `Y.shape[1]`
- [ ] Creating the view does not call `servable()`

## Related

- CIP: 0004

## Progress Updates

### 2026-10-27

Task created when CIP-0004 was Accepted.
