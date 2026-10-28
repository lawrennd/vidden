---
id: "2026-10-28_doodle-correspondence-view"
title: "Panel correspondence view for aligned doodles"
status: "In Progress"
priority: "High"
created: "2026-10-28"
last_updated: "2026-10-28"
category: "features"
related_cips: ["0008"]
owner: "Neil Lawrence"
dependencies: ["2026-10-28_port-doodle-align-store"]
tags:
- backlog
- doodle
---

# Task: Panel correspondence view for aligned doodles

## Description

Colour-matched alignment check. Same colour = same template slot; grey
= dropped extra. Optional packed row. Uses `align_doodles` only.

## Acceptance Criteria

- [x] Extra strokes are grey
- [x] `doodle_align` builds without serving
- [x] `examples/doodle_align.py` is the servable entry

## Related

- CIP: 0008

## Progress Updates

### 2026-10-28

Task created with `vidden.host.correspondence`.
