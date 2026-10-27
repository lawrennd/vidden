---
id: "visualise-then-modify"
title: "Visualise then modify"
status: "Active"
created: "2026-10-27"
last_reviewed: "2026-10-27"
review_frequency: "Annual"
conflicts_with: []
tags:
- tenet
- plotting
---

# Project Tenet: Visualise Then Modify

## Description

MATLAB `stickVisualise` creates artists and freezes `axis equal`.
`stickModify` only `set`s X/Y/Z on those handles. Live latent
exploration is a data-source write, not a scene rebuild. Axes that
autoscale on every mouse move, or 3-D libraries that restyle a full
figure over a websocket, are the wrong analog.

## Quote

*"Init once. Then only set the data."*

## Examples

- Bokeh `ColumnDataSource.data = ...` is the analog of MATLAB `set`.
- Cubic axis limits come from the Visualise pose and never change.
- The red cross is its own stream. It does not ride a hover tooltip.

## Counter-examples

- GPy `mocap_data_show.modify` deletes and redraws artists, so
  matplotlib autoscales.
- Replacing the stick pane with a Plotly 3-D figure on every pointer
  move.
- HoloViews `framewise=False` freezing ARD bar limits at the PCA peak
  so trained bars vanish.

## Conflicts

- A true 3-D camera can help later skeleton views.
- Resolution: 3-D is a later view, not the live modify path. Project
  with MATLAB's default azimuth/elevation onto a 2-D canvas first.
