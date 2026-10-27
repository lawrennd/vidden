---
id: 2026-10-27_brendan-faces-demo
title: Brendan faces explorer demo on ImageView
status: Ready
priority: High
created: "2026-10-27"
last_updated: "2026-10-27"
category: features
related_cips:
- "0005"
owner: Neil Lawrence
dependencies:
- 2026-10-27_image-view
tags:
- backlog
- visualization
- faces
---

# Task: Brendan faces explorer demo

> Backlog task for [CIP-0005](../../cip/cip0005.md).

## Description

`face_explorer` plus `examples/faces.py` on Brendan faces:
`dimensions=(20, 28)`, `transpose=True`, `order='F'`, 2-D Bayesian
GPLVM with inducing points as in GPy `brendan_faces`. Do not inflate
Q. Olivetti is the same view, optional later.

## Acceptance Criteria

- [ ] `panel serve examples/faces.py --show` is the documented entry
- [ ] `face_explorer` uses `latent_explorer` and `ImageView`
- [ ] Explorer construction test `importorskip`s GPy / Panel / pods
- [ ] Reshape matches GPy Brendan flags so the face is upright

## Related

- CIP: 0005
- Depends: 2026-10-27_image-view

## Progress Updates

### 2026-10-27

Task created when CIP-0005 was Accepted.
