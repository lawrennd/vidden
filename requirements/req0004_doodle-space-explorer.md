---
id: "0004"
title: "A doodle family can be explored in the same latent viewer as the stick man"
status: "Implemented"
priority: "High"
created: "2026-10-27"
last_updated: "2026-10-27"
related_tenets:
- "visualise-then-modify"
- "browser-pointer-not-gui-backend"
- "models-ignorant-of-ui"
stakeholders:
- "Neil Lawrence"
tags:
- visualization
- doodle
- gplvm
---

# REQ-0004: A doodle family can be explored in the same latent viewer as the stick man

## Description

Given a packed family of line drawings and a fitted latent model, a user
can move in the latent plane and see a synthesized doodle, with the same
click-to-track and axis-select behaviour as the stick man.

**Why this matters**: Baxter and Anjyo's *Latent Doodle Space* is the
teaching example of a GPLVM on huge feature vectors and few examples.
A static interpolation grid does not show the latent space. The live
explorer does.

**Who benefits**: Teaching (GP Summer School unsupervised GPs), and
anyone with a family of aligned doodles (faces, bugs, …).

## Acceptance Criteria

- [x] A doodle reconstruction updates from `model.predict` on pointer
      motion after a click
- [x] Training doodles appear as points on the latent scatter
- [x] Missing strokes (NaN in the packed vector) stay missing in the
      drawing
- [x] The same host runs in Jupyter and as `panel serve`
- [x] No matplotlib GUI backend is required for exploration

## Notes

Correspondence and the drawing studio are how we *build* a family
(REQ-0006). This requirement is how we *present* one.

## References

- Baxter & Anjyo, *Latent Doodle Space*, Eurographics 2006
- GPy branch `notebook-latent-doodle-space`
