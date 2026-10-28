"""JSON family store for doodle stroke lists.

No figures, no matplotlib, no Panel. PNG thumbnails are optional files
the gallery may use if they already exist; this module does not render
them.
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np

from vidden.doodle.geometry import cartoon_doodles

VIDDEN_FORMAT = "vidden-doodle-strokes"
GPY_FORMAT = "gpy-doodle-strokes"
_RESERVED_FAMILIES = ("all", "faces", "generated")


def family_slug(name):
    """Filesystem-safe family name: ``Dogs & Bugs`` → ``dogs-bugs``."""
    text = str(name or "").strip().lower()
    chars = [ch if ch.isalnum() else "-" for ch in text]
    slug = "-".join(part for part in "".join(chars).split("-") if part)
    return slug or "faces"


def picker_target(outdir="doodles", family=None):
    """``load_doodle_dir("faces")`` means the faces family, not a folder named faces.

    Returns ``(library_outdir, family_or_none)``.
    """
    if family is not None:
        return outdir, family
    slug = family_slug(outdir)
    if slug in _RESERVED_FAMILIES:
        return "doodles", slug
    try:
        names = list_doodle_families("doodles")
    except OSError:
        names = {}
    if slug in names and slug != "doodles":
        return "doodles", slug
    return outdir, None


def resolve_doodle_root(outdir="doodles"):
    """Find a doodle library from cwd or its parent. Do not search GPy."""
    path = Path(outdir)
    if path.is_absolute():
        return path
    candidates = [Path.cwd() / path, Path.cwd().parent / path]
    for cand in candidates:
        if not cand.exists():
            continue
        if (cand / "doodles.json").is_file():
            return cand.resolve()
        if cand.is_dir() and any((child / "doodles.json").is_file() for child in cand.iterdir() if child.is_dir()):
            return cand.resolve()
    return (Path.cwd() / path).resolve()


def family_dir(outdir, family="faces"):
    """Directory for one named family. Legacy ``outdir/doodles.json`` counts as ``faces``."""
    root = resolve_doodle_root(outdir)
    slug = family_slug(family)
    named = root / slug
    if (named / "doodles.json").is_file():
        return named
    if slug == "faces" and (root / "doodles.json").is_file() and not named.exists():
        return root
    return named


def list_doodle_families(outdir="doodles"):
    """Map family slug → directory for every saved family under ``outdir``."""
    root = resolve_doodle_root(outdir)
    found = {}
    if root.is_dir():
        for child in sorted(root.iterdir()):
            if child.is_dir() and (child / "doodles.json").is_file():
                found[child.name] = child
    if (root / "doodles.json").is_file():
        data = json.loads((root / "doodles.json").read_text(encoding="utf-8"))
        name = family_slug(data.get("family") if isinstance(data, dict) else None)
        if name not in found:
            found[name] = root
    return found


def doodles_to_jsonable(doodles, family="faces"):
    """Convert doodles (lists of ``(k, 2)`` arrays) to a JSON-serialisable dict."""
    return {
        "format": VIDDEN_FORMAT,
        "version": 1,
        "family": family_slug(family),
        "doodles": [[np.asarray(stroke, dtype=float).tolist() for stroke in doodle] for doodle in doodles],
    }


def doodles_from_jsonable(data):
    """Inverse of :func:`doodles_to_jsonable`. Also accepts GPy JSON and a bare list."""
    raw = data if isinstance(data, list) else data["doodles"]
    return [[np.asarray(stroke, dtype=float) for stroke in doodle] for doodle in raw]


def save_doodles(path, doodles, family="faces"):
    """Write doodles to a JSON file. Returns the ``Path``."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(doodles_to_jsonable(doodles, family=family), indent=2), encoding="utf-8")
    return path


def load_doodles(path):
    """Load doodles from a JSON file written by :func:`save_doodles` or GPy."""
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    return doodles_from_jsonable(data)


def save_family(outdir, doodles, family="faces", shrink=False):
    """Write ``doodles.json`` for one family. Does not render PNGs.

    By default a shorter in-memory list does not replace a longer library
    already on disk.
    """
    dest = Path(outdir)
    dest.mkdir(parents=True, exist_ok=True)
    json_path = dest / "doodles.json"
    if not shrink and json_path.is_file():
        existing = load_doodles(json_path)
        if len(existing) > len(doodles):
            doodles = existing
    return save_doodles(json_path, doodles, family=family)


def load_doodle_dir(outdir, family=None):
    """Load ``doodles.json`` and optional PNG paths for one family.

    Returns ``(doodles, png_paths, family)``. A PNG path is ``None`` if that
    file is missing. ``family="all"`` concatenates every saved family.
    """
    root = resolve_doodle_root(outdir)
    families = list_doodle_families(root)
    if family is None:
        if "faces" in families:
            family = "faces"
        elif families:
            family = next(iter(families))
        else:
            family = "faces"
    slug = family_slug(family) if str(family).strip().lower() != "all" else "all"
    if slug == "all":
        doodles, pngs = [], []
        for name in families:
            d, p, _fam = load_doodle_dir(root, name)
            doodles.extend(d)
            pngs.extend(p)
        if not doodles:
            raise FileNotFoundError(f"no saved doodles under {root}")
        return doodles, pngs, "all"
    dest = family_dir(root, slug)
    json_path = dest / "doodles.json"
    if not json_path.is_file():
        raise FileNotFoundError(f"no doodles.json for family {slug!r} under {root}")
    doodles = load_doodles(json_path)
    pngs = []
    for i in range(len(doodles)):
        path = dest / f"doodle_{i:03d}.png"
        pngs.append(path if path.is_file() else None)
    return doodles, pngs, slug


def ensure_cartoon_family(outdir="doodles", family="generated", n_smile=4, n_round=3):
    """Write the generated faces as a named family if they are not on disk yet.

    Returns ``(directory, doodles)``.
    """
    root = resolve_doodle_root(outdir)
    dest = family_dir(root, family)
    json_path = dest / "doodles.json"
    expected = int(n_smile) * int(n_round)
    if json_path.is_file():
        doodles = load_doodles(json_path)
        if len(doodles) == expected:
            return dest, doodles
    doodles = cartoon_doodles(n_smile=n_smile, n_round=n_round)
    save_family(dest, doodles, family=family)
    return dest, doodles
