---
id: "0002"
title: "The inference library is optional"
status: "In Progress"
priority: "High"
created: "2026-10-27"
last_updated: "2026-10-27"
related_tenets:
- "models-ignorant-of-ui"
stakeholders:
- "Neil Lawrence"
- "GPy maintainers"
tags:
- visualization
- packaging
---

# REQ-0002: The inference library is optional

## Description

Installing vidden does not install GPy. Geometry and the explorer talk
to a duck-typed model. GPy is an extra for demos that load OSU stick,
oil, or faces.

**Why this matters**: Visualisation that lives inside GPy cannot be
shared with other latent models, and GPy should not grow Panel as a
core dependency.

**Who benefits**: GPy (smaller plotting surface), other latent-model
code (doodle space, future libraries).

## Acceptance Criteria

- [ ] `pip install vidden` does not require GPy
- [ ] Explorer tests that need a GPLVM skip when GPy is absent
- [ ] Stick-man data loading is behind `vidden[gpy]`

## References

- Related tenet: models-ignorant-of-ui

## Progress Updates

### 2026-10-27

Requirement created with the package skeleton.
