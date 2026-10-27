# vidden

Latent-space visualisation, independent of the inference library.

`vidden` is the browser explorer that used to live inside
[GPy](https://github.com/SheffieldML/GPy) as
`GPy.plotting.matplot_dep.visualize`. Those matplotlib and VPython
callbacks do not work on current macOS or Jupyter. The replacement is a
Panel app whose pointer events call `model.predict` in Python.

The name is Norwegian *vidden*: the open expanse.

## Install

```bash
pip install -e ".[explore]"
```

GPy is optional. The stick-man demo needs it:

```bash
pip install -e ".[explore,gpy]"
```

## Stick-man explorer

```bash
panel serve examples/stick.py --show
```

Or from Jupyter:

```python
from vidden.explore import stick_explorer

stick_explorer()
```

A click writes the two visible latent axes. Other coordinates stay where
you left them, starting at zero. Left-click a sensitivity bar for the
red (y) axis. Right-click the histogram and pick a dimension for green
(x). Double-click a bar also sets green.

## What this package is not

GPy's static plots (`plot`, `plot_latent`, `plot_confidence`) stay in
GPy. `vidden` is only the interactive LVM viewers.

## Project management

This repository uses [VibeSafe](https://github.com/lawrennd/vibesafe).
See `tenets/`, `requirements/`, `cip/`, and `backlog/`.
