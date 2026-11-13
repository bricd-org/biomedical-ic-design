"""ch11_figs.py -- Chapter 11 figure: bias current of a Gm-C filter versus corner frequency, and the
anti-alias filter for the EMG-mode SAR at 2 kS/s with the 4 kHz chopper ripple."""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "labs", "python"))
from bricdstyle import *
import biosig as bs

GMID = 25.0


def fig():
    fig, (a1, a2) = plt.subplots(1, 2, figsize=FULL2)
    fc = np.logspace(-1, 4, 200)
    for c, col in ((10e-12, C1), (50e-12, C3)):
        gm = 2 * np.pi * fc * c
        a1.loglog(fc, gm / GMID * 1e9, color=col, label=f"C = {c*1e12:g} pF")
    a1.axhspan(1e-3, 1e-2, color=ATINT, lw=0)
    a1.text(0.13, 2.2e-3, "junction leakage (pA range)", fontsize=6.5, color=AMBERDK)
    a1.axvline(100, color=MUTED, ls=":", lw=0.7); a1.axvline(1e3, color=MUTED, ls=":", lw=0.7)
    a1.set_xlim(0.1, 1e4); a1.set_ylim(1e-3, 1e3)
    finish(a1, xlabel="Gm-C corner frequency (Hz)", ylabel="Bias current per transconductor (nA)",
           legend=True, loc="upper left")
    panel(a1, "a")
    f = np.logspace(1, 4.5, 400)
    for n, col in ((2, C2), (4, C1)):
        a2.semilogx(f, -bs.butter_atten_db(f, 600.0, n), color=col, label=f"Butterworth order {n} at 600 Hz")
    for x, lab, y in ((1500, "1.5 kHz\nfolds to 500 Hz", -42), (4000, "4 kHz chopper\nripple → DC", -8)):
        a2.axvline(x, color=MUTED, ls=":", lw=0.7)
        a2.text(x * 1.07, y, lab, fontsize=6.3, color=MUTED, va="top")
    a2.axhline(-30, color=AMBER, ls="--", lw=0.8)
    a2.text(12, -28, "30 dB needed at 1.5 kHz", fontsize=6.5, color=AMBERDK, va="bottom")
    a2.axvspan(10, 500, color=BTINT, lw=0)
    a2.set_xlim(10, 3e4); a2.set_ylim(-90, 5)
    finish(a2, xlabel="Frequency (Hz)", ylabel="Filter response (dB)", legend=True, loc="lower left")
    a2.legend(loc="lower left", fontsize=6.3)
    panel(a2, "b")
    savefig(fig, "ch11_filters")


if __name__ == "__main__":
    for c in (10e-12, 50e-12):
        for f0 in (0.5, 100, 1000):
            gm = 2 * np.pi * f0 * c
            print("C %.0f pF f %g Hz: gm %.3g nS, I %.3g nA" % (c * 1e12, f0, gm * 1e9, gm / GMID * 1e9))
    print("ktc 10 pF: %.1f uV; x2 excess: %.1f uV" % (np.sqrt(bs.K_B * 300 / 10e-12) * 1e6, np.sqrt(4 * bs.K_B * 300 / 10e-12) * 1e6))
    for n in (2, 4):
        print("order", n, "at 1.5k: %.1f dB, at 4k: %.1f dB" % (bs.butter_atten_db(1500, 600, n), bs.butter_atten_db(4000, 600, n)))
    print("needed: 20log(0.1mV/3.3uV) = %.1f dB" % (20 * np.log10(0.1e-3 / 3.3e-6)))
    fig()
