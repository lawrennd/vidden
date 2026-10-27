---
id: "0005"
title: "Users can explore a tree of latent spaces"
status: "In Progress"
priority: "High"
created: "2026-10-27"
last_updated: "2026-10-27"
related_tenets:
- "visualise-then-modify"
- "models-ignorant-of-ui"
- "browser-pointer-not-gui-backend"
stakeholders:
- "Neil Lawrence"
tags:
- visualization
- hgplvm
- hierarchical
---

# REQ-0005: Users can explore a tree of latent spaces

## Description

A hierarchical latent-variable model is several 2-D spaces, not one.
Clicking in a parent writes the children's coordinates; only the leaves
reconstruct pose. The user sees that cascade in the browser.

**Why this matters**: Stick, doodle, oil, and faces are one plane plus
one `Y`. Lawrence and Moore's HGPLVM is a tree. A dropdown of nodes on
`latent_explorer` would hide the structure.

**Who benefits**: Anyone teaching or inspecting a hierarchical GP-LVM
without MATLAB.

## Acceptance Criteria

- [x] A parent click updates descendant latent positions and leaf poses
- [x] Leaves share one reconstruction pane (composite sub-skeletons)
- [x] The tree host is not `latent_explorer` with extra widgets
- [x] The model is duck-typed (`predict`, children); GPy need not ship HGPLVM

## Notes

Dynamics (run / time slider) can wait. First close is click in the
tree and see the skeleton.

## References

- Related tenets: visualise-then-modify, models-ignorant-of-ui,
  browser-pointer-not-gui-backend
- Lawrence and Moore, ICML 2007
