---
id: "2026-10-28_doodle-user-studio"
title: "Panel doodle studio with grey selection and save/load"
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

# Task: Panel doodle studio with grey selection and save/load

## Description

Browser drawing pad (`FreehandDrawTool`), selected doodle grey below,
Keep / Undo / Clear / Save / Load. JSON via `vidden.doodle.store`.

## Acceptance Criteria

- [x] `doodle_studio` builds without serving
- [x] Keep then Save writes `doodles.json`; Load restores the family
- [x] `examples/doodle_studio.py` is the servable entry

## Related

- CIP: 0008

## Progress Updates

### 2026-10-28

Task created with the Panel host.
