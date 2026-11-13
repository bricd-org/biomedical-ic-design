"""ch19_figs.py -- Chapter 19 figures: noise transfer functions and a shaped spectrum, SQNR versus
OSR and input amplitude, idle tones and incremental resolution. Models from labs/python/biosig.py
(simulate_dsm is a 1-bit error-feedback loop; same output as any topology with the same NTF)."""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "labs", "python"))
from bricdstyle import *
import biosig as bs

M_BIN = 13                       # tone bin


def tone(n, amp):
    return amp * np.sin(2 * np.pi * M_BIN * np.arange(n) / n)


def ntf_and_spectrum():
    fig, (a1, a2) = plt.subplots(1, 2, figsize=FULL2)
    f = np.logspace(-4, np.log10(0.5), 500)
    for L, c in ((1, C2), (2, C1), (3, C4)):
        a1.loglog(f, bs.ntf_response(*bs.ntf_pure(L), f), color=c, label=f"$(1-z^{{-1}})^{L}$")
    b, a = bs.synth_ntf(3, 128, opt_zeros=True)
    a1.loglog(f, bs.ntf_response(b, a, f), color=C3, lw=1.6, label="3rd order, ‖NTF‖∞ = 1.5")
    a1.axvline(1 / 256, color=MUTED, lw=0.7, ls=":")
    a1.text(1 / 256 * 1.15, 1.6e-8, "band edge\nat OSR 128", fontsize=6.5, color=MUTED)
    a1.set_ylim(1e-8, 20); a1.set_xlim(1e-4, 0.5)
    finish(a1, xlabel=r"Frequency $f/f_\mathrm{s}$", ylabel="|NTF|", legend=True, loc="upper left")
    a1.legend(loc="upper left", fontsize=6.3)
    panel(a1, "a")
    n = 2 ** 16
    v, _ = bs.simulate_dsm(tone(n, 0.5), *bs.ntf_pure(2))
    w = np.hanning(n) ** 2
    p = np.abs(np.fft.rfft(v * w)) ** 2
    ref = (np.sum(w) / 2) ** 2                      # full-scale sine (amplitude 1) peak
    fr = np.arange(len(p)) / n
    a2.semilogx(fr[1:], 10 * np.log10(p[1:] / ref + 1e-30), color=C1, lw=0.4)
    ff = np.array([3e-4, 3e-2])
    nbw = 1.94 / n                                     # Hann^2 noise bandwidth (fraction of fs)
    a2.semilogx(ff, 10 * np.log10((2 / 3) * nbw * (2 * np.pi * ff) ** 4) + 0, color=AMBER, ls="--", lw=1)
    a2.text(1.2e-3, -165, "+40 dB/decade", fontsize=7, color=AMBERDK, rotation=0)
    a2.axvline(1 / 256, color=MUTED, lw=0.7, ls=":")
    a2.set_xlim(1e-4, 0.5); a2.set_ylim(-200, 5)
    finish(a2, xlabel=r"Frequency $f/f_\mathrm{s}$", ylabel="Output spectrum (dBFS)")
    panel(a2, "b")
    savefig(fig, "ch19_ntf")


def sqnr_curves():
    fig, (a1, a2) = plt.subplots(1, 2, figsize=FULL2)
    osrs = np.array([16, 32, 64, 128, 256])
    n = 2 ** 17
    u = tone(n, 0.5)
    sim = {}
    for L in (1, 2):
        v, _ = bs.simulate_dsm(u, *bs.ntf_pure(L))
        sim[L] = [bs.dsm_sqnr(v, M_BIN, o) for o in osrs]
    for L in (3, 4):
        vals = []
        for o in osrs:
            v, ok = bs.simulate_dsm(u, *bs.synth_ntf(L, o, opt_zeros=True))
            vals.append(bs.dsm_sqnr(v, M_BIN, o) if ok else np.nan)
        sim[L] = vals
    cols = {1: C2, 2: C1, 3: C3, 4: C5}
    for L in (1, 2, 3, 4):
        lab = f"L = {L}" + (" (pure)" if L < 3 else ", ‖NTF‖∞ = 1.5")
        a1.semilogx(osrs, sim[L], "o-", color=cols[L], ms=3, label=lab, base=2)
    for L in (1, 2):
        a1.semilogx(osrs, bs.sqnr_os_db(1, osrs, L) - 6.02, color=cols[L], ls=":", lw=1, base=2)
    a1.axhline(108, color=AMBER, ls="--", lw=0.9)
    a1.text(17, 110, "target 108 dB", fontsize=7, color=AMBERDK, va="bottom")
    a1.set_xticks(osrs); a1.set_xticklabels([str(o) for o in osrs])
    a1.set_ylim(0, 150)
    finish(a1, xlabel="Oversampling ratio", ylabel="SQNR at −6 dBFS (dB)", legend=True, loc="lower right")
    a1.legend(loc="lower right", fontsize=6.3)
    panel(a1, "a")
    amps_db = np.arange(-60, 1, 4.0)
    n = 2 ** 16
    for name, (b, a), c in (("L = 2 (pure)", bs.ntf_pure(2), C1),
                            ("L = 3, ‖NTF‖∞ = 1.5", bs.synth_ntf(3, 128, opt_zeros=True), C3),
                            ("L = 4, ‖NTF‖∞ = 1.5", bs.synth_ntf(4, 128, opt_zeros=True), C5)):
        xs, ys, bad = [], [], None
        for adb in amps_db:
            v, ok = bs.simulate_dsm(tone(n, 10 ** (adb / 20)), b, a)
            if not ok:
                bad = adb
                break
            xs.append(adb); ys.append(bs.dsm_sqnr(v, M_BIN, 128))
        a2.plot(xs, ys, "o-", color=c, ms=2.8, label=name)
        if bad is not None:
            a2.plot(bad, ys[-1], "x", color=c, ms=6, mew=1.5)
    a2.text(-58, 128, "× : loop unstable", fontsize=6.5, color=MUTED)
    a2.set_xlim(-62, 2); a2.set_ylim(20, 140)
    finish(a2, xlabel="Input amplitude (dBFS)", ylabel="SQNR at OSR 128 (dB)", legend=True, loc="lower right")
    a2.legend(loc="lower right", fontsize=6.3)
    panel(a2, "b")
    savefig(fig, "ch19_sqnr")


def tones_incremental():
    fig, (a1, a2) = plt.subplots(1, 2, figsize=FULL2)
    n = 2 ** 16
    dc = 0.002 * np.ones(n)
    w = np.hanning(n) ** 2
    ref = (np.sum(w) / 2) ** 2
    fr = np.arange(n // 2 + 1) / n
    v1, _ = bs.simulate_dsm(dc, *bs.ntf_pure(1))
    rng = np.random.default_rng(19)
    v2, _ = bs.simulate_dsm(dc, *bs.ntf_pure(2), dither=rng.uniform(-0.25, 0.25, n))
    for v, c, lab, al in ((v1, C4, "1st order, DC input 0.002", 1.0), (v2, C1, "2nd order + dither, same input", 0.8)):
        p = np.abs(np.fft.rfft((v - v.mean()) * w)) ** 2
        a1.semilogx(fr[1:], 10 * np.log10(p[1:] / ref + 1e-30), color=c, lw=0.5, label=lab, alpha=al)
    a1.axvline(1 / 256, color=MUTED, lw=0.7, ls=":")
    a1.text(1 / 256 * 1.1, -40, "band edge\n(OSR 128)", fontsize=6.5, color=MUTED, va="top")
    a1.set_xlim(1e-4, 0.5); a1.set_ylim(-200, 0)
    finish(a1, xlabel=r"Frequency $f/f_\mathrm{s}$", ylabel="Output spectrum (dBFS)", legend=True, loc="lower right")
    a1.legend(loc="lower right", fontsize=6.3)
    panel(a1, "a")
    ms = np.array([64, 128, 256, 512, 768, 1024, 1536, 2048])
    ud = np.linspace(-0.8, 0.8, 8001)
    worst, rms = [], []
    for M in ms:
        err = bs.incremental2(ud, M) - ud
        worst.append(np.log2(1 / np.abs(err).max()))
        rms.append(np.log2(2 / (np.sqrt(12) * err.std())))
    a2.semilogx(ms, np.log2(ms), "o-", color=C2, ms=3, base=2, label=r"1st order: $\log_2 M$")
    a2.semilogx(ms, worst, "o-", color=C1, ms=3, base=2, label="2nd order, worst-case error")
    a2.semilogx(ms, rms, "o--", color=C1, ms=3, base=2, lw=1, label="2nd order, rms error")
    a2.axhline(16, color=AMBER, ls="--", lw=0.9)
    a2.text(70, 16.3, "16 bits", fontsize=7, color=AMBERDK, va="bottom")
    tk = [64, 128, 256, 512, 1024, 2048]
    a2.set_xticks(tk); a2.set_xticklabels([str(m) for m in tk])
    a2.set_ylim(5, 21)
    finish(a2, xlabel="Cycles per conversion M", ylabel="Resolution (bits)", legend=True, loc="upper left")
    a2.legend(loc="upper left", fontsize=6.3)
    panel(a2, "b")
    savefig(fig, "ch19_tones_incr")


if __name__ == "__main__":
    ntf_and_spectrum()
    sqnr_curves()
    tones_incremental()
