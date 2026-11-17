"""Render the study-pipeline overview figure for the IEEE BDDM 2026 manuscript.

A schematic only: every count it shows is quoted from the reviewed manuscript text
(paper/manuscript_draft.md, Table 2 and Methods). Style matches the reliability figure
(SciencePlots-like serif, Okabe-Ito colours) and fonts are embedded as TrueType (no Type 3).

    python -m scripts.make_pipeline_figure --out-dir paper/camera-ready
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch, Rectangle  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]

INK, MUTED, LINE = "#1F1F1F", "#5E5E5E", "#9A9A9A"
BLUE, ORANGE, GREEN = "#0072B2", "#D55E00", "#009E73"
PANEL, HEADER = "#F7F7F7", "#E9EEF3"
SPLIT = [("Train", 60, "#C9D6E3"), ("Rule", 10, "#E8C9A9"), ("Cal.", 15, "#BFDCCF"), ("Test", 15, "#9FB8D0")]

STYLE = {
    "font.family": "serif",
    "font.serif": ["Liberation Serif", "Nimbus Roman", "Times New Roman", "STIXGeneral"],
    "mathtext.fontset": "stix",
    "font.size": 6.5,
    "pdf.fonttype": 42,
    "ps.fonttype": 42,
    "svg.fonttype": "none",
    "savefig.dpi": 600,
}

W, H = 7.16, 2.05            # inches; IEEE full text width
COLS, GAP, X0 = 5, 0.17, 0.02
CW = (W - 2 * X0 - (COLS - 1) * GAP) / COLS
TOP, BOTTOM, HEAD = H - 0.03, 0.03, 0.30


def text(ax, x, y, s, size=6.5, color=INK, ha="left", va="center", weight="normal", style="normal"):
    ax.text(x, y, s, fontsize=size, color=color, ha=ha, va=va, fontweight=weight, fontstyle=style, zorder=20)


def box(ax, x, y, w, h, fc, ec="none", lw=0.6, r=0.04, z=1):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle=f"round,pad=0,rounding_size={r}",
                                fc=fc, ec=ec, lw=lw, zorder=z))


def arrow(ax, x0, y0, x1, y1, color=LINE, lw=0.8, z=3):
    ax.add_patch(FancyArrowPatch((x0, y0), (x1, y1), arrowstyle="-|>", mutation_scale=6,
                                 color=color, lw=lw, shrinkA=0, shrinkB=0, zorder=z))


def stage(ax, i, title):
    x = X0 + i * (CW + GAP)
    box(ax, x, BOTTOM, CW, TOP - BOTTOM, PANEL, ec="#D4D4D4")
    box(ax, x, TOP - HEAD, CW, HEAD, HEADER, r=0.04, z=2)
    ax.add_patch(Rectangle((x, TOP - HEAD), CW, 0.05, fc=HEADER, ec="none", zorder=2))
    ax.add_patch(plt.Circle((x + 0.15, TOP - HEAD / 2), 0.085, fc=INK, ec="none", zorder=3))
    text(ax, x + 0.15, TOP - HEAD / 2 - 0.003, str(i + 1), size=6.5, color="white", ha="center", weight="bold")
    text(ax, x + 0.28, TOP - HEAD / 2, title, size=7.2, weight="bold")
    if i < COLS - 1:
        y = (TOP + BOTTOM) / 2 - 0.1
        arrow(ax, x + CW + 0.02, y, x + CW + GAP - 0.02, y, color=INK, lw=0.9)
    return x


def stage_cohort(ax):
    x = stage(ax, 0, "Cohort & features")
    pad, y = 0.08, TOP - HEAD - 0.17
    text(ax, x + pad, y, "PhysioNet/CinC 2019", size=6.5, weight="bold")
    # Hospital A split bar
    y -= 0.2
    text(ax, x + pad, y, "Hospital A", size=6.3)
    text(ax, x + CW - pad, y, "10,174 pts · 57 events", size=5.6, color=MUTED, ha="right")
    y -= 0.15
    bx, bw = x + pad, CW - 2 * pad
    cursor = bx
    for name, pct, colour in SPLIT:
        seg = bw * pct / 100
        ax.add_patch(Rectangle((cursor, y - 0.055), seg, 0.11, fc=colour, ec="white", lw=0.5, zorder=3))
        text(ax, cursor + seg / 2, y, name, size=4.3, ha="center")
        cursor += seg
    text(ax, bx, y - 0.13, "train / rule select / calibrate / test", size=5.2, color=MUTED)
    text(ax, bx, y - 0.24, "= 60 / 10 / 15 / 15%, stratified", size=5.2, color=MUTED)
    # Hospital B
    y -= 0.40
    text(ax, x + pad, y, "Hospital B", size=6.3)
    text(ax, x + CW - pad, y, "13,921 pts · 38 events", size=5.6, color=MUTED, ha="right")
    y -= 0.15
    ax.add_patch(Rectangle((bx, y - 0.055), bw, 0.11, fc="#9FB8D0", ec="white", lw=0.5, zorder=3))
    text(ax, bx + bw / 2, y, "held out: external test", size=4.6, ha="center")
    # Features and outcome
    y -= 0.22
    text(ax, x + pad, y, "Last value ≤ 12 h: 34 vitals/labs", size=5.6)
    text(ax, x + pad, y - 0.13, "+ age, sex, missingness flags", size=5.6)
    text(ax, x + pad, y - 0.28, "Outcome: sepsis onset in (12, 24] h", size=5.6, weight="bold")


def stage_imputation(ax):
    x = stage(ax, 1, "Multiple imputation")
    pad = 0.08
    # stacked completed copies
    sx, sy = x + pad + 0.06, TOP - HEAD - 0.62
    for k in range(4, -1, -1):
        ax.add_patch(Rectangle((sx + 0.035 * k, sy + 0.035 * k), 0.36, 0.30, fc="white",
                               ec="#7A7A7A", lw=0.5, zorder=3 + (5 - k)))
    for r in range(3):
        for c in range(4):
            fill = "#F2B880" if (r + 2 * c) % 5 == 0 else "#D9D9D9"
            ax.add_patch(Rectangle((sx + 0.035 + 0.075 * c, sy + 0.04 + 0.08 * r), 0.06, 0.06,
                                   fc=fill, ec="none", zorder=9))
    text(ax, sx + 0.23, sy - 0.08, "$M = 10$ completions", size=5.6, ha="center")
    text(ax, sx + 0.23, sy - 0.19, "chained equations", size=5.2, color=MUTED, ha="center")
    # shared predictor
    lx = x + CW - pad - 0.42
    box(ax, lx, sy + 0.06, 0.42, 0.22, "white", ec=INK, lw=0.6, r=0.03, z=4)
    text(ax, lx + 0.21, sy + 0.17, "shared LR", size=5.8, ha="center", weight="bold")
    arrow(ax, sx + 0.52, sy + 0.17, lx - 0.02, sy + 0.17, color=INK, lw=0.6)
    # probability strip
    py = BOTTOM + 0.42
    sx0, sx1 = x + pad + 0.05, x + CW - pad - 0.05
    ax.plot([sx0, sx1], [py, py], color=LINE, lw=0.6, zorder=3)
    for t, lab in ((0, "0"), (1, "1")):
        xx = sx0 + t * (sx1 - sx0)
        ax.plot([xx, xx], [py - 0.03, py + 0.03], color=LINE, lw=0.6, zorder=3)
        text(ax, xx, py - 0.09, lab, size=5, color=MUTED, ha="center")
    draws = [0.18, 0.22, 0.25, 0.27, 0.29, 0.31, 0.34, 0.36, 0.40, 0.44]
    for p in draws:
        ax.add_patch(plt.Circle((sx0 + p * (sx1 - sx0), py + 0.05), 0.016, fc=ORANGE, ec="none", zorder=4))
    mean = sum(draws) / len(draws)
    mx = sx0 + mean * (sx1 - sx0)
    ax.plot([mx, mx], [py - 0.02, py + 0.12], color=INK, lw=0.8, zorder=5)
    lo, hi = sx0 + 0.18 * (sx1 - sx0), sx0 + 0.44 * (sx1 - sx0)
    ax.plot([lo, hi], [py + 0.15, py + 0.15], color=ORANGE, lw=0.8, zorder=5)
    text(ax, sx1, py + 0.15, "$p_{i1},\\dots,p_{iM}$", size=5.4, color=MUTED, ha="right")
    arrow(ax, lx + 0.21, sy + 0.04, lx + 0.21, py + 0.24, color=INK, lw=0.6)
    text(ax, x + pad, BOTTOM + 0.17, "$\\bar p_i$ = mean", size=5.8)
    text(ax, x + CW - pad, BOTTOM + 0.17, "$D_i$ = SD (disagreement)", size=5.8, color=ORANGE, ha="right")


def stage_conformal(ax):
    x = stage(ax, 2, "Split conformal sets")
    pad = 0.08
    y = TOP - HEAD - 0.17
    text(ax, x + pad, y, "Score $1-\\bar p_i(y)$; threshold", size=5.8)
    text(ax, x + pad, y - 0.13, "from calibration, $\\alpha = 0.10$", size=5.8)
    chips = [("{0}", GREEN, "white"), ("{1}", GREEN, "white"), ("{0, 1}", "#BDBDBD", INK), ("$\\varnothing$", "#BDBDBD", INK)]
    cy = y - 0.43
    cw = (CW - 2 * pad - 0.15) / 4
    for k, (lab, fc, tc) in enumerate(chips):
        cx = x + pad + k * (cw + 0.05)
        box(ax, cx, cy - 0.09, cw, 0.18, fc, r=0.03, z=4)
        text(ax, cx + cw / 2, cy, lab, size=6, color=tc, ha="center", weight="bold")
    gx = x + pad
    gw = 2 * cw + 0.05
    # singleton pool / deferred
    py = cy - 0.42
    box(ax, gx, py - 0.13, gw, 0.26, "#DCEFE7", ec=GREEN, lw=0.6, r=0.03, z=4)
    text(ax, gx + gw / 2, py + 0.04, "singleton", size=5.6, ha="center", weight="bold", color="#00634A")
    text(ax, gx + gw / 2, py - 0.07, "pool", size=5.6, ha="center", weight="bold", color="#00634A")
    dx = gx + gw + 0.05
    box(ax, dx, py - 0.13, gw, 0.26, "#EDEDED", ec="#9E9E9E", lw=0.6, r=0.03, z=4)
    text(ax, dx + gw / 2, py, "defer", size=5.8, ha="center", weight="bold", color=MUTED)
    for k in range(4):
        cx0 = x + pad + k * (cw + 0.05) + cw / 2
        tx = (gx + gw / 2 if k < 2 else dx + gw / 2) + (-0.08 if k % 2 == 0 else 0.08)
        arrow(ax, cx0, cy - 0.11, tx, py + 0.15, color=LINE, lw=0.6)
    text(ax, x + pad, BOTTOM + 0.17, "Coverage checked for all and", size=5.4, color=MUTED)
    text(ax, x + pad, BOTTOM + 0.06, "for true positives separately", size=5.4, color=MUTED)


def stage_ranking(ax):
    x = stage(ax, 3, "Rank & accept")
    pad = 0.08
    y = TOP - HEAD - 0.17
    text(ax, x + pad, y, "Rank the same pool by:", size=5.8)
    signals = [("B2", "confidence", BLUE), ("B3", "missingness burden", GREEN), ("B4", "disagreement $D_i$", ORANGE)]
    for k, (code, name, colour) in enumerate(signals):
        yy = y - 0.17 - 0.15 * k
        box(ax, x + pad, yy - 0.055, 0.22, 0.11, colour, r=0.02, z=4)
        text(ax, x + pad + 0.11, yy, code, size=5.4, color="white", ha="center", weight="bold")
        text(ax, x + pad + 0.28, yy, name, size=5.8)
    y2 = y - 0.75
    text(ax, x + pad, y2, "Equal capacity", size=5.8, weight="bold")
    text(ax, x + pad, y2 - 0.13, "$K=\\min(\\lfloor cN \\rfloor, N_{\\rm single})$, $c = 0.6$", size=5.6)
    text(ax, x + pad, y2 - 0.31, "Frozen threshold", size=5.8, weight="bold")
    text(ax, x + pad, y2 - 0.44, "cutoffs fixed in Hospital A", size=5.6)
    ay = BOTTOM + 0.12
    bw = (CW - 2 * pad - 0.06) / 2
    box(ax, x + pad, ay - 0.08, bw, 0.16, "#DCEFE7", ec=GREEN, lw=0.5, r=0.03, z=4)
    text(ax, x + pad + bw / 2, ay, "accept", size=5.8, ha="center", weight="bold", color="#00634A")
    box(ax, x + pad + bw + 0.06, ay - 0.08, bw, 0.16, "#EDEDED", ec="#9E9E9E", lw=0.5, r=0.03, z=4)
    text(ax, x + pad + 1.5 * bw + 0.06, ay, "defer", size=5.8, ha="center", weight="bold", color=MUTED)


def stage_evaluation(ax):
    x = stage(ax, 4, "Evaluate")
    pad = 0.08
    y = TOP - HEAD - 0.17
    for k, (name, n) in enumerate((("Internal test (S0)", "1,525 pts · 8 events"),
                                   ("External test (S4)", "13,921 pts · 38 events"))):
        yy = y - 0.32 * k
        text(ax, x + pad, yy, name, size=6.2, weight="bold")
        text(ax, x + pad, yy - 0.13, n, size=5.6, color=MUTED)
    items = ["Coverage: all vs. positives",
             "Selective risk, B4 − B2",
             "Paired positive dispositions",
             "Realized acceptance",
             "Random-ranking reference"]
    y2 = y - 0.72
    for k, item in enumerate(items):
        yy = y2 - 0.15 * k
        ax.add_patch(plt.Circle((x + pad + 0.03, yy), 0.018, fc=INK, ec="none", zorder=4))
        text(ax, x + pad + 0.09, yy, item, size=5.8)
    text(ax, x + pad, BOTTOM + 0.06, "1,000 paired bootstrap resamples", size=5.4, color=MUTED)


def draw(out_dir: Path):
    with plt.rc_context(STYLE):
        fig = plt.figure(figsize=(W, H))
        ax = fig.add_axes([0, 0, 1, 1])
        ax.set_xlim(0, W)
        ax.set_ylim(0, H)
        ax.set_axis_off()
        stage_cohort(ax)
        stage_imputation(ax)
        stage_conformal(ax)
        stage_ranking(ax)
        stage_evaluation(ax)
        out_dir.mkdir(parents=True, exist_ok=True)
        outputs = []
        for ext in ("pdf", "png", "svg"):
            path = out_dir / f"fig_pipeline.{ext}"
            fig.savefig(path, metadata={"CreationDate": None} if ext == "pdf" else None)
            outputs.append(path)
        plt.close(fig)
    return outputs


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out-dir", type=Path, default=ROOT / "paper/camera-ready")
    args = parser.parse_args()
    outputs = draw(args.out_dir)
    record = {
        "figure": "Study pipeline overview (schematic; counts quoted from paper/manuscript_draft.md)",
        "generator": "scripts/make_pipeline_figure.py",
        "generator_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "matplotlib": matplotlib.__version__,
        "output_sha256": {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in outputs},
    }
    (args.out_dir / "fig_pipeline.provenance.json").write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
    print("Wrote", ", ".join(str(p) for p in outputs))


if __name__ == "__main__":
    main()
