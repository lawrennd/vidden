# vidden

[![Tests](https://github.com/lawrennd/vidden/actions/workflows/test.yml/badge.svg)](https://github.com/lawrennd/vidden/actions/workflows/test.yml)

Latent-space visualisation, independent of the inference library.

`vidden` is the browser explorer that used to live inside
[GPy](https://github.com/SheffieldML/GPy) as
`GPy.plotting.matplot_dep.visualize`. Those matplotlib and VPython
callbacks do not work on current macOS or Jupyter. Here, pointer events
call `model.predict` in Python.

The name is Norwegian *vidden*: the open expanse.

## Install

Python 3.11 or later. From a clone of this repository:

```bash
git clone https://github.com/lawrennd/vidden.git
cd vidden
pip install -e ".[explore,gpy]"
```

`explore` pulls HoloViews, Panel, and Bokeh. `gpy` is only needed for
the stick-man demo (GPy plus [pods](https://github.com/lawrennd/pods)
for the OSU motion data).

## Demo: OSU stick man

From the repository root:

```bash
panel serve examples/stick.py --show
```

This loads `pods.datasets.osu_run1()`, initialises a Bayesian GPLVM
with PCA, and opens a browser. The stick figure is a 2-D projection of
the joints (MATLAB's default camera), not a live 3-D scene.

Or in Jupyter, after the same install:

```python
from vidden.host.panel import stick_explorer

stick_explorer()
```

The last line returns a Panel layout. Leave it as the last expression
in the cell so the notebook displays it.

### What to do in the window

The model starts **untrained**. Empty latent space is prior mean zero,
which collapses the stick. Do not hover around hoping for motion.

1. Click **Optimize Bayesian GPLVM** (5000 BFGS iterations by default).
   Wait until the status line reports a log likelihood.
2. Click the grey latent plot once to start tracking. Move the pointer.
   Click again to freeze.
3. The red cross is the latent position that produced the current stick.
4. Left-click a sensitivity bar to set the **red (y)** axis.
5. Right-click the histogram and pick a dimension for the **green (x)**
   axis. Double-click a bar also sets green.

The latent position starts at zero. A click writes only the two visible
axes. The other coordinates stay where we left them. Switch the bar
axes to set those leftover dimensions.

Dropdowns above the plot select the same two axes if we prefer not to
use the histogram.

## Demo: a tiny GPLVM of our own

The explorer takes any duck-typed model with `X` and `predict` (or
`_raw_predict`). This is enough to see the layout without OSU data:

```python
import numpy as np
import GPy
from vidden.host.panel import stick_explorer

np.random.seed(0)
Y = np.random.randn(12, 9)
model = GPy.models.GPLVM(Y, 3)
connect = np.eye(3)
stick_explorer(model=model, connect=connect)
```

`connect` is a joint adjacency matrix. The OSU demo uses the connectivity
that ships with the dataset. Here `np.eye(3)` just draws three joints.

`from vidden.explore import stick_explorer` still works. That module is a
compatibility import; new code should use `vidden.host.panel`.

## What is not here yet

Oil-flow and Olivetti faces still run through GPy's deprecated
`visualize` module. They will land as more views on this host. Static
GPy plots (`plot`, `plot_latent`, `plot_confidence`) stay in GPy.

## Project management

This repository uses [VibeSafe](https://github.com/lawrennd/vibesafe).
See `tenets/`, `requirements/`, `cip/`, and `backlog/`.
