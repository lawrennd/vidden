# vidden

[![Tests](https://github.com/lawrennd/vidden/actions/workflows/test.yml/badge.svg)](https://github.com/lawrennd/vidden/actions/workflows/test.yml)
[![codecov](https://codecov.io/gh/lawrennd/vidden/graph/badge.svg)](https://codecov.io/gh/lawrennd/vidden)

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

`explore` pulls HoloViews, Panel, and Bokeh. `gpy` is needed for the
stick, doodle, oil, and faces demos (GPy plus [pods](https://github.com/lawrennd/pods)
for OSU motion, oil-flow, and Brendan faces). Jupyter imports need this editable install.
`panel serve examples/...` from the repository root also works without
it: the example scripts put `src/` on `sys.path`.

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

## Demo: latent doodle space

Generated cartoon faces on a smile × roundness grid, as a 2-D Bayesian
GPLVM with the same ARD RBF start as the stick man (lengthscale 0.5,
noise 0.001). This is Baxter and Anjyo's click-to-synthesize demo, not
an interpolation grid.

From the repository root:

```bash
panel serve examples/doodle.py --show
```

Or in Jupyter:

```python
from vidden.host.panel import doodle_explorer

doodle_explorer()
```

The reconstruction pane is a packed doodle (`DoodleView`). The latent
scatter, ARD bars, Optimize button, and click-to-track behaviour are
the same host as the stick man (`latent_explorer`).

The model starts **untrained**. Empty latent space is prior mean zero,
which collapses the face. Optimize first, then click the grey plot.

1. Click **Optimize Bayesian GPLVM** and wait for the log likelihood.
2. Click the grey latent plot once to start tracking. Move the pointer.
3. The mouth and head should follow smile and roundness. If every
   reconstruction looks the same, the GP mean is still the prior, or
   the two visible axes are not the ones that carry those factors —
   switch bars as in the stick demo.

A static grid of decoded stamps is a notebook diagnostic, not how we
present the space.

## Demo: doodle studio

Draw a family, save it as JSON, and check stroke correspondence. Matching
(`vidden.doodle.align`) and files (`vidden.doodle.store`) are separate
from the Panel hosts.

```bash
panel serve examples/doodle_studio.py --show
panel serve examples/doodle_align.py --show
```

Or in Jupyter:

```python
from vidden.host.studio import doodle_studio
from vidden.host.correspondence import doodle_align

doodle_studio()
doodle_align()
```

Keep stores a drawing. Click the gallery to show that doodle in grey
below the pad. Save writes `doodles/<family>/doodles.json`. The
alignment view colours matched strokes and greys extras. Then pack with
`align_doodles` and open `doodle_explorer`.

## Demo: oil flow

12-D oil observations as a line of index against value (`VectorView`),
on a 7-D Bayesian GPLVM. Same host as the stick man.

From the repository root:

```bash
panel serve examples/oil.py --show
```

Or in Jupyter:

```python
from vidden.host.panel import oil_explorer

oil_explorer()
```

The model starts **untrained**. Optimize first, then click the grey
plot. Switch ARD bars to set the five leftover latent axes. Training
labels colour the scatter.

## Demo: Brendan faces

Greyscale face reconstruction (`ImageView`) on a 2-D Bayesian GPLVM.
Reshape matches GPy `brendan_faces`: 20×28, Fortran order, then
transpose, so the face is upright.

From the repository root:

```bash
panel serve examples/faces.py --show
```

Or in Jupyter:

```python
from vidden.host.panel import face_explorer

face_explorer()
```

The model starts **untrained**. Optimize first, then click the grey
plot. If the face is on its side, the Fortran/transpose flags are
wrong — they must stay explicit (Olivetti is 112×92, C order, no
transpose).

## Demo: hierarchical GP-LVM

A **tree** of 2-D latent scatters, not another reconstruction on
`latent_explorer`. The default demo is MATLAB `demWalkRun1`: CMU
subject 35 run (`35_25`) and walk (`35_01`) through pods, split as
`acclaimSplitHierarchy` (skeleton → abdomen / legs / upper body →
limbs). Leaves reconstruct one Acclaim skeleton, not cartoon arms.
Walk and run colour the latent points. Click skeleton, then move.

From the repository root:

```bash
panel serve examples/tree.py --show
```

Or in Jupyter:

```python
from vidden.host.tree import tree_explorer
from vidden.demos import load_walk_tree, load_walk_run_tree

tree_explorer()
tree_explorer(load_walk_tree())
```

Each node is a local interpolant, so the explorer does not need a GPy
`HGPLVM` class. `make_synthetic_hierarchy` remains for tests without
pods. Dynamics sliders are not in this pass.

## What is not here yet

Olivetti can use the same `ImageView` with different reshape flags;
there is no separate demo yet. Static GPy plots (`plot`, `plot_latent`,
`plot_confidence`) stay in GPy. The matplotlib doodle studio on
`notebook-latent-doodle-space` is superseded by the Panel studio here.

## Project management

This repository uses [VibeSafe](https://github.com/lawrennd/vibesafe).
See `tenets/`, `requirements/`, `cip/`, and `backlog/`.
