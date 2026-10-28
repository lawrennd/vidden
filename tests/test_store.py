import json

import numpy as np

from vidden.doodle import (
    cartoon_doodles,
    doodles_from_jsonable,
    doodles_to_jsonable,
    ensure_cartoon_family,
    face_from_factors,
    family_dir,
    family_slug,
    list_doodle_families,
    load_doodle_dir,
    load_doodles,
    picker_target,
    resolve_doodle_root,
    save_doodles,
    save_family,
)


def test_json_roundtrip_and_gpy_format():
    original = [face_from_factors(0.5, -0.3), face_from_factors(-0.2, 0.8)]
    restored = doodles_from_jsonable(doodles_to_jsonable(original, family="faces"))
    assert len(restored) == 2
    for want, got in zip(original, restored, strict=True):
        assert len(got) == len(want)
        for w, g in zip(want, got, strict=True):
            np.testing.assert_allclose(g, w)
    gpy = {
        "format": "gpy-doodle-strokes",
        "version": 1,
        "doodles": doodles_to_jsonable(original)["doodles"],
    }
    from_gpy = doodles_from_jsonable(gpy)
    np.testing.assert_allclose(from_gpy[0][0], original[0][0])


def test_save_family_does_not_shrink_library(tmp_path):
    six = [face_from_factors(s, 0.0) for s in np.linspace(-1, 1, 6)]
    save_family(tmp_path, six, family="faces")
    save_family(tmp_path, six[:3], family="faces")
    loaded = load_doodles(tmp_path / "doodles.json")
    assert len(loaded) == 6
    payload = json.loads((tmp_path / "doodles.json").read_text(encoding="utf-8"))
    assert payload["format"] == "vidden-doodle-strokes"
    assert not list(tmp_path.glob("*.png"))


def test_named_family_and_all(tmp_path):
    original = [face_from_factors(0.5, -0.3), face_from_factors(-0.2, 0.8)]
    save_doodles(tmp_path / "doodles.json", original)
    from_dir, png_paths, family = load_doodle_dir(tmp_path)
    assert family == "faces"
    assert len(from_dir) == 2
    assert all(p is None for p in png_paths)
    assert family_slug("Dogs & Bugs") == "dogs-bugs"
    dogs = tmp_path / "lib"
    save_family(family_dir(dogs, "dogs"), original, family="dogs")
    loaded_dogs, pngs_dogs, name = load_doodle_dir(dogs, family="dogs")
    assert name == "dogs"
    assert len(loaded_dogs) == 2
    assert all(p is None for p in pngs_dogs)


def test_picker_target_treats_family_name_as_family():
    assert picker_target("faces") == ("doodles", "faces")
    assert picker_target("generated") == ("doodles", "generated")
    assert picker_target("all") == ("doodles", "all")
    assert picker_target("doodles") == ("doodles", None)
    assert picker_target("doodles", family="generated") == ("doodles", "generated")


def test_cartoon_family_is_twelve_faces(tmp_path):
    doodles = cartoon_doodles()
    assert len(doodles) == 12
    dest, loaded = ensure_cartoon_family(tmp_path)
    assert dest == tmp_path / "generated"
    assert len(loaded) == 12
    families = list_doodle_families(tmp_path)
    assert "generated" in families
    save_family(tmp_path, [face_from_factors(0.0, 0.0)], family="faces")
    all_doodles, pngs, name = load_doodle_dir(tmp_path, family="all")
    assert name == "all"
    assert len(all_doodles) == 13
    assert len(pngs) == 13


def test_resolve_doodle_root_from_notebooks_cwd(tmp_path, monkeypatch):
    lib = tmp_path / "doodles"
    original = [face_from_factors(0.1, 0.0)]
    save_family(lib, original)
    notebooks = tmp_path / "notebooks"
    notebooks.mkdir()
    monkeypatch.chdir(notebooks)
    found = resolve_doodle_root("doodles")
    assert (found / "doodles.json").is_file()
    loaded, pngs, family = load_doodle_dir("doodles")
    assert family == "faces"
    assert len(loaded) == 1
    assert pngs[0] is None
