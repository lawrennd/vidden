def test_views_import_does_not_serve():
    import vidden.views
    from vidden.views.stick import StickView

    assert StickView is vidden.views.StickView


def test_explore_reexports_view_and_host():
    from vidden.explore import StickView, stick_explorer
    from vidden.host.panel import stick_explorer as host_explorer
    from vidden.views.stick import StickView as View

    assert StickView is View
    assert stick_explorer is host_explorer


def test_examples_stick_is_the_servable_entry():
    from pathlib import Path

    example = Path(__file__).resolve().parents[1] / "examples" / "stick.py"
    host = Path(__file__).resolve().parents[1] / "src" / "vidden" / "host" / "panel.py"
    views = Path(__file__).resolve().parents[1] / "src" / "vidden" / "views" / "stick.py"
    assert ".servable()" in example.read_text()
    assert ".servable()" not in host.read_text()
    assert ".servable()" not in views.read_text()
