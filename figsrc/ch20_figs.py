"""ch20_figs.py -- Chapter 20 figure: integrator swings of the second-order incremental modulator
(a1 = a2 = 0.5) versus DC input, and the frequency response of its cascade-of-integrators decimator
against sinc filters of the same length."""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "labs", "python"))
from bricdstyle import *
import biosig as bs

M = 1024
FCLK = 512e3


def swings(u_dc, m=M, a1=0.5, a2=0.5):
    u = np.atleast_1d(u_dc).astype(float)
    x1 = np.zeros_like(u); x2 = np.zeros_like(u)
    m1 = np.zeros_like(u); m2 = np.zeros_like(u)
    for _ in range(m):
        v = np.where(x2 >= 0, 1.0, -1.0)
        x2 = x2 + a2 * (x1 - v)
        x1 = x1 + a1 * (u - v)
        m1 = np.maximum(m1, np.abs(x1)); m2 = np.maximum(m2, np.abs(x2))
    return m1, m2


def response(w, f):
    n = np.arange(len(w))
    h = np.abs(np.exp(-2j * np.pi * np.outer(f, n) / FCLK) @ w)
    return h / w.sum()


def fig():
    fig, (a1, a2) = plt.subplots(1, 2, figsize=FULL2)
    u = np.linspace(-0.95, 0.95, 191)
    m1, m2 = swings(u)
    a1.plot(u, m1, color=C1, label=r"first integrator $|x_1|_\mathrm{max}$")
    a1.plot(u, m2, color=C4, label=r"second integrator $|x_2|_\mathrm{max}$")
    a1.axvspan(-0.8, 0.8, color=BTINT, lw=0)
    a1.text(0, 0.15, "input range ±0.8", fontsize=6.5, color=BLUE, ha="center")
    a1.set_xlim(-1, 1); a1.set_ylim(0, 3)
    finish(a1, xlabel="DC input (fraction of reference)", ylabel="Peak integrator state (× reference)",
           legend=True, loc="upper center")
    a1.legend(loc="upper center", fontsize=6.3)
    panel(a1, "a")
    f = np.logspace(1, np.log10(2e4), 1500)
    coi = (M - 1 - np.arange(M)).astype(float)
    sinc1 = np.ones(M)
    sinc2 = np.convolve(np.ones(M // 2), np.ones(M // 2))
    for w, c, lab in ((sinc1, C2, "sinc (boxcar), 1024 taps"), (sinc2, C3, "sinc², 1024 taps"), (coi, C1, "CoI ramp (incremental)")):
        a2.semilogx(f, 20 * np.log10(response(w, f) + 1e-12), color=c, lw=0.9, label=lab)
    a2.axvline(4e3, color=MUTED, ls=":", lw=0.8)
    a2.text(4.3e3, -8, "4 kHz\nchopper", fontsize=6.5, color=MUTED, va="top")
    a2.axvspan(10, 150, color=BTINT, lw=0)
    a2.set_xlim(10, 2e4); a2.set_ylim(-90, 5)
    finish(a2, xlabel="Frequency (Hz)", ylabel="Decimator response (dB)", legend=True, loc="lower left")
    a2.legend(loc="lower left", fontsize=6.0)
    panel(a2, "b")
    savefig(fig, "ch20_incremental")


if __name__ == "__main__":
    m1, m2 = swings(np.linspace(-0.8, 0.8, 161))
    print("max |x1| %.2f, |x2| %.2f over +-0.8" % (m1.max(), m2.max()))
    f = np.array([150.0, 500.0, 4000.0])
    coi = (M - 1 - np.arange(M)).astype(float)
    print("CoI response at 150/500/4000 Hz (dB):", np.round(20 * np.log10(response(coi, f)), 1), " 1/(8 pi) =", round(20 * np.log10(1 / (8 * np.pi)), 1))
    kt = bs.K_B * 300
    cs = 16 * kt / (3 * M * (1.0 / 65536 / np.sqrt(12)) ** 2)
    print("Cs for 16b over 1 V with CoI averaging: %.2f pF" % (cs * 1e12))
    gbw = 1 / (2 * np.pi * (1 / FCLK / 2 / 5)) / 0.67
    print("GBW for 1%% settling in half period: %.2f MHz; gm on 2.5 pF %.1f uS; I at gm/ID 20: %.2f uA" % (gbw / 1e6, 2 * np.pi * gbw * 2.5e-12 * 1e6, 2 * np.pi * gbw * 2.5e-12 / 20 * 1e6))
    print("CoI word length: log2(M(M-1)/2) = %.1f bits" % np.log2(M * (M - 1) / 2))
    fig()
