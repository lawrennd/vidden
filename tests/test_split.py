def test_views_import_does_not_serve():
    import vidden.views
    from vidden.views.doodle import DoodleView
    from vidden.views.stick import StickView

    assert StickView is vidden.views.StickView
    assert DoodleView is vidden.views.DoodleView


def test_explore_reexports_view_and_host():
    from vidden.explore import DoodleView, doodle_explorer, latent_explorer, StickView, stick_explorer
    from vidden.host.panel import (
        doodle_explorer as host_doodle,
        latent_explorer as host_latent,
        stick_explorer as host_explorer,
    )
    from vidden.views.doodle import DoodleView as Doodle
    from vidden.views.stick import StickView as View

    assert StickView is View
    assert DoodleView is Doodle
    assert stick_explorer is host_explorer
    assert doodle_explorer is host_doodle
    assert latent_explorer is host_latent


def test_examples_stick_is_the_servable_entry():
    from pathlib import Path

    example = Path(__file__).resolve().parents[1] / "examples" / "stick.py"
    host = Path(__file__).resolve().parents[1] / "src" / "vidden" / "host" / "panel.py"
    views = Path(__file__).resolve().parents[1] / "src" / "vidden" / "views" / "stick.py"
    text = example.read_text()
    assert ".servable()" in text
    assert "sys.path.insert" in text
    assert ".servable()" not in host.read_text()
    assert ".servable()" not in views.read_text()
