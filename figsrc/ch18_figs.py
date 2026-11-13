"""ch18_figs.py -- Chapter 18 figure: ENOB of a 12-bit SAR versus unit-capacitor mismatch for a binary array
and a redundant (radix < 2) array, uncalibrated and with calibrated weights; and the energy breakdown per
conversion. Behavioural Monte Carlo with biosig.tone_metrics()."""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "labs", "python"))
from bricdstyle import *
import biosig as bs

N = 12
NS = 4096
F, M = None, None


def unit_weights(radix, cycles, total_units):
    """Integer unit counts per cycle (MSB first) for a radix-`radix` array summing to about total_units."""
    w = radix ** np.arange(cycles - 1, -1, -1)
    return np.maximum(1, np.round(w / w.sum() * (total_units - 1))).astype(int)


def sar(x, units_nom, units_act, noise=0.0, rng=None):
    """Behavioural SAR: decisions with actual weights (+ comparator noise), returns decision bits."""
    tot = units_act.sum() + 1.0
    u = (x + 1) / 2 * tot                        # input in units of the actual array
    acc = np.zeros_like(u)
    bits = np.zeros((len(units_act), len(u)))
    for k, wa in enumerate(units_act):
        n = rng.normal(0, noise, len(u)) if noise else 0.0
        b = (u + n) >= acc + wa
        acc = acc + b * wa
        bits[k] = b
    return bits


def enob_for(sig_u, radix, cycles, calibrated, seed):
    rng = np.random.default_rng(seed)
    nom = unit_weights(radix, cycles, NS)
    act = np.array([rng.normal(1.0, sig_u, k).sum() for k in nom])
    n = 4096
    f, m = bs.coherent_tone(37, 16e3, n)
    x = 0.95 * np.sin(2 * np.pi * m * np.arange(n) / n)
    bits = sar(x, nom, act, noise=0.25 * NS / 4096 / 2, rng=rng)   # LSB/4 comparator noise
    w = act if calibrated else nom.astype(float)
    y = (w[:, None] * bits).sum(axis=0)
    return bs.enob(bs.tone_metrics(y, m)["sndr"])


def fig():
    fig, (a1, a2) = plt.subplots(1, 2, figsize=FULL2)
    sig = np.array([0.002, 0.005, 0.01, 0.0124, 0.02, 0.03])
    for radix, cyc, cal, c, ls, lab in ((2.0, 12, False, C4, "-", "binary, 12 cycles"),
                                        (2.0, 12, True, C4, "--", "binary, calibrated weights"),
                                        (1.8, 14, False, C1, "-", "radix 1.8, 14 cycles"),
                                        (1.8, 14, True, C1, "--", "radix 1.8, calibrated weights")):
        e = [np.median([enob_for(s, radix, cyc, cal, sd) for sd in range(6)]) for s in sig]
        a1.semilogx(sig * 100, e, "o" + ls, color=c, ms=3, label=lab)
    a1.axvline(1.24, color=MUTED, ls=":", lw=0.8)
    a1.text(1.3, 8.2, "0.98 fF MIM", fontsize=6.5, color=MUTED)
    a1.set_xlim(0.18, 3.5); a1.set_ylim(8, 12.2)
    a1.set_xticks([0.2, 0.5, 1, 2, 3]); a1.set_xticklabels(["0.2", "0.5", "1", "2", "3"])
    finish(a1, xlabel=r"Unit-capacitor mismatch $\sigma_u$ (%)", ylabel="ENOB (bits)", legend=True, loc="lower left")
    a1.legend(loc="lower left", fontsize=5.8)
    panel(a1, "a")
    parts = [("comparator", 3.9, C4), ("CDAC switching", 0.84, C1), ("SAR logic", 1.5, C2),
             ("sampler & clock", 0.5, C3), ("reference (avg.)", 0.84, C5)]
    left = 0.0
    for name, e, c in parts:
        a2.barh([0], [e], left=left, color=c, height=0.45, label=f"{name}: {e:g} pJ")
        left += e
    a2.text(left + 0.15, 0, f"{left:.1f} pJ", va="center", fontsize=7.5, color=GRAPHITE)
    a2.set_xlim(0, 10); a2.set_ylim(-0.6, 1.6); a2.set_yticks([])
    finish(a2, xlabel="Energy per conversion (pJ)", legend=True, loc="upper left")
    a2.legend(loc="upper left", fontsize=6.0, ncol=2)
    panel(a2, "b")
    savefig(fig, "ch18_sar")


if __name__ == "__main__":
    for radix, cyc in ((2.0, 12), (1.8, 14)):
        nom = unit_weights(radix, cyc, NS)
        print(radix, cyc, "units", nom.tolist(), "sum", nom.sum())
        for cal in (False, True):
            print("  cal", cal, "ENOB at 1.24%%: %.2f" % np.median([enob_for(0.0124, radix, cyc, cal, sd) for sd in range(6)]))
    tot = 3.9 + 0.84 + 1.5 + 0.5 + 0.84
    print("total %.2f pJ, FoM_W at ENOB 11: %.1f fJ/step; power at 16 kS/s %.3f uW" % (tot, tot / 2 ** 11 * 1e3, tot * 16e3 * 1e-6))
    fig()
