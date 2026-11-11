"""bricdstyle.py -- one matplotlib house style for every plot in the BRICD tutorials (Open-BioAFE copy).

Usage in a figure script (run from anywhere with the tutorial venv python):

    from bricdstyle import *          # palette, sizes, apply(), savefig(), eye helpers
    fig, ax = plt.subplots(figsize=FULL)
    ax.plot(x, y, color=C1, label="channel")
    finish(ax, xlabel="Frequency (GHz)", ylabel="|S21| (dB)", title="Channel loss")
    savefig(fig, "ch03_loss_vs_f")    # -> assets/figs/ch03_loss_vs_f.svg

Figures are drawn at a fixed size (column width = 6.3 in) and saved as SVG for the website.
Put them on a page with <img src="{{ '/assets/figs/NAME.svg' | relative_url }}" ...>.
"""
import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.colors import LinearSegmentedColormap

# ---------------------------------------------------------------- palette (site theme "Monitor", _sass/custom/custom.scss)
GRAPHITE, BLUE, GREEN = "#1D2A30", "#1F64A8", "#1A7A4C"
AMBER, AMBERDK, AMBERLT = "#C98A1C", "#9A6212", "#F2B84B"     # targets, limits, highlights
BROWN, MUTED, PALE, SLATE = "#7A5C14", "#56656B", "#B9C6C9", "#3E4C52"
GRID, BTINT, ATINT, BGPALE = "#E1E8E8", "#E4EEF8", "#FBF1DF", "#F2F5F5"
C1, C2, C3, C4, C5 = "#1F64A8", "#C98A1C", "#1A7A4C", "#B5473A", "#6B5CA5"
SERIES = [C1, C2, C3, C4, C5, GRAPHITE, AMBER]
GOOD, BAD = C3, C4

# ---------------------------------------------------------------- sizes (inches)
TEXTW = 6.3
FULL = (6.3, 2.7)        # full-width, single row
FULLTALL = (6.3, 3.6)
FULL2 = (6.3, 2.5)       # use with 1x2 subplots
HALF = (3.05, 2.35)      # half-width (two side by side in LaTeX with subfigure/minipage)
SQUARE = (3.05, 3.05)

_HERE = os.path.dirname(os.path.abspath(__file__))
FIGDIR = os.path.normpath(os.path.join(_HERE, "..", "assets", "figs"))


def _tex_gyre_paths():
    """TeX Gyre Heros from the local TeX installation (macOS/Linux), found with kpsewhich."""
    import subprocess
    out = []
    for name in ("texgyreheros-regular.otf", "texgyreheros-bold.otf", "texgyreheros-italic.otf",
                 "texgyreheros-bolditalic.otf"):
        try:
            r = subprocess.run(["kpsewhich", name], capture_output=True, text=True, timeout=10)
            if r.stdout.strip():
                out.append(r.stdout.strip())
        except (OSError, subprocess.SubprocessError):
            pass
    return out


def _pick_font():
    for path in _tex_gyre_paths() + ["/usr/share/texmf/fonts/opentype/public/tex-gyre/texgyreheros-regular.otf",
                 "/usr/share/texmf/fonts/opentype/public/tex-gyre/texgyreheros-bold.otf",
                 "/usr/share/texmf/fonts/opentype/public/tex-gyre/texgyreheros-italic.otf",
                 "/usr/share/texmf/fonts/opentype/public/tex-gyre/texgyreheros-bolditalic.otf"]:
        if os.path.exists(path):
            font_manager.fontManager.addfont(path)
    names = {f.name for f in font_manager.fontManager.ttflist}
    return "TeX Gyre Heros" if "TeX Gyre Heros" in names else "DejaVu Sans"


def apply():
    fam = _pick_font()
    plt.rcParams.update({
        "font.family": "sans-serif", "font.sans-serif": [fam, "DejaVu Sans"],
        "mathtext.fontset": "custom", "mathtext.rm": fam, "mathtext.it": fam + ":italic",
        "mathtext.bf": fam + ":bold", "mathtext.sf": fam,
        "font.size": 8.5, "axes.titlesize": 9, "axes.labelsize": 8.5,
        "xtick.labelsize": 7.5, "ytick.labelsize": 7.5, "legend.fontsize": 7.5,
        "axes.edgecolor": MUTED, "axes.labelcolor": GRAPHITE, "axes.linewidth": 0.7,
        "xtick.color": MUTED, "ytick.color": MUTED, "xtick.major.width": 0.6, "ytick.major.width": 0.6,
        "xtick.major.size": 3, "ytick.major.size": 3,
        "axes.spines.top": False, "axes.spines.right": False,
        "axes.grid": True, "grid.color": GRID, "grid.linewidth": 0.6, "axes.axisbelow": True,
        "axes.titleweight": "bold", "axes.titlecolor": GRAPHITE, "axes.titlelocation": "left",
        "axes.prop_cycle": matplotlib.cycler(color=SERIES),
        "lines.linewidth": 1.4, "lines.solid_capstyle": "round",
        "legend.frameon": False, "legend.handlelength": 1.8,
        "figure.dpi": 150, "savefig.dpi": 300, "pdf.fonttype": 42, "ps.fonttype": 42,
        "figure.constrained_layout.use": True,
    })


apply()


def finish(ax, xlabel=None, ylabel=None, title=None, legend=False, loc="best"):
    if xlabel: ax.set_xlabel(xlabel)
    if ylabel: ax.set_ylabel(ylabel)
    if title: ax.set_title(title)
    if legend: ax.legend(loc=loc)
    return ax


def panel(ax, letter, x=-0.02, y=1.04):
    """Panel tag '(a)' in the top-left corner."""
    ax.text(x, y, f"({letter})", transform=ax.transAxes, fontsize=9, fontweight="bold",
            color=AMBERDK, ha="right", va="bottom")


def note(ax, xy, text, xytext, color=GRAPHITE, fs=7.5, ha="left", arrow=True):
    """Annotation with a thin arrow in house style."""
    ax.annotate(text, xy=xy, xytext=xytext, fontsize=fs, color=color, ha=ha, va="center",
                arrowprops=dict(arrowstyle="-|>", lw=0.7, color=color, shrinkA=1, shrinkB=2,
                                mutation_scale=7) if arrow else None)


def savefig(fig, name, png=False):
    os.makedirs(FIGDIR, exist_ok=True)
    out = os.path.join(FIGDIR, name + ".svg")
    fig.savefig(out, bbox_inches="tight", pad_inches=0.03, metadata={"Date": None})
    if png:
        fig.savefig(os.path.join(FIGDIR, name + ".png"), bbox_inches="tight", pad_inches=0.03, dpi=200)
    plt.close(fig)
    print("saved", out)
    return out


# ---------------------------------------------------------------- eye diagrams
EYE_CMAP = LinearSegmentedColormap.from_list(
    "bricd_eye", ["#FFFFFF", "#DCE4F2", PALE, BLUE, GRAPHITE, AMBERDK, AMBERLT], N=256)


def eye_density(ax, y, sps, phase=0, n_ui=2, skip_ui=50, vbins=220, vlim=None, gamma=0.6,
                t_unit="UI", ui_s=200e-12, cmap=EYE_CMAP):
    """Density (persistence) eye diagram of oversampled waveform y.
    phase: sample index (0..sps-1) that should sit at the eye centre (x = 0).
    The window spans [-n_ui/2, +n_ui/2] UI. Returns the image handle."""
    y = np.asarray(y, float)[skip_ui * sps:]
    span = n_ui * sps
    start = (phase - span // 2) % sps
    y = y[start:]
    nseg = (y.size - span) // sps
    segs = np.stack([y[k * sps:k * sps + span + 1] for k in range(nseg)])
    tt = (np.arange(span + 1) - span // 2) / sps
    # upsample each trace 4x (linear) so steep edges do not leave gaps
    up = 4
    tf = np.linspace(tt[0], tt[-1], (tt.size - 1) * up + 1)
    segs_f = np.stack([np.interp(tf, tt, s) for s in segs])
    if vlim is None:
        m = np.max(np.abs(segs_f)) * 1.12
        vlim = (-m, m)
    H, xe, ye = np.histogram2d(np.tile(tf, nseg), segs_f.ravel(), bins=[tf.size // 2, vbins],
                               range=[[tf[0], tf[-1]], list(vlim)])
    H = (H / H.max()) ** gamma
    scale = 1.0 if t_unit == "UI" else ui_s * 1e12
    im = ax.imshow(H.T, origin="lower", aspect="auto", cmap=cmap, interpolation="bilinear",
                   extent=[xe[0] * scale, xe[-1] * scale, ye[0], ye[-1]])
    ax.grid(False)
    ax.set_xlabel("Time (UI)" if t_unit == "UI" else "Time (ps)")
    return im


def eye_lines(ax, y, sps, phase=0, n_ui=2, skip_ui=50, ntraces=400, color=GRAPHITE, alpha=0.06, lw=0.6):
    """Classic overlaid-trace eye diagram (good for few traces / clean channels)."""
    y = np.asarray(y, float)[skip_ui * sps:]
    span = n_ui * sps
    start = (phase - span // 2) % sps
    y = y[start:]
    tt = (np.arange(span + 1) - span // 2) / sps
    n = min(ntraces, (y.size - span) // sps)
    for k in range(n):
        ax.plot(tt, y[k * sps:k * sps + span + 1], color=color, alpha=alpha, lw=lw)
    ax.set_xlim(tt[0], tt[-1])
    ax.set_xlabel("Time (UI)")


def stem_cursors(ax, k, pk, main_color=AMBER, pre_color=C4, post_color=C1, labels=True, fmt="{:.3f}"):
    """Stem plot of pulse-response cursors p_k (k = integer UI index, 0 = main cursor)."""
    k = np.asarray(k); pk = np.asarray(pk)
    for kk, v in zip(k, pk):
        c = main_color if kk == 0 else (pre_color if kk < 0 else post_color)
        ax.vlines(kk, 0, v, color=c, lw=2.2)
        ax.plot(kk, v, "o", color=c, ms=4)
        if labels:
            ax.text(kk, v + (0.02 if v >= 0 else -0.02) * max(1e-9, np.max(np.abs(pk))) * 3,
                    fmt.format(v), ha="center", va="bottom" if v >= 0 else "top", fontsize=6.5, color=c)
    ax.axhline(0, color=MUTED, lw=0.7)
    ax.set_xticks(k)
    ax.set_xticklabels([f"{kk:+d}" if kk else "0" for kk in k])
