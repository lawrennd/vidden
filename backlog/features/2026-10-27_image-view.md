---
id: 2026-10-27_image-view
title: ImageView Visualise/Modify for a reshaped greyscale face
status: Ready
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

- [ ] Reshape tests cover C vs F and transpose without GPy
- [ ] `modify` does not change axis ranges
- [ ] Creating the view does not call `servable()`

## Related

- CIP: 0005
- Depends: 2026-10-27_oil-explorer-demo (oil then faces)

## Progress Updates

### 2026-10-27

Task created when CIP-0005 was Accepted. Starts after the oil demo.
