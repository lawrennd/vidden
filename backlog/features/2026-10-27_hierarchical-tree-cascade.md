---
id: 2026-10-27_hierarchical-tree-cascade
title: Duck-typed HGPLVM tree and parent-to-leaf cascade
status: Completed
priority: High
created: "2026-10-27"
last_updated: "2026-10-27"
category: features
related_cips:
- "0006"
owner: Neil Lawrence
dependencies: []
tags:
- backlog
- visualization
- hgplvm
---

# Task: Duck-typed tree and cascade

> Backlog task for [CIP-0006](../../cip/cip0006.md).

## Description

Node `predict`, children, optional subskel `connect` / `offset`.
`cascade` matches MATLAB `updateVisualisation`: parent output is
concatenated 2-D child coordinates; leaves return pose.

## Acceptance Criteria

- [x] Parent `(x, y)` writes both child latents and both leaf `Y`s
- [x] Leaf cascade does not touch the sibling
- [x] Tests run without GPy or Panel

## Related

- CIP: 0006

## Progress Updates

### 2026-10-27

Task created when CIP-0006 was Accepted.

### 2026-10-27

`vidden.tree.cascade` and `Mapping` nearest-neighbour nodes. Tests in
`tests/test_tree.py`.
