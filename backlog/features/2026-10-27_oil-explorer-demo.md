---
id: 2026-10-27_oil-explorer-demo
title: Oil-flow explorer demo on VectorView
status: Completed
priority: High
created: "2026-10-27"
last_updated: "2026-10-27"
category: features
related_cips:
- "0004"
owner: Neil Lawrence
dependencies:
- 2026-10-27_vector-view
tags:
- backlog
- visualization
- oil
---

# Task: Oil-flow explorer demo

> Backlog task for [CIP-0004](../../cip/cip0004.md).

## Description

`oil_explorer` plus `examples/oil.py` on `pods.datasets.oil()`, as
`bgplvm_oil`: Bayesian GPLVM, ARD RBF, labels on the latent scatter if
present. Same Optimize then click-to-track story as stick and doodle.

## Acceptance Criteria

- [x] `panel serve examples/oil.py --show` is the documented entry
- [x] `oil_explorer` uses `latent_explorer` and `VectorView`
- [x] Explorer construction test `importorskip`s GPy / Panel / pods

## Related

- CIP: 0004
- Depends: 2026-10-27_vector-view

## Progress Updates

### 2026-10-27

Task created when CIP-0004 was Accepted.

`oil_explorer` plus `examples/oil.py`. Labels colour the scatter.
