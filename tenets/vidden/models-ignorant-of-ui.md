---
id: "models-ignorant-of-ui"
title: "Models ignorant of the UI"
status: "Active"
created: "2026-10-27"
last_reviewed: "2026-10-27"
review_frequency: "Annual"
conflicts_with: []
tags:
- tenet
- architecture
---

# Project Tenet: Models Ignorant of the UI

## Description

Inference libraries construct a mapping from latent coordinates to
observations. Visualisation consumes that mapping. Neither side should
import the other as a core dependency. GPy, or any other GPLVM, is a
client of vidden, not its host. Duck-type the contract: a writable
latent array, `predict` (or `_raw_predict`), and optional ARD
sensitivities.

## Quote

*"The model predicts. The view only writes data."*

## Examples

- `vidden.explore` talks to `model.X` and `model.predict`. It does not
  import `GPy.models.BayesianGPLVM` except in an optional demo loader.
- GPy keeps static `plot_latent`. Interactive viewers live here.
- A future doodle-space notebook can pass any fitted latent model
  without GPy knowing about Panel.

## Counter-examples

- Putting HoloViews inside GPy's default install.
- Detecting Bayesian GPLVM with `isinstance(X, VariationalPosterior)`
  instead of testing whether `X.mean` is an array.
- Rebuilding a GPy-only matplotlib GUI to "fix" macOS backends.

## Conflicts

- Optional GPy extras make the stick demo easy to run.
- Resolution: keep GPy behind `vidden[gpy]`. Core geometry needs numpy
  only.
