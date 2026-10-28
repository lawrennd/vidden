import numpy as np
import pytest

from vidden.doodle import EXTRA_GREY, align_doodles, cartoon_doodles, face_from_factors, query_match_colors


def test_align_and_store_do_not_import_ui():
    import inspect

    import vidden.doodle.align as align
    import vidden.doodle.store as store

    for mod in (align, store):
        src = inspect.getsource(mod)
        assert "import panel" not in src
        assert "from panel" not in src
        assert "import bokeh" not in src
        assert "from bokeh" not in src
        assert "import matplotlib" not in src
        assert "from matplotlib" not in src


def test_strokes_from_source_roundtrip():
    pytest.importorskip("bokeh")
    from bokeh.models import ColumnDataSource
    from vidden.host.studio import _strokes_from_source

    src = ColumnDataSource({"xs": [[0.0, 1.0, 1.0], [0.2]], "ys": [[0.0, 0.0, 0.5], [0.1]]})
    doodle = _strokes_from_source(src)
    assert len(doodle) == 1
    np.testing.assert_allclose(doodle[0][-1], [1.0, 0.5])


def test_doodle_studio_keep_save_load(tmp_path):
    pytest.importorskip("holoviews")
    pytest.importorskip("panel")
    pytest.importorskip("bokeh")
    from vidden.host.studio import doodle_studio

    app = doodle_studio(outdir=str(tmp_path), family="faces")
    app._vidden_draw.data = {"xs": [[-0.2, 0.2, 0.1]], "ys": [[0.1, 0.1, -0.2]]}
    app._vidden_keep.clicks = 1
    app._vidden_save.clicks = 1
    assert (tmp_path / "faces" / "doodles.json").is_file() or (tmp_path / "doodles.json").is_file()
    app._vidden_load.clicks = 1
    assert app._vidden_state["doodles"]


def test_doodle_align_builds_and_greys_extras():
    pytest.importorskip("holoviews")
    pytest.importorskip("panel")
    pytest.importorskip("bokeh")
    pytest.importorskip("scipy")
    from vidden.host.correspondence import correspondence_row, doodle_align

    template = face_from_factors(-0.2, 0.1)
    extra = [*face_from_factors(0.4, 0.0), np.array([[0.0, -1.1], [0.1, -1.0]], dtype=float)]
    doodles = [template, extra]
    Y, specs, assignments = align_doodles(doodles)
    colors = query_match_colors(len(extra), assignments[1])
    assert colors[-1] == EXTRA_GREY
    rows = correspondence_row(doodles, assignments, packed=Y, specs=specs)
    assert len(rows) == 2
    assert len(rows[0]) == 2
    app = doodle_align(doodles=cartoon_doodles(n_smile=2, n_round=2))
    assert app is not None


def test_examples_studio_and_align_are_servable():
    from pathlib import Path

    root = Path(__file__).resolve().parents[1]
    for name in ("doodle_studio.py", "doodle_align.py"):
        text = (root / "examples" / name).read_text()
        assert ".servable()" in text
        assert "sys.path.insert" in text
    host_studio = (root / "src" / "vidden" / "host" / "studio.py").read_text()
    host_align = (root / "src" / "vidden" / "host" / "correspondence.py").read_text()
    assert ".servable()" not in host_studio
    assert ".servable()" not in host_align
