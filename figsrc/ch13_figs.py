"""ch13_figs.py -- Chapter 13 figures: aliasing of mains harmonics and the anti-alias filter,
the quantiser and its error, oversampling and clock jitter. Models from labs/python/biosig.py."""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "labs", "python"))
from bricdstyle import *
import biosig as bs


def aliasing():
    fig, (a1, a2) = plt.subplots(1, 2, figsize=FULL2)
    fs = 256.0
    a1.axvspan(0.5, 100, color=BTINT, lw=0)
    a1.text(30, 1.22, "EEG band 0.5–100 Hz", fontsize=7, color=BLUE, ha="center")
    for k in range(1, 11):
        f = 50.0 * k
        fa = float(bs.alias_freq(f, fs))
        inband = k <= 2
        c = C1 if inband else C4
        a1.vlines(fa, 0, 1, color=c, lw=1.4)
        a1.plot(fa, 1, "o", color=c, ms=3.5)
        dy = 0.06 if k % 2 else -0.0
        a1.text(fa, 1.03 + dy, f"{f:.0f}", fontsize=6.5, color=c, ha="center", va="bottom")
    note(a1, (6.8, 0.45), "250 Hz lands\nat 6 Hz (theta)", (64, 0.45), color=C4, fs=7)
    a1.set_xlim(0, 128); a1.set_ylim(0, 1.32); a1.set_yticks([])
    a1.text(127, 1.22, "labels: frequency before sampling", fontsize=6.5, color=MUTED, ha="right")
    finish(a1, xlabel="Frequency after sampling at 256 S/s (Hz)")
    panel(a1, "a")
    f = np.logspace(1, 3.3, 400)
    for n, c in zip((2, 4, 8), (C2, C1, C3)):
        a2.semilogx(f, -bs.butter_atten_db(f, 150.0, n), color=c, label=f"order {n}")
    need = 20 * np.log10(1e-3 / 1.5e-6)
    a2.axhline(-need, color=AMBER, ls="--", lw=1)
    a2.text(12, -need + 2, f"needed: {need:.0f} dB", fontsize=7, color=AMBERDK, va="bottom")
    a2.axvline(350, color=MUTED, lw=0.7, ls=":")
    a2.text(370, -8, "350 Hz\nfolds to 150 Hz", fontsize=6.5, color=MUTED, va="top")
    a2.set_ylim(-80, 5)
    a2.set_xticks([10, 100, 1000]); a2.set_xticklabels(["10", "100", "1k"])
    finish(a2, xlabel="Frequency (Hz)", ylabel="Butterworth response (dB)", legend=True, loc="center left")
    panel(a2, "b")
    savefig(fig, "ch13_alias")


def quantiser():
    fig, (a1, a2) = plt.subplots(1, 2, figsize=FULL2)
    # (a) 3-bit transfer curve and its error, in LSB
    N = 3
    x = np.linspace(-4.6, 4.6, 2000)                       # input in LSB (full scale = +-4 LSB)
    q = bs.quantize(x, N, vfs=4.0)
    a1.plot(x, x, color=MUTED, lw=0.8, ls="--", label="ideal line")
    a1.plot(x, q, color=C1, lw=1.3, label="3-bit output")
    a1.plot(x, (q - x) - 6.0, color=C4, lw=1.0, label="error (offset by −6)")
    a1.axhline(-6.5, color=C4, lw=0.4, ls=":"); a1.axhline(-5.5, color=C4, lw=0.4, ls=":")
    a1.set_xlim(-4.6, 4.6); a1.set_ylim(-7.2, 5)
    finish(a1, xlabel="Input (LSB)", ylabel="Output (LSB)", legend=True, loc="upper left")
    panel(a1, "a")
    # (b) a 1.3-LSB sine on a 12-bit quantiser, with and without dither
    n, fsamp = 8192, 1000.0
    f, m = bs.coherent_tone(37.0, fsamp, n)
    t = np.arange(n) / fsamp
    lsb = 2.0 / 2 ** 12
    s = 1.3 * lsb * np.sin(2 * np.pi * f * t) + 0.31 * lsb        # small sine, slightly off a code edge
    rng = np.random.default_rng(13)
    tpdf = (rng.uniform(-0.5, 0.5, n) + rng.uniform(-0.5, 0.5, n)) * lsb     # triangular, 1 LSB pp each
    win = np.hanning(n)
    for y, c, lab in ((bs.quantize(s, 12), C4, "no dither"), (bs.quantize(s + tpdf, 12), C1, "triangular dither")):
        p = np.abs(np.fft.rfft((y - y.mean()) * win)) ** 2
        p = p / (np.abs(np.fft.rfft(np.sin(2 * np.pi * f * t) * win)) ** 2).max()   # dB re full-scale sine
        a2.plot(np.fft.rfftfreq(n, 1 / fsamp), 10 * np.log10(p + 1e-30), color=c, lw=0.6, label=lab,
                alpha=0.9 if c == C4 else 0.75)
    a2.set_xlim(0, 500); a2.set_ylim(-160, -50)
    finish(a2, xlabel="Frequency (Hz)", ylabel="Spectrum (dBFS)", legend=True, loc="upper right")
    panel(a2, "b")
    savefig(fig, "ch13_quant")


def oversampling_jitter():
    fig, (a1, a2) = plt.subplots(1, 2, figsize=FULL2)
    osr = 2.0 ** np.arange(0, 9)
    for L, c, ls, lab in ((0, C1, "-", "plain oversampling (+3 dB/octave)"),
                          (1, C2, "--", "1st-order shaping (+9 dB/octave)"),
                          (2, C3, "--", "2nd-order shaping (+15 dB/octave)")):
        a1.semilogx(osr, bs.sqnr_os_db(8, osr, L), color=c, ls=ls, label=lab, base=2)
    # simulated: 8-bit quantiser, near-full-scale sine, ideal brick-wall decimation filter
    n = 2 ** 16
    m = 17
    t = np.arange(n)
    y = bs.quantize(0.999 * np.sin(2 * np.pi * m * t / n + 0.3), 8)
    sim = [bs.tone_metrics(y, m, band_bins=int(n / 2 / r))["sndr"] for r in osr]
    a1.plot(osr, sim, "o", color=C1, ms=3.5, label="simulated, 8-bit")
    a1.set_xticks(osr); a1.set_xticklabels([f"{int(r)}" for r in osr])
    a1.set_ylim(40, 150)
    finish(a1, xlabel="Oversampling ratio", ylabel="In-band SQNR (dB)", legend=True, loc="upper left")
    panel(a1, "a")
    f = np.logspace(0, 4.2, 300)
    a2.axvspan(0.5, 1000, color=BTINT, lw=0)
    a2.axvspan(1000, 7000, color=BGPALE, lw=0)
    a2.text(25, 52, "ExG band", fontsize=7, color=BLUE, ha="center")
    a2.text(2600, 52, "spikes", fontsize=7, color=MUTED, ha="center")
    for st, c, lab in ((10e-9, C4, "10 ns"), (1e-9, C1, "1 ns"), (100e-12, C3, "100 ps")):
        a2.semilogx(f, bs.jitter_snr_db(f, st), color=c, label=r"$\sigma_t$ = " + lab)
    for nb in (12, 16):
        a2.axhline(bs.sqnr_ideal_db(nb), color=AMBER, ls="--", lw=0.9)
        a2.text(1.3, bs.sqnr_ideal_db(nb) + 1.5, f"ideal {nb} bit", fontsize=7, color=AMBERDK, va="bottom")
    a2.set_xlim(1, 1.6e4); a2.set_ylim(45, 180)
    a2.set_xticks([1, 10, 100, 1e3, 1e4]); a2.set_xticklabels(["1", "10", "100", "1k", "10k"])
    finish(a2, xlabel="Input frequency (Hz)", ylabel="Jitter-limited SNR (dB)", legend=True, loc="upper right")
    panel(a2, "b")
    savefig(fig, "ch13_os_jitter")


if __name__ == "__main__":
    aliasing()
    quantiser()
    oversampling_jitter()
