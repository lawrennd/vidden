---
id: 2026-10-27_hierarchical-host-layout
title: Tree host layout of node scatters plus composite StickView
status: Completed
priority: High
created: "2026-10-27"
last_updated: "2026-10-27"
category: features
related_cips:
- "0006"
owner: Neil Lawrence
dependencies:
- 2026-10-27_hierarchical-tree-cascade
tags:
- backlog
- visualization
- hgplvm
---

# Task: Tree host layout

> Backlog task for [CIP-0006](../../cip/cip0006.md).

## Description

`vidden.host.tree.tree_explorer`: Panel grid of 2-D node scatters
(density + points + red cross, click-to-track) and one composite
`StickView`. Not a second `latent_explorer`. No ARD bars. No dynamics.

## Acceptance Criteria

- [x] Layout construction `importorskip`s Panel
- [x] Creating the host does not call `servable()`
- [x] Leaves share one `StickView`

## Related

- CIP: 0006

## Progress Updates

### 2026-10-27

Task created when CIP-0006 was Accepted.

### 2026-10-27

`vidden.host.tree.tree_explorer`.
