---
id: 2026-10-27_image-view
title: ImageView Visualise/Modify for a reshaped greyscale face
status: Completed
priority: High
created: "2026-10-27"
last_updated: "2026-10-27"
category: features
related_cips:
- "0005"
owner: Neil Lawrence
dependencies:
- 2026-10-27_oil-explorer-demo
tags:
- backlog
- visualization
- faces
---

# Task: ImageView

> Backlog task for [CIP-0005](../../cip/cip0005.md). After CIP-0004 oil.

## Description

Bokeh greyscale image from a packed `Y` row. Match GPy `image_show`
flags: `dimensions`, `transpose`, `order` (`C`/`F`), `invert`. Init
freezes the pixel box. `modify` only writes image data.

## Acceptance Criteria

- [x] Reshape tests cover C vs F and transpose without GPy
- [x] `modify` does not change axis ranges
- [x] Creating the view does not call `servable()`

## Related

- CIP: 0005
- Depends: 2026-10-27_oil-explorer-demo (oil then faces)

## Progress Updates

### 2026-10-27

Task created when CIP-0005 was Accepted. Starts after the oil demo.

### 2026-10-27

`ImageView` and `reshape_image` in `src/vidden/views/image.py`. Tests
in `tests/test_image.py`.
