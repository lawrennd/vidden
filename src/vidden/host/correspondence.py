"""Advanced doodle view: colour-matched stroke correspondence.

Uses :func:`vidden.doodle.align.align_doodles`. Does not draw new strokes
or write files.
"""

from __future__ import annotations

from vidden.doodle.align import EXTRA_GREY, align_doodles, query_match_colors, stroke_palette
from vidden.doodle.geometry import DOODLE_LIMITS, unpack_doodle
from vidden.doodle.store import load_doodle_dir
from vidden.views.doodle import stroke_figure


def correspondence_row(doodles, assignments, template_index=0, packed=None, specs=None, limits=DOODLE_LIMITS):
    """Bokeh figures: drawn doodles coloured by match, extras grey.

    If ``packed`` and ``specs`` are given, a second row shows the aligned
    vectors the model sees.
    """
    n = len(doodles)
    if n < 1:
        raise ValueError("need at least one doodle")
    template = doodles[template_index]
    colors = stroke_palette(len(template))
    top = []
    for i, doodle in enumerate(doodles):
        assignment = assignments[i]
        missing = int((assignment < 0).sum())
        extra = len(doodle) - int((assignment >= 0).sum())
        tag = "template" if i == template_index else "query"
        bits = [tag]
        if missing:
            bits.append(f"miss {missing}")
        if extra:
            bits.append(f"extra {extra}")
        if i == template_index:
            stroke_colors = colors
        else:
            stroke_colors = query_match_colors(len(doodle), assignment, colors)
        fig, _src = stroke_figure(
            doodle,
            colors=stroke_colors,
            limits=limits,
            title=f"{i} {', '.join(bits)}",
            width=260,
            height=260,
        )
        top.append(fig)
    rows = [top]
    if packed is not None and specs is not None:
        bottom = []
        aligned_colors = stroke_palette(len(specs))
        for i, y in enumerate(packed):
            fig, _src = stroke_figure(
                unpack_doodle(y, specs),
                colors=aligned_colors,
                limits=limits,
                title=f"{i} aligned",
                width=260,
                height=260,
            )
            bottom.append(fig)
        rows.append(bottom)
    return rows


def doodle_align(doodles=None, outdir="doodles", family=None, template_index="typical", limits=DOODLE_LIMITS):
    """Advanced studio: show Hungarian matching for a saved or given family."""
    import panel as pn

    pn.extension()
    if doodles is None:
        try:
            doodles, _pngs, family = load_doodle_dir(outdir, family=family)
        except FileNotFoundError:
            from vidden.doodle.geometry import cartoon_doodles

            doodles = cartoon_doodles(n_smile=2, n_round=2)
    Y, specs, assignments = align_doodles(doodles, template_index=template_index)
    if template_index == "typical":
        from vidden.doodle.align import typical_template_index

        shown = typical_template_index(doodles)
    else:
        shown = int(template_index)
    rows = correspondence_row(doodles, assignments, template_index=shown, packed=Y, specs=specs, limits=limits)
    intro = pn.pane.Markdown(
        "### Stroke correspondence\n"
        "Same colour means the matcher put those strokes in the same template "
        f"slot. Grey (`{EXTRA_GREY}`) is a dropped extra. Missing template "
        "strokes are omitted, not drawn at the origin."
    )
    layout_rows = [pn.Row(*row) for row in rows]
    return pn.Column(intro, *layout_rows)
