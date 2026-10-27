---
id: "browser-pointer-not-gui-backend"
title: "Browser pointer, not a GUI backend"
status: "Active"
created: "2026-10-27"
last_reviewed: "2026-10-27"
review_frequency: "Annual"
conflicts_with: []
tags:
- tenet
- plotting
---

# Project Tenet: Browser Pointer, Not a GUI Backend

## Description

Latent exploration is a pointer stream plus `predict`. It is not a
matplotlib GUI-backend problem. macOS Cocoa, Jupyter inline, and nested
`canvas.draw()` all failed for that reason. Use the widget toolkit's
documented events. Do not intercept browser gestures the toolkit does
not expose.

## Quote

*"Read the toolkit manual. Do not invent a mouse button."*

## Examples

- Panel + Bokeh `Tap` / `mousemove` replace `mpl_connect`.
- Bokeh `Tap` is left-click only. Right-click is `Plot.context_menu`
  and `MenuItemClick`.
- Click-to-track, as in MATLAB `lvmClassVisualise`, so hovering empty
  latent space does not collapse an untrained GP to the prior mean.

## Counter-examples

- Patching `visualize.py` around `macosx` / `osx` / `input()`.
- `preventDefault` on `contextmenu` to fake a right-button Tap.
- CustomJS `source.stream()` expecting a Python `on_change('data')`.

## Conflicts

- MATLAB used left/right mouse on the ARD histogram.
- Resolution: left-click sets red (y); right-click opens the documented
  dimension menu for green (x); double-click is the one-gesture
  fallback.
