"""ch01_figs.py -- Chapter 1 figures: battery lifetime versus average power."""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "labs", "python"))
from bricdstyle import *
import biosig as bs

# energy of two small batteries (J): nominal capacity x nominal voltage
BATTERIES = {"CR2032 coin cell (225 mAh, 3 V)": 0.225 * 3.0 * 3600,
             "small Li-po (40 mAh, 3.7 V)": 0.040 * 3.7 * 3600}


def lifetime():
    p = np.logspace(-5, -1.5, 200)                      # 10 uW .. 30 mW
    fig, ax = plt.subplots(figsize=FULL)
    for (name, e), c in zip(BATTERIES.items(), (C1, C2)):
        ax.loglog(p * 1e3, e / p / 86400, color=c, label=name)
    marks = [(bs.SPEC["channels"] * bs.SPEC["power_per_ch_W"], "Open-BioAFE AFE target\n8 ch x 10 uW"),
             (8 * 100e-6, "8 ch x 100 uW"),
             (8 * 1e-3, "discrete-class AFE\n8 ch x ~1 mW")]
    e0 = list(BATTERIES.values())[0]
    for pw, lab in marks:
        d = e0 / pw / 86400
        ax.plot(pw * 1e3, d, "o", color=NAVY, ms=4.5, zorder=5)
        ax.annotate(f"{lab}\n{d:,.0f} days" if d >= 10 else f"{lab}\n{d:.1f} days", xy=(pw * 1e3, d),
                    xytext=(8, 4), textcoords="offset points", fontsize=7, color=NAVY, va="bottom")
    ax.axhline(365, color=GOLD, lw=0.9, ls="--")
    ax.text(0.011, 400, "one year", color=GOLDDK, fontsize=7, va="bottom")
    ax.axhline(1, color=MUTED, lw=0.7, ls=":")
    ax.text(0.011, 1.1, "one day", color=MUTED, fontsize=7, va="bottom")
    ax.set_xlim(0.01, 30); ax.set_ylim(0.05, 5000)
    finish(ax, xlabel="Average power drawn from the battery (mW)", ylabel="Lifetime (days)", legend=True, loc="upper right")
    savefig(fig, "ch01_lifetime")


if __name__ == "__main__":
    lifetime()
