"""Render the camera-ready reliability figure (Fig. 1) from the signed content-review package.

The figure reads only aggregate CSVs from ``paper/content-review/20261110-r1`` and first checks
their SHA-256 against that package's provenance record, so every plotted number is the signed one.
Fonts are embedded as TrueType (Type 42); the PDF contains no Type 3 fonts. The default theme uses
the SciencePlots ``science + ieee + no-latex`` style (pip install SciencePlots; no LaTeX needed).

    python -m scripts.make_reliability_figure --out-dir paper/camera-ready
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import pandas as pd  # noqa: E402
from matplotlib import patheffects  # noqa: E402
from matplotlib.lines import Line2D  # noqa: E402
from matplotlib.patches import Patch  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "paper/content-review/20261110-r1"
INPUTS = ("capacity_coverage_release.csv", "random_reference.csv")
ALPHA = 0.10

# Okabe-Ito colour-blind-safe palette.
COLORS = {"B2": "#0072B2", "B4": "#D55E00"}
MARKERS = {"B2": "o", "B4": "D"}
LABELS = {"B2": "Confidence (B2)", "B4": "Imputation disagreement (B4)"}
INK, MUTED, RULE, BAND = "#222222", "#6B6B6B", "#BDBDBD", "#E3E3E3"
ROWS = [("S0", "batch"), ("S0", "frozen"), ("S4", "batch"), ("S4", "frozen")]
ROW_LABELS = ["Equal capacity", "Frozen threshold", "Equal capacity", "Frozen threshold"]
SITE = {"S0": "Internal", "S4": "External"}
# White outline keeps data labels legible where they cross reference lines or bands.
HALO = [patheffects.withStroke(linewidth=1.6, foreground="white")]
STYLE = {
    "font.family": "sans-serif",
    "font.sans-serif": ["Liberation Sans", "Arial", "Helvetica", "Nimbus Sans", "DejaVu Sans"],
    "font.size": 7,
    "axes.labelsize": 7,
    "axes.titlesize": 7.5,
    "xtick.labelsize": 6.5,
    "ytick.labelsize": 6.5,
    "legend.fontsize": 6.5,
    "axes.linewidth": 0.6,
    "axes.edgecolor": INK,
    "axes.labelcolor": INK,
    "xtick.color": INK,
    "ytick.color": INK,
    "xtick.major.width": 0.6,
    "xtick.major.size": 2.5,
    "ytick.major.size": 0,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "axes.spines.left": False,
    "pdf.fonttype": 42,
    "ps.fonttype": 42,
    "svg.fonttype": "none",
    "savefig.dpi": 600,
}
# SciencePlots "science + ieee" look (serif, boxed axes, inward ticks), with the overrides a
# camera-ready IEEE figure still needs: TrueType embedding, 7 pt text and a Times-metric serif.
SCIENCEPLOTS_OVERRIDES = {
    "font.serif": ["Liberation Serif", "Nimbus Roman", "Times New Roman", "STIXGeneral"],
    "font.size": 7,
    "axes.labelsize": 7,
    "xtick.labelsize": 6.5,
    "ytick.labelsize": 6.5,
    "legend.fontsize": 6.5,
    "ytick.minor.visible": False,
    "ytick.major.size": 0,
    "ytick.right": False,
    "figure.dpi": 100,
    "pdf.fonttype": 42,
    "ps.fonttype": 42,
    "svg.fonttype": "none",
    "savefig.dpi": 600,
}


def theme_settings(name: str) -> dict:
    """Return the rc styles, method colours, grid choice and file suffix for a theme."""
    if name == "clean":
        return {"styles": [STYLE], "colors": dict(COLORS), "grid": True, "suffix": "_clean", "extra": {}}
    if name == "ieee":
        from importlib.metadata import version

        import scienceplots  # noqa: F401  (registers the styles)

        # Keep the IEEE serif/boxed look but replace its pure red/blue with the softer,
        # colour-blind-safe Okabe-Ito pair used throughout the paper.
        styles = ["science", "ieee", "no-latex", SCIENCEPLOTS_OVERRIDES]
        return {"styles": styles, "colors": dict(COLORS), "grid": False, "suffix": "",
                "extra": {"scienceplots": version("SciencePlots")}}
    raise ValueError(f"Unknown theme {name!r}")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_verified() -> dict[str, pd.DataFrame]:
    expected = json.loads((PACKAGE / "provenance.json").read_text(encoding="utf-8"))["output_sha256"]
    frames = {}
    for name in INPUTS:
        actual = sha256(PACKAGE / name)
        if actual != expected[name]:
            raise ValueError(f"{name}: SHA-256 {actual} does not match signed package {expected[name]}")
        frames[name] = pd.read_csv(PACKAGE / name)
    return frames


def exact_upper_for_zero(n: int, level: float = 0.95) -> float:
    """Clopper-Pearson upper bound when 0 of n are covered: 1 - (alpha/2)^(1/n)."""
    return 1 - ((1 - level) / 2) ** (1 / n)


def row_value(data: pd.DataFrame, scenario: str, mode: str, method: str, field: str):
    rows = data[(data.scenario == scenario) & (data.selection_mode == mode) & (data.method == method)]
    if len(rows) != 1:
        raise ValueError(f"Expected one row for {scenario}/{mode}/{method}, found {len(rows)}")
    return rows.iloc[0][field]


def style_axis(ax, xlim, xticks, xlabel, grid=True):
    ax.set_xlim(*xlim)
    ax.set_xticks(xticks, [f"{t:g}" for t in xticks])
    ax.set_xlabel(xlabel, labelpad=2)
    if grid:
        ax.grid(axis="x", color="#EFEFEF", linewidth=0.5)
    ax.set_axisbelow(True)


def panel_letter(fig, ax, letter, title, x_pad=0.0):
    """Bold panel letter at the panel's outer-left edge and a plain title beside it."""
    box = ax.get_position()
    x = box.x0 - x_pad
    fig.text(x, box.y1 + 0.075, letter, fontsize=8.5, fontweight="bold", color=INK, va="bottom")
    fig.text(x + 0.018, box.y1 + 0.075, title, fontsize=7.5, color=INK, va="bottom")


def draw_coverage(ax, data, grid=True):
    sites = data.drop_duplicates("scenario").set_index("scenario")
    y = {"S0": 0, "S4": 1}
    reference_line(ax, 100 * (1 - ALPHA), "nominal 90%")
    for scenario, pos in y.items():
        row = sites.loc[scenario]
        n, covered = int(row.n), int(row.covered)
        positives, pos_cov = int(row.positives), int(row.positive_covered)
        ax.scatter(100 * covered / n, pos - 0.14, s=18, color=INK, zorder=3, linewidth=0)
        ax.text(100 * covered / n - 3, pos - 0.14, f"{covered:,}/{n:,}", ha="right", va="center", fontsize=6,
                path_effects=HALO, zorder=4)
        if pos_cov != 0:
            raise ValueError("Panel a assumes zero positive-class coverage; update the interval code")
        upper = 100 * exact_upper_for_zero(positives)
        ax.plot([0, upper], [pos + 0.14] * 2, color=INK, linewidth=0.9, linestyle="-",
                solid_capstyle="butt", zorder=2)
        ax.plot([upper] * 2, [pos + 0.06, pos + 0.22], color=INK, linewidth=0.9, linestyle="-", zorder=2)
        ax.scatter(0, pos + 0.14, s=18, facecolor="white", edgecolor=INK, linewidth=0.9, zorder=3, clip_on=False)
        ax.text(upper + 3, pos + 0.14, f"0/{positives}  (95% CI 0–{upper:.1f})", va="center", fontsize=6,
                path_effects=HALO, zorder=4)
    ax.set_yticks([0, 1], [f"Internal\n(n = {int(sites.loc['S0'].n):,})", f"External\n(n = {int(sites.loc['S4'].n):,})"])
    ax.set_ylim(1.55, -0.55)
    ax.axhline(0.5, color=RULE, linewidth=0.6)
    style_axis(ax, (0, 104), [0, 25, 50, 75, 100], "Prediction-set coverage (%)", grid)


def reference_line(ax, x, label):
    ax.axvline(x, color=MUTED, linewidth=0.6, linestyle=(0, (3, 2)), zorder=1)
    ax.text(x, 1.0, label, transform=ax.get_xaxis_transform(), ha="center", va="bottom",
            fontsize=6, color=MUTED, clip_on=False)


def draw_dotrows(ax, value, label_fn, colors, reference=None, ticklabels=True):
    """One row per (site, rule); B2 sits just above B4 so equal values never hide each other."""
    for i, (scenario, mode) in enumerate(ROWS):
        if reference is not None and mode == "batch":
            low, mid, high = reference(scenario)
            ax.add_patch(plt.Rectangle((low, i - 0.32), high - low, 0.64, color=BAND, linewidth=0, zorder=0))
            ax.plot([mid, mid], [i - 0.32, i + 0.32], color=MUTED, linewidth=0.6, linestyle="-", zorder=1)
        for offset, method in ((-0.15, "B2"), (0.15, "B4")):
            x = value(scenario, mode, method)
            ax.scatter(x, i + offset, s=17, marker=MARKERS[method], color=colors[method],
                       edgecolor="white", linewidth=0.4, zorder=3)
            ax.text(x + 2.2, i + offset, label_fn(scenario, mode, method), va="center", fontsize=5.8,
                    path_effects=HALO, zorder=4,
                    color=colors[method])
    for boundary in (0.5, 2.5):
        ax.axhline(boundary, color="#F2F2F2", linewidth=0.5, zorder=0)
    ax.axhline(1.5, color=RULE, linewidth=0.6)
    ax.set_yticks(range(len(ROWS)), ROW_LABELS if ticklabels else [])
    ax.set_ylim(len(ROWS) - 0.45, -0.55)
    if not ticklabels:
        ax.tick_params(axis="y", length=0)


def site_brackets(fig, ax):
    """Bracket each site's two rows, just left of the measured row labels."""
    renderer = fig.canvas.get_renderer()
    left_px = min(t.get_window_extent(renderer).x0 for t in ax.get_yticklabels())
    to_axes = ax.transAxes.inverted()
    x = to_axes.transform((left_px - 4, 0))[0]
    label_x = to_axes.transform((left_px - 10, 0))[0]
    for scenario, top in (("S0", 0), ("S4", 2)):
        ax.plot([x, x], [top - 0.35, top + 1.35], transform=ax.get_yaxis_transform(),
                color=INK, linewidth=0.6, linestyle="-", clip_on=False)
        ax.text(label_x, top + 0.5, SITE[scenario], transform=ax.get_yaxis_transform(), rotation=90,
                ha="center", va="center", fontsize=6.5, fontweight="bold", color=INK)


def draw(frames, out_dir: Path, theme: dict):
    data = frames["capacity_coverage_release.csv"]
    ref = frames["random_reference.csv"].set_index("scenario")
    colors, grid = theme["colors"], theme["grid"]

    with plt.style.context(theme["styles"]):
        fig = plt.figure(figsize=(7.16, 2.2))
        # Panel b carries the row labels shared with panel c, so it starts further right.
        axes = [fig.add_axes([0.105, 0.27, 0.235, 0.56]),
                fig.add_axes([0.505, 0.27, 0.225, 0.56]),
                fig.add_axes([0.755, 0.27, 0.23, 0.56])]

        draw_coverage(axes[0], data, grid)

        def acc(s, m, k):
            return 100 * row_value(data, s, m, k, "acceptance")

        def acc_label(s, m, k):
            return f"{100 * row_value(data, s, m, k, 'acceptance'):.1f}"

        reference_line(axes[1], 60, "target 60%")
        draw_dotrows(axes[1], acc, acc_label, colors)
        style_axis(axes[1], (40, 105), [40, 60, 80, 100], "Accepted patients (% of cohort)", grid)

        def fn(s, m, k):
            return 100 * row_value(data, s, m, k, "dangerous_miss")

        def fn_label(s, m, k):
            a = int(row_value(data, s, m, k, "accepted_false_negative"))
            return f"{a}/{int(row_value(data, s, m, k, 'positives'))}"

        def random_ref(s):
            p = int(row_value(data, s, "batch", "B2", "positives"))
            r = ref.loc[s]
            return (100 * r.reference_low / p, 100 * r.expected_false_negatives / p, 100 * r.reference_high / p)

        draw_dotrows(axes[2], fn, fn_label, colors, reference=random_ref, ticklabels=False)
        style_axis(axes[2], (0, 112), [0, 25, 50, 75, 100], "Positives accepted as negative (%)", grid)
        site_brackets(fig, axes[1])

        panel_letter(fig, axes[0], "a", "Coverage before acceptance", x_pad=0.095)
        panel_letter(fig, axes[1], "b", "Realized acceptance", x_pad=0.13)
        panel_letter(fig, axes[2], "c", "False-negative acceptances", x_pad=0.0)

        fig.legend(
            handles=[
                Line2D([], [], marker="o", linestyle="", markersize=4, color=INK, label="All patients"),
                Line2D([], [], marker="o", linestyle="", markersize=4, markerfacecolor="white",
                       markeredgecolor=INK, label="True positives"),
                *(Line2D([], [], marker=MARKERS[k], linestyle="", markersize=4.5, color=colors[k],
                         markeredgecolor="white", markeredgewidth=0.4, label=LABELS[k]) for k in colors),
                Patch(facecolor=BAND, edgecolor="none", label="Random ranking, central 95%"),
            ],
            loc="lower center", bbox_to_anchor=(0.5, 0.0), ncol=5, frameon=False,
            handletextpad=0.3, columnspacing=1.3, handlelength=1.2,
        )

        out_dir.mkdir(parents=True, exist_ok=True)
        outputs = []
        for ext in ("pdf", "png", "svg"):
            path = out_dir / f"fig1_reliability{theme['suffix']}.{ext}"
            fig.savefig(path, metadata={"CreationDate": None} if ext == "pdf" else None)
            outputs.append(path)
        plt.close(fig)
    return outputs


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out-dir", type=Path, default=ROOT / "paper/camera-ready")
    parser.add_argument("--theme", choices=("ieee", "clean"), default="ieee",
                        help="ieee (camera-ready): SciencePlots science+ieee with Okabe-Ito colours, needs "
                             "SciencePlots; clean: sans-serif alternative written as *_clean.*")
    args = parser.parse_args()
    frames = load_verified()
    theme = theme_settings(args.theme)
    outputs = draw(frames, args.out_dir, theme)
    record = {
        "theme": args.theme,
        **theme["extra"],
        "figure": "Fig. 1 prediction-set coverage and patient disposition (camera-ready)",
        "source_package": "paper/content-review/20261110-r1",
        "input_sha256": {name: sha256(PACKAGE / name) for name in INPUTS},
        "generator": "scripts/make_reliability_figure.py",
        "generator_sha256": sha256(Path(__file__)),
        "matplotlib": matplotlib.__version__,
        "output_sha256": {p.name: sha256(p) for p in outputs},
    }
    (args.out_dir / f"fig1_reliability{theme['suffix']}.provenance.json").write_text(
        json.dumps(record, indent=2) + "\n", encoding="utf-8")
    print("Wrote", ", ".join(str(p) for p in outputs))


if __name__ == "__main__":
    main()
