---
id: "0006"
title: "Users can draw, save, load, and align a doodle family"
status: "In Progress"
priority: "High"
created: "2026-10-28"
last_updated: "2026-10-28"
related_tenets:
- "browser-pointer-not-gui-backend"
- "models-ignorant-of-ui"
- "visualise-then-modify"
stakeholders:
- "Neil Lawrence"
tags:
- visualization
- doodle
- correspondence
---

# REQ-0006: Users can draw, save, load, and align a doodle family

## Description

A user can collect a family of line drawings in the browser, keep that
family as a dataset on disk, and see how strokes were matched onto a
template so the packed vectors for REQ-0004 are honest.

REQ-0004 is how we *present* a packed family. This requirement is how
we *build* one. The drawings need not already share stroke order,
vertex counts, or stroke counts.

**Why this matters**: Baxter and Anjyo's first component is
correspondence. Without a drawing pad and a matching check, the latent
explorer only ever sees generated faces that already share topology.

**Who benefits**: Teaching (GP Summer School), and anyone who wants a
family of faces, bugs, or other sketches rather than the cartoon grid.

## Acceptance Criteria

- [ ] A user can draw strokes for a new doodle in the browser, without
      a matplotlib GUI backend
- [ ] A selected saved doodle is visible in grey as a reference while
      drawing the next one
- [ ] A family can be saved to disk and loaded again as the same
      stroke lists
- [ ] Stroke correspondence onto a template is available, including
      missing template strokes and dropped extras
- [ ] An advanced view shows that correspondence (same colour = same
      matched stroke; grey = extra)
- [ ] Packed output from alignment can be explored with the existing
      doodle explorer

## Notes

Two presentations of the same family store: a drawing app, and an
alignment check. Referia is not required. GPy
`notebook-latent-doodle-space` already has matplotlib versions of both;
this requirement is that those outcomes live in vidden.

## References

- Baxter & Anjyo, *Latent Doodle Space*, Eurographics 2006
- REQ-0004 (present a packed family)
- GPy branch `notebook-latent-doodle-space`

## Progress Updates

### 2026-10-28
Proposed after CIP-0003 deferred drawing and matching to a later CIP.
