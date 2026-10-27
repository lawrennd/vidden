---
id: "0001"
title: "Users can explore a latent model in the browser"
status: "In Progress"
priority: "High"
created: "2026-10-27"
last_updated: "2026-10-27"
related_tenets:
- "browser-pointer-not-gui-backend"
- "visualise-then-modify"
stakeholders:
- "Neil Lawrence"
- "GPy users"
tags:
- visualization
- gplvm
---

# REQ-0001: Users can explore a latent model in the browser

## Description

A user with a fitted latent-variable model can move in the latent plane
and see the reconstruction, including choosing which two of Q>2 axes to
plot, without a matplotlib GUI backend.

**Why this matters**: Interactive viewers are how people understand a
GPLVM. That interaction is a pointer plus `predict`, not a desktop
window toolkit.

**Who benefits**: Anyone using GPy (or another GPLVM) on macOS, Jupyter,
or a browser.

## Acceptance Criteria

- [ ] Pointer motion after a click updates the reconstruction
- [ ] Two latent axes are selectable; unused coordinates persist
- [ ] The same app runs in Jupyter and as `panel serve`
- [ ] No matplotlib `macosx` / `osx` backend is required

## Notes

MATLAB `lvmVisualise` starts `latentPos` at zeros and only writes the
two visible dimensions.

## References

- Related tenets: browser-pointer-not-gui-backend, visualise-then-modify
- GPy CIP-000B (deprecated matplotlib visualize; work continues here)

## Progress Updates

### 2026-10-27

Requirement created as vidden received the GPy stick-explorer spike.
