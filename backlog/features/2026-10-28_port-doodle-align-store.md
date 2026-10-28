---
id: "2026-10-28_port-doodle-align-store"
title: "Port doodle correspondence and JSON store from GPy"
status: "In Progress"
priority: "High"
created: "2026-10-28"
last_updated: "2026-10-28"
category: "features"
related_cips: ["0008"]
owner: "Neil Lawrence"
dependencies: []
tags:
- backlog
- doodle
---

# Task: Port doodle correspondence and JSON store from GPy

## Description

Move Hungarian matching and JSON family I/O into `vidden.doodle.align`
and `vidden.doodle.store`. No Panel, no matplotlib.

## Acceptance Criteria

- [x] `align_doodles` recovers scrambled stroke order and packs NaNs for missing strokes
- [x] JSON roundtrip loads GPy `gpy-doodle-strokes` files
- [x] Save does not shrink a longer library; no PNG rendering

## Related

- CIP: 0008

## Progress Updates

### 2026-10-28

Task created and implemented with GPy unit tests.
