"""ch07_figs.py -- Chapter 7 figures: CMRR of the three-op-amp IA versus resistor tolerance and the
gain that a +-300 mV offset allows at 1.2 V; CMRR of a capacitively coupled IA from MIM mismatch, and
CMRR versus frequency from input RC mismatch. Monte Carlo and closed-form models."""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "labs", "python"))
from bricdstyle import *
import biosig as bs

MIM_DENSITY = 1.5e-15        # F/um^2, SG13G2 cornerCAP.lib cap_carea
MIM_AC = 0.01                # 1 %.um, capacitors_mod_mismatch.lib
CMRR_OPAMP_DB = 100.0


def diffamp_cmrr(g2, tol, n=20000, seed=7):
    """CMRR (linear) samples of a difference amplifier of gain g2 with four resistors uniform in +-tol."""
    rng = np.random.default_rng(seed)
    r3 = 1 + rng.uniform(-tol, tol, n); r5 = 1 + rng.uniform(-tol, tol, n)
    r4 = g2 * (1 + rng.uniform(-tol, tol, n)); r6 = g2 * (1 + rng.uniform(-tol, tol, n))
    gcm = r6 / (r5 + r6) * (1 + r4 / r3) - r4 / r3
    gdm = 0.5 * (r6 / (r5 + r6) * (1 + r4 / r3) + r4 / r3)
    return np.abs(gdm / gcm)


def total_cmrr_db(g1, cmrr_lin):
    """First stage of gain g1 (common-mode gain 1) multiplies the second stage's CMRR; the op-amp's own
    CMRR adds in parallel (1/CMRR terms add)."""
    inv = 1 / cmrr_lin + 10 ** (-CMRR_OPAMP_DB / 20)
    return 20 * np.log10(g1 / inv)


def fig_three_opamp():
    fig, (a1, a2) = plt.subplots(1, 2, figsize=FULL2)
    tols = np.logspace(-4, -2, 13)
    for g1, c in ((1.0, C4), (1.5, C2), (10.0, C1), (100.0, C3)):
        med = [np.median(total_cmrr_db(g1, diffamp_cmrr(1.0, t))) for t in tols]
        a1.semilogx(tols * 100, med, "o-", color=c, ms=2.8, label=f"first-stage gain {g1:g}")
        wc = 20 * np.log10(g1 / ((4 * tols) / 2 + 10 ** (-CMRR_OPAMP_DB / 20)))
        a1.semilogx(tols * 100, wc, color=c, ls=":", lw=0.9)
    a1.axhline(90, color=AMBER, ls="--", lw=0.9)
    a1.text(0.0105, 91.5, "90 dB target", fontsize=7, color=AMBERDK, va="bottom")
    a1.set_xlim(0.01, 1); a1.set_ylim(30, 150)
    a1.set_xticks([0.01, 0.1, 1]); a1.set_xticklabels(["0.01", "0.1", "1"])
    finish(a1, xlabel="Resistor tolerance (%)", ylabel="CMRR (dB)", legend=True, loc="upper right")
    a1.legend(loc="upper right", fontsize=6.0)
    panel(a1, "a")
    off = np.linspace(0.01, 0.4, 200)
    for vdd, swing, c in ((1.2, 0.45, C1), (1.8, 0.75, C5), (3.3, 1.5, C3)):
        a2.semilogy(off * 1e3, swing / off, color=c, label=f"{vdd:g} V supply (±{swing:g} V swing)")
    a2.axvline(300, color=AMBER, ls="--", lw=0.9)
    a2.text(305, 2.2, "±300 mV\noffset", fontsize=7, color=AMBERDK)
    a2.axhline(100, color=MUTED, ls=":", lw=0.8)
    a2.text(15, 115, "gain 100", fontsize=6.5, color=MUTED)
    a2.set_xlim(0, 400); a2.set_ylim(0.8, 200)
    finish(a2, xlabel="Electrode offset at the input (mV)", ylabel="Largest DC-coupled first-stage gain",
           legend=True, loc="upper right")
    a2.legend(loc="upper right", fontsize=6.3)
    panel(a2, "b")
    savefig(fig, "ch07_threeopamp")


def fig_ccia():
    fig, (a1, a2) = plt.subplots(1, 2, figsize=FULL2)
    cin = np.logspace(np.log10(1e-12), np.log10(100e-12), 100)
    area = cin / MIM_DENSITY
    sig = np.sqrt(2) * MIM_AC / np.sqrt(area)           # sigma of (C1 - C2)/C
    for k, ls in ((1, "-"), (3, "--")):
        a1.semilogx(cin * 1e12, 20 * np.log10(1 / (k * sig)), color=C1, ls=ls,
                    label=f"input-capacitor mismatch, {k}σ")
    a1.axhline(90, color=AMBER, ls="--", lw=0.9)
    a1.text(1.1, 91.5, "90 dB target", fontsize=7, color=AMBERDK, va="bottom")
    a1.axvline(20, color=MUTED, ls=":", lw=0.7)
    a1.text(21, 84, "20 pF =\n13 300 µm²", fontsize=6.5, color=MUTED)
    a1.set_xlim(1, 100); a1.set_ylim(50, 100)
    finish(a1, xlabel=r"Input capacitor $C_\mathrm{in}$ (pF, MIM)", ylabel="CMRR without chopping (dB)", legend=True,
           loc="lower right")
    a1.legend(loc="lower right", fontsize=6.3)
    panel(a1, "a")
    f = np.logspace(0, 5, 300)
    for r, dc, c, lab in ((10e3, 0.1e-12, C3, "10 kΩ, ΔC = 0.1 pF"), (10e3, 1e-12, C1, "10 kΩ, ΔC = 1 pF"),
                          (100e3, 1e-12, C4, "100 kΩ, ΔC = 1 pF")):
        a2.semilogx(f, -20 * np.log10(2 * np.pi * f * r * dc), color=c, label=lab)
    a2.axhline(90, color=AMBER, ls="--", lw=0.9)
    a2.axvspan(50, 60, color=ATINT, lw=0)
    a2.text(70, 140, "50/60 Hz", fontsize=6.5, color=AMBERDK)
    a2.set_xlim(1, 1e5); a2.set_ylim(40, 160)
    finish(a2, xlabel="Frequency (Hz)", ylabel="CMRR limit from input RC mismatch (dB)", legend=True,
           loc="lower left")
    a2.legend(loc="lower left", fontsize=6.3)
    panel(a2, "b")
    savefig(fig, "ch07_ccia")


if __name__ == "__main__":
    for t in (1e-3, 1e-2):
        for g1 in (1, 1.5, 100):
            print("tol", t, "g1", g1, "median CMRR %.1f dB" % np.median(total_cmrr_db(g1, diffamp_cmrr(1.0, t))),
                  "worst (1+G)/(4t)*g1: %.1f" % (20 * np.log10(g1 * 2 / (4 * t))))
    for c in (5e-12, 20e-12, 50e-12):
        a = c / MIM_DENSITY; s = np.sqrt(2) * MIM_AC / np.sqrt(a)
        print("Cin %.0f pF area %.0f um2 sigma %.4f %% CMRR1s %.1f 3s %.1f" % (c * 1e12, a, s * 100, 20 * np.log10(1 / s), 20 * np.log10(1 / (3 * s))))
    print("RC 10k 1pF 50Hz %.1f dB" % (-20 * np.log10(2 * np.pi * 50 * 1e4 * 1e-12)))
    fig_three_opamp()
    fig_ccia()
