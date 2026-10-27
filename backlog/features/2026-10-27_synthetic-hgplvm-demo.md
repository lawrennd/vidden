---
id: 2026-10-27_synthetic-hgplvm-demo
title: Synthetic two-leaf hierarchical explorer demo
status: Completed
priority: High
created: "2026-10-27"
last_updated: "2026-10-27"
category: features
related_cips:
- "0006"
owner: Neil Lawrence
dependencies:
- 2026-10-27_hierarchical-host-layout
tags:
- backlog
- visualization
- hgplvm
---

# Task: Synthetic HGPLVM demo

> Backlog task for [CIP-0006](../../cip/cip0006.md).

## Description

One parent, two 3-joint chain leaves. `examples/tree.py` is the
`servable()` entry. CMU walk is later.

## Acceptance Criteria

- [x] `panel serve examples/tree.py --show` is the documented entry
- [x] Demo does not require a GPy `HGPLVM` class
- [x] Parent click moves both chains

## Related

- CIP: 0006

## Progress Updates

### 2026-10-27

Task created when CIP-0006 was Accepted.

### 2026-10-27

`make_synthetic_hierarchy` and `examples/tree.py`.
