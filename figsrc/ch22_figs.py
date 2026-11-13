"""ch22_figs.py -- Chapter 22 figure: spectral leakage of a non-coherent tone with rectangular and Hann
windows against coherent sampling, and DNL of the mismatched 12-bit SAR of Chapter 14 from a sine-wave
histogram (arcsine-corrected) against the ramp histogram."""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "labs", "python"))
from bricdstyle import *
import biosig as bs

N = 12


def sine_hist_dnl(codes, amp_lsb, offset_lsb, nbits):
    """DNL from a sine-wave histogram: compare counts with the arcsine-distributed expectation."""
    h = np.bincount(codes, minlength=2 ** nbits).astype(float)
    k = np.arange(2 ** nbits)
    lo = np.clip((k - 2 ** (nbits - 1) - offset_lsb) / amp_lsb, -1, 1)
    hi = np.clip((k + 1 - 2 ** (nbits - 1) - offset_lsb) / amp_lsb, -1, 1)
    p = (np.arcsin(hi) - np.arcsin(lo)) / np.pi
    sel = (p > 1e-6) & (k > 0) & (k < 2 ** nbits - 1)
    dnl = np.full(len(k), np.nan)
    dnl[sel] = h[sel] / (p[sel] * len(codes)) - 1
    return dnl


def fig():
    fig, (a1, a2) = plt.subplots(1, 2, figsize=FULL2)
    n, fs = 4096, 16e3
    t = np.arange(n) / fs
    fc, m = bs.coherent_tone(1000.0, fs, n)
    for f0, win, c, lab in ((fc, None, C3, "coherent, rectangular"), (1003.7, None, C4, "non-coherent, rectangular"),
                            (1003.7, "hann", C1, "non-coherent, Hann")):
        y = bs.code_to_volts(bs.sar_convert(0.95 * np.sin(2 * np.pi * f0 * t), N), N)
        w = np.ones(n) if win is None else np.hanning(n)
        p = np.abs(np.fft.rfft((y - y.mean()) * w)) ** 2
        p = p / p.max()
        a1.plot(np.fft.rfftfreq(n, 1 / fs), 10 * np.log10(p + 1e-30), color=c, lw=0.6, label=lab)
    a1.set_xlim(0, fs / 2); a1.set_ylim(-150, 5)
    finish(a1, xlabel="Frequency (Hz)", ylabel="Spectrum (dBc)", legend=True, loc="upper right")
    a1.legend(loc="upper right", fontsize=6.0)
    panel(a1, "a")
    w = bs.cdac_weights(N, 0.01, 2)
    r = np.linspace(-1, 1, 2 ** N * 64, endpoint=False) + 1 / 2 ** N / 64
    dnl_r, _ = bs.dnl_inl(bs.sar_convert(r, N, w), N)
    ns = 2 ** 20
    rng = np.random.default_rng(22)
    amp = 1.02
    xs = amp * np.sin(2 * np.pi * rng.uniform(0, 1, ns))
    codes = bs.sar_convert(np.clip(xs, -0.99999, 0.99999), N, w)
    dnl_s = sine_hist_dnl(codes, amp * 2 ** (N - 1), 0.0, N)
    k = np.arange(1, 2 ** N - 1)
    a2.plot(k, dnl_s[1:-1], color=C1, lw=0.5, label=f"sine histogram, {ns/1e6:.1f} M samples")
    a2.plot(k, dnl_r, color=C4, lw=0.5, alpha=0.8, label="ramp histogram (reference)")
    a2.set_xlim(0, 2 ** N); a2.set_ylim(-1.2, 1.8)
    a2.set_xticks([0, 1024, 2048, 3072, 4096])
    finish(a2, xlabel="Output code", ylabel="DNL (LSB)", legend=True, loc="upper right")
    a2.legend(loc="upper right", fontsize=6.0)
    panel(a2, "b")
    savefig(fig, "ch22_testing")
    d = dnl_s[1:-1] - dnl_r
    return np.nanstd(d), np.nanmax(np.abs(dnl_s[1:-1])), np.max(np.abs(dnl_r))


if __name__ == "__main__":
    print("sine-hist DNL error rms %.3f LSB; max |DNL| sine %.2f ramp %.2f" % fig())
    print("expected per-code count at mid-scale for 2^20 samples:", round(2 ** 20 / (np.pi * 2 ** 11 * 1.02), 1))
