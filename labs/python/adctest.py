"""adctest.py -- spectral and histogram tests for any ADC (Lab 6; reused by Labs 8 and 10).

Import it:
    from adctest import sine_test, ramp_histogram, sine_histogram
    met = sine_test(y, m=None, window="hann")      # SNDR, SNR, THD, SFDR, ENOB of a sine record
    dnl, inl = ramp_histogram(codes, nbits)        # from a slow uniform ramp
    dnl, inl, (amp, off) = sine_histogram(codes, nbits)   # from a sine, amplitude estimated

or run it as Lab 6 (Chapters 13, 14 and 22):
    python adctest.py                 # ideal and mismatched 12-bit SAR, windows, histograms, sigma sweep
    python adctest.py --sigma 0.005   # another unit-capacitor mismatch

The SAR model is biosig.sar_convert() with biosig.cdac_weights(); replace it by your own
converter (behavioural, or codes exported from an ngspice run) to test that instead.
"""
import argparse
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import biosig  # noqa: E402

OUT = os.path.join(HERE, "out")

# Window: (function of n, half-width of the main lobe in bins that holds the tone's power)
WINDOWS = {
    "rect": (np.ones, 0),
    "hann": (np.hanning, 2),
    "bh4": (lambda n: (0.35875 - 0.48829 * np.cos(2 * np.pi * np.arange(n) / n)
                       + 0.14128 * np.cos(4 * np.pi * np.arange(n) / n)
                       - 0.01168 * np.cos(6 * np.pi * np.arange(n) / n)), 4),
}


def sine_test(y, m=None, window="rect", n_harm=5, band_bins=None, half=None):
    """SNDR, SNR, THD, SFDR (dB) and ENOB of a sine record y.
    m: the tone's bin if the record is coherent (then use window="rect"); None finds the largest bin.
    window: "rect", "hann" or "bh4" (4-term Blackman-Harris) for non-coherent records; the tone's
    and each harmonic's power is summed over `half` bins either side (default: the main lobe;
    Hann's slowly falling skirt needs ~30 bins at 12 bits). band_bins limits the noise sum
    (oversampled converters: band_bins = n / (2 * OSR))."""
    y = np.asarray(y, float)
    n = len(y)
    wf, half0 = WINDOWS[window]
    half = half0 if half is None else half
    p = np.abs(np.fft.rfft((y - y.mean()) * wf(n))) ** 2
    p[: half + 1] = 0.0                                   # DC and its window skirt
    top = len(p) - 1 if band_bins is None else band_bins
    if m is None:
        m = int(np.argmax(p[1:top + 1])) + 1
    if window == "rect" and m is not None:
        met = biosig.tone_metrics(y, m, n_harm, band_bins)
    else:
        def lobe(k):
            return slice(max(1, k - half), min(len(p), k + half + 1))
        used = np.zeros(len(p), bool)
        ps = p[lobe(m)].sum(); used[lobe(m)] = True
        ph = 0.0
        for h in range(2, n_harm + 2):
            k = h * m % n
            k = min(k, n - k)
            if 0 < k <= top and not used[k]:
                ph += p[lobe(k)].sum(); used[lobe(k)] = True
        band = np.zeros(len(p), bool); band[1:top + 1] = True
        pn = p[band & ~used].sum() * (band.sum() / max(1, (band & ~used).sum()))  # fill the lobes
        spur = max(p[band & ~np.isin(np.arange(len(p)), np.arange(len(p))[lobe(m)])].max(), 1e-300)
        met = dict(sndr=10 * np.log10(ps / (pn + ph)), snr=10 * np.log10(ps / pn),
                   thd=10 * np.log10(ph / ps) if ph > 0 else -np.inf, sfdr=10 * np.log10(ps / spur))
    met["enob"] = float(biosig.enob(met["sndr"]))
    return met


def ramp_histogram(codes, nbits):
    """DNL and INL (LSB, end-point fit) from a slow uniform ramp; end codes dropped."""
    return biosig.dnl_inl(codes, nbits)


def sine_histogram(codes, nbits):
    """DNL and INL (LSB) from a sine-wave histogram (IEEE 1241 style). The sine must overdrive
    both end codes slightly; its amplitude and offset are estimated from the end-code counts."""
    codes = np.asarray(codes, int)
    ntot = len(codes)
    h = np.bincount(codes, minlength=2 ** nbits).astype(float)
    half = 2 ** (nbits - 1)
    t_lo, t_hi = 1 - half, half - 1                      # first and last transition, LSB from mid-scale
    c_lo, c_hi = np.cos(np.pi * h[0] / ntot), np.cos(np.pi * h[-1] / ntot)
    amp = (t_hi - t_lo) / (c_lo + c_hi)
    off = t_hi - amp * c_hi
    k = np.arange(2 ** nbits)
    lo = np.clip((k - half - off) / amp, -1, 1)
    hi = np.clip((k + 1 - half - off) / amp, -1, 1)
    pk = (np.arcsin(hi) - np.arcsin(lo)) / np.pi
    dnl = h[1:-1] / (pk[1:-1] * ntot) - 1.0
    inl = np.cumsum(dnl)
    inl = inl - np.linspace(inl[0], inl[-1], len(inl))
    return dnl, inl, (amp, off)


def _ramp_codes(nbits, w, per_code=64):
    r = np.linspace(-1, 1, 2 ** nbits * per_code, endpoint=False) + 1.0 / 2 ** nbits / per_code
    return biosig.sar_convert(r, nbits, w)


def main():
    ap = argparse.ArgumentParser(description="Lab 6: ideal ADC and spectral testing")
    ap.add_argument("--bits", type=int, default=12)
    ap.add_argument("--sigma", type=float, default=0.01, help="unit-capacitor mismatch (relative rms)")
    ap.add_argument("--seed", type=int, default=2)
    args = ap.parse_args()
    nb, fs, n = args.bits, 2000.0, 8192
    os.makedirs(OUT, exist_ok=True)
    w = biosig.cdac_weights(nb, args.sigma, args.seed)
    lines = []

    def say(s=""):
        print(s)
        lines.append(s)

    # 1. Coherent sampling: ideal and mismatched converter (Worked Example 14.1)
    f, m = biosig.coherent_tone(97.0, fs, n)
    t = np.arange(n) / fs
    x = 0.99 * np.sin(2 * np.pi * f * t)
    say(f"1. Coherent test, {n} points, tone {f:.3f} Hz (bin {m}), -0.09 dBFS; ideal SQNR {biosig.sqnr_ideal_db(nb):.1f} dB")
    for lab, wt in (("ideal", None), (f"sigma_u = {args.sigma*100:g} %", w)):
        met = sine_test(biosig.code_to_volts(biosig.sar_convert(x, nb, wt), nb), m)
        say(f"   {lab:>16}: SNDR {met['sndr']:5.1f} dB  ENOB {met['enob']:5.2f}  SFDR {met['sfdr']:5.1f} dB  THD {met['thd']:6.1f} dB")

    # 2. Non-coherent sampling and windows (Chapter 22)
    say("2. Non-coherent tone (97.37 Hz), ideal converter:")
    xn = 0.99 * np.sin(2 * np.pi * 97.37 * t)
    yn = biosig.code_to_volts(biosig.sar_convert(xn, nb), nb)
    for win, hb in (("rect", None), ("hann", None), ("hann", 30), ("bh4", None)):
        met = sine_test(yn, None, win, half=hb)
        hb = WINDOWS[win][1] if hb is None else hb
        say(f"   {win:>5}, tone +-{hb:>2} bins: SNDR {met['sndr']:5.1f} dB  SFDR {met['sfdr']:5.1f} dB")

    # 3. Ramp histogram
    dnl, inl = ramp_histogram(_ramp_codes(nb, w), nb)
    say(f"3. Ramp histogram (64 hits/code): DNL {dnl.min():+.2f} .. {dnl.max():+.2f} LSB, "
        f"INL {inl.min():+.2f} .. {inl.max():+.2f} LSB, missing codes {int(np.sum(dnl <= -0.99))}")

    # 4. Sine histogram with estimated amplitude and offset
    ns = 2 ** 20
    rng = np.random.default_rng(22)
    xs = 1.02 * np.sin(2 * np.pi * rng.uniform(0, 1, ns)) + 0.003
    codes = biosig.sar_convert(np.clip(xs, -0.99999, 0.99999), nb, w)
    dnl_s, inl_s, (amp, off) = sine_histogram(codes, nb)
    say(f"4. Sine histogram, {ns} samples: amplitude {amp/2**(nb-1):.4f} FS (true 1.0200), offset {off:+.1f} LSB "
        f"(true {0.003*2**(nb-1):+.1f}); DNL rms difference from the ramp {np.std(dnl_s - dnl):.3f} LSB")

    # 5. Sweep the mismatch: where do missing codes start?
    say("5. Mismatch sweep (10 seeds each): ENOB and worst DNL, mean over seeds")
    for s in (0.001, 0.002, 0.005, 0.01, 0.02):
        en, dmin, miss = [], [], 0
        for sd in range(10):
            ws = biosig.cdac_weights(nb, s, sd)
            en.append(sine_test(biosig.code_to_volts(biosig.sar_convert(x, nb, ws), nb), m)["enob"])
            d, _ = ramp_histogram(_ramp_codes(nb, ws, 16), nb)
            dmin.append(d.min()); miss += int(np.any(d <= -0.99))
        say(f"   sigma_u {s*100:4.1f} %: ENOB {np.mean(en):5.2f}, DNL min {np.mean(dmin):+.2f} LSB, "
            f"{miss}/10 converters with a missing code")

    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        fig, (a1, a2) = plt.subplots(1, 2, figsize=(11, 4.2), constrained_layout=True)
        y = biosig.code_to_volts(biosig.sar_convert(x, nb, w), nb)
        p = np.abs(np.fft.rfft(y - y.mean())) ** 2
        a1.plot(np.fft.rfftfreq(n, 1 / fs), 10 * np.log10(p / p[m] + 1e-30), lw=0.5)
        a1.set(xlabel="frequency (Hz)", ylabel="dBc", ylim=(-140, 5), title=f"(a) coherent spectrum, sigma_u {args.sigma*100:g} %")
        k = np.arange(1, 2 ** nb - 1)
        a2.plot(k, dnl, lw=0.5, label="DNL (ramp)")
        a2.plot(k, dnl_s, lw=0.4, alpha=0.6, label="DNL (sine histogram)")
        a2.plot(k, inl, lw=1.2, label="INL (ramp)")
        a2.set(xlabel="output code", ylabel="LSB", title="(b) DNL and INL")
        a2.legend(fontsize=8)
        fig.savefig(os.path.join(OUT, "lab6_adctest.png"), dpi=130)
        say(f"\nwrote {os.path.join(OUT, 'lab6_adctest.png')}")
    except ImportError:
        pass
    with open(os.path.join(OUT, "lab6_summary.txt"), "w") as fh:
        fh.write("\n".join(lines) + "\n")


if __name__ == "__main__":
    main()
