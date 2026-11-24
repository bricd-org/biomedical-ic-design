"""ch30_figs.py -- Chapter 30 figure: three checks on simulated numbers, from labs/spice/sg13_flow.py.

    python labs/spice/sg13_flow.py     # writes figsrc/data/sg13_flow_*.csv (needs Docker)
    python figsrc/ch30_figs.py

(a) Simulator settings: the thick-oxide pseudo-resistor of Chapter 8 against gmin, for abstol of 1e-12 and
    1e-18 A, with the 2/gmin floor the simulator adds. (b) Corners: the same pair's high-pass corner with
    C2 = 200 fF at the five MOS corners from -20 to 85 degC. (c) Mismatch: the running estimate of the offset
    sigma of a diode-connected 4/1 um NMOS pair from N Monte Carlo runs, the band a correct estimate falls in
    95 % of the time, and two hand predictions: the per-device coefficient times sqrt 2 times gm/(gm + gds)
    (a diode-connected device moves its gate by that fraction of a threshold shift), and the coefficient read
    as a pair's.
"""
import csv, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "labs", "python"))
from bricdstyle import *
from scipy import stats

DATA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
C2F = 200e-15                       # LNA feedback capacitor (Chapter 8)
A_DEV = 3.9e-3                      # V um, PDK's per-device sigma(VT) coefficient, sg13_lv_nmos
WL = 4.0                            # um^2, the comparator's input devices (Chapter 16)


def rows(name):
    return list(csv.DictReader(open(os.path.join(DATA, name))))


def gmin_data():
    r = rows("sg13_flow_gmin.csv")
    out = {}
    for x in r:
        out.setdefault(float(x["abstol_A"]), []).append((float(x["gmin_S"]), float(x["R_ohm"])))
    return {a: np.array(sorted(v)) for a, v in out.items()}


def corner_data():
    out = {}
    for x in rows("sg13_flow_corners.csv"):
        out.setdefault(x["corner"], []).append((float(x["temp_C"]), float(x["R_ohm"])))
    return {c: np.array(sorted(v)) for c, v in out.items()}


def mc_data():
    return np.array([float(x["vos_V"]) for x in rows("sg13_flow_mc.csv")])


def prediction():
    """Hand prediction of the diode-connected pair's offset sigma: sqrt 2 x per-device sigma x gm/(gm + gds)."""
    x = rows("sg13_flow_gmgds.csv")[0]
    k = float(x["gm_S"]) / (float(x["gm_S"]) + float(x["gds_S"]))
    return np.sqrt(2) * A_DEV / np.sqrt(WL) * k, k


def running_sigma(v):
    n = np.arange(1, len(v) + 1)
    s1 = np.cumsum(v); s2 = np.cumsum(v * v)
    var = (s2 - s1 * s1 / n) / np.maximum(n - 1, 1)
    return n[1:], np.sqrt(var[1:])


def fig():
    fig, (a1, a2, a3) = plt.subplots(1, 3, figsize=(TEXTW, 2.55))
    # (a) gmin
    g = gmin_data()
    gg = np.logspace(-9, -18, 100)
    settled = g[1e-18][0, 1]                       # gmin = 1e-18
    a1.loglog(gg, 2 / gg, color=MUTED, ls="--", lw=0.8)
    a1.annotate(r"simulator's $2/g_\mathrm{min}$", xy=(4e-14, 5e13), xytext=(3e-10, 1.6e14), fontsize=6.2, color=MUTED,
                arrowprops=dict(arrowstyle="-", color=MUTED, lw=0.6), va="center")
    a1.axhline(settled, color=AMBER, ls=":", lw=0.9)
    a1.loglog(g[1e-12][:, 0], g[1e-12][:, 1], color=C1, marker="o", ms=3, lw=1.3, label="abstol $10^{-12}$ A (default)")
    a1.loglog(g[1e-18][:, 0], g[1e-18][:, 1], ls="none", marker="o", ms=6, mfc="none", mec=C2, mew=0.8, label="abstol $10^{-18}$ A")
    a1.annotate("ngspice\ndefault", xy=(1e-12, 1.93e12), xytext=(1e-10, 2.5e12), fontsize=6.2, color=GRAPHITE,
                arrowprops=dict(arrowstyle="-", color=MUTED, lw=0.6), va="center")
    a1.annotate("Ch. 8: 3 % low", xy=(1e-15, 5.59e13), xytext=(1e-16, 8e12), fontsize=6.2, color=GRAPHITE,
                arrowprops=dict(arrowstyle="-", color=MUTED, lw=0.6), ha="center")
    a1.set_xlim(1e-9, 1e-18); a1.set_ylim(1e9, 4e14)
    a1.set_xticks([1e-9, 1e-12, 1e-15, 1e-18])
    finish(a1, xlabel=r"$g_\mathrm{min}$ (S)", ylabel="Simulated resistance (Ω)", legend=True, loc="lower right")
    a1.legend(loc="lower right", fontsize=5.4)
    panel(a1, "a")
    # (b) corners
    cd = corner_data()
    a2.axvspan(0, 45, color=BTINT, lw=0)
    a2.text(22.5, 4.5, "in use", fontsize=6.2, color=MUTED, ha="center")
    for c, col in (("ff", C4), ("sf", C2), ("tt", C1), ("fs", C5), ("ss", C3)):
        t, r = cd[c][:, 0], cd[c][:, 1]
        a2.semilogy(t, 1 / (2 * np.pi * r * C2F), color=col, marker="o", ms=2.5, lw=1.1, label=c)
    for f0, lab in ((0.5, "0.5 Hz"), (0.05, "0.05 Hz")):
        a2.axhline(f0, color=AMBER, ls="--", lw=0.8)
        a2.text(-18, f0 * 1.25, lab, fontsize=6.0, color=AMBERDK)
    a2.set_xlim(-20, 85); a2.set_ylim(3e-5, 10)
    a2.set_xticks([-20, 0, 27, 45, 85])
    finish(a2, xlabel="Temperature (°C)", ylabel=r"High-pass corner, $C_2$ = 200 fF (Hz)", legend=True, loc="lower right")
    a2.legend(loc="lower right", fontsize=5.4, ncol=2)
    panel(a2, "b")
    # (c) Monte Carlo
    v = mc_data()
    n, s = running_sigma(v)
    pred, k = prediction()
    nn = np.unique(np.round(np.logspace(np.log10(2), np.log10(len(v)), 200)).astype(int))
    lo = pred * np.sqrt(stats.chi2.ppf(0.025, nn - 1) / (nn - 1))
    hi = pred * np.sqrt(stats.chi2.ppf(0.975, nn - 1) / (nn - 1))
    a3.fill_between(nn, lo * 1e3, hi * 1e3, color=BTINT, lw=0)
    a3.semilogx(n, s * 1e3, color=C1, lw=1.0, label="Monte Carlo estimate")
    a3.axhline(pred * 1e3, color=AMBER, ls="--", lw=0.9, label=r"$%.2f\times\sqrt{2}\times3.9/\sqrt{4}$ = %.2f mV" % (k, pred * 1e3))
    a3.axhline(A_DEV / np.sqrt(WL) * 1e3, color=C4, ls=":", lw=1.0, label=r"$3.9/\sqrt{4}$ = %.2f mV" % (A_DEV / np.sqrt(WL) * 1e3))
    a3.set_xlim(2, len(v)); a3.set_ylim(0, 5)
    finish(a3, xlabel="Monte Carlo runs N", ylabel="Offset σ estimate (mV)", legend=True, loc="upper right")
    a3.legend(loc="upper right", fontsize=5.4)
    panel(a3, "c")
    savefig(fig, "ch30_checks")


def report():
    g = gmin_data()
    print("gmin sweep (abstol 1e-12 / 1e-15 / 1e-18):")
    for k in range(len(g[1e-12])):
        print("  gmin %.0e: %s" % (g[1e-12][k, 0], " / ".join("%.4g" % g[a][k, 1] for a in (1e-12, 1e-15, 1e-18))))
    settled = g[1e-18][0, 1]
    for gm in (1e-12, 1e-14, 1e-15, 1e-16):
        r = g[1e-12][g[1e-12][:, 0] == gm][0, 1]
        print("  gmin %.0e: %.3g ohm, %+.1f %% vs settled %.4g; R||2/gmin = %.4g" % (gm, r, (r / settled - 1) * 100, settled, 1 / (1 / settled + gm / 2)))
    cd = corner_data()
    print("high-pass corner with C2 = 200 fF (Hz), tau = R C2 (s):")
    for c in ("tt", "ss", "ff", "sf", "fs"):
        print("  %s: " % c + "  ".join("%d C %.3g Hz (%.0f s)" % (t, 1 / (2 * np.pi * r * C2F), r * C2F) for t, r in cd[c]))
    v = mc_data()
    s = v.std(ddof=1); N = len(v)
    lo = s * np.sqrt((N - 1) / stats.chi2.ppf(0.975, N - 1)); hi = s * np.sqrt((N - 1) / stats.chi2.ppf(0.025, N - 1))
    pred, k = prediction()
    print("Monte Carlo: N %d, mean %.3f mV, sigma %.3f mV, 95 %% CI %.3f-%.3f mV" % (N, v.mean() * 1e3, s * 1e3, lo * 1e3, hi * 1e3))
    print("  predictions: sqrt2 x 3.9/sqrt4 = %.3f mV; x gm/(gm+gds) %.3f = %.3f mV; 3.9/sqrt4 = %.3f mV"
          % (np.sqrt(2) * A_DEV / np.sqrt(WL) * 1e3, k, pred * 1e3, A_DEV / np.sqrt(WL) * 1e3))
    for n in (10, 40, 193, 1000, 4000):
        a, b = np.sqrt(stats.chi2.ppf([0.025, 0.975], n - 1) / (n - 1))
        print("  first %d runs: sigma %.3f mV; a correct estimate falls within %.3f-%.3f of the truth (approx +-%.1f %%)" % (
            n, v[:n].std(ddof=1) * 1e3, a, b, 196 / np.sqrt(2 * (n - 1))))
    # when does the running estimate leave the band of the 1.95 mV reading for good?
    nr, sr = running_sigma(v)
    wrong = A_DEV / np.sqrt(WL)
    hi_w = wrong * np.sqrt(stats.chi2.ppf(0.975, nr - 1) / (nr - 1))
    inside = np.where(sr <= hi_w)[0]
    print("  running estimate last inside the 95 %% band of the 1.95 mV reading at N = %d" % (nr[inside[-1]] if len(inside) else 1))
    print("  beyond 3 sigma: %d of %d (Gaussian expects %.1f)" % (np.sum(abs(v - v.mean()) > 3 * s), N, N * 0.0027))
    print("  runs to count a 0.27 %% failure rate to +-20 %% (95 %%): %.0f" % ((1.96 / 0.2) ** 2 / 0.0027))


if __name__ == "__main__":
    report()
    fig()
