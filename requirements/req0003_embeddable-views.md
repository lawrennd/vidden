---
id: "0003"
title: "Reconstruction views are embeddable panes, not a single app"
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
- hosting
---

# REQ-0003: Reconstruction views are embeddable panes, not a single app

## Description

A stick, image, or curve view can be placed in more than one host: a
Panel layout today, a Jupyter cell, and later a slot in another web
page. `panel serve` is one way to show an explorer, not the definition
of a view.

**Why this matters**: The MATLAB split was Visualise (create artists)
then Modify (write data). Binding that to one server command repeats
the GPy mistake of tying the view to a particular GUI.

**Who benefits**: The stick explorer now; oil/faces next; a future
Referia or notebook host that only needs a pane.

## Acceptance Criteria

- [x] Creating a stick view does not start a Panel server
- [x] The explorer layout is a return value (a pane), not a process
- [x] A host can hold the view and call modify on new `Y` rows
- [x] vidden does not import referia

## Notes

Referia integration is later. Referia's web UI is FastAPI + HTMX, not
HoloViz Panel; its Jupyter path is ipywidgets. Designing views as panes
is what keeps that door open.

## References

- Related tenets: visualise-then-modify, models-ignorant-of-ui,
  browser-pointer-not-gui-backend
