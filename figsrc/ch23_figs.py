"""ch23_figs.py -- Chapter 23 figure: ST-segment distortion by a causal high-pass filter against zero-phase
filtering, and the output SNR of a fixed-point 4th-order low-pass versus word length, direct form against
second-order sections."""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "labs", "python"))
from bricdstyle import *
import biosig as bs
from scipy import signal as sps

FS = 500.0


def quant(x, frac):
    s = 2.0 ** frac
    return np.round(x * s) / s


def fixed_df(b, a, x, bits):
    """Direct-form I IIR in fixed point: coefficients and products rounded to `bits` fractional bits."""
    bq, aq = quant(b, bits - 4), quant(a, bits - 4)        # 4 integer bits for coefficients up to +-8
    y = np.zeros_like(x); xs = np.zeros(len(b)); ys = np.zeros(len(a) - 1)
    for n, xn in enumerate(x):
        xs = np.r_[xn, xs[:-1]]
        acc = bq @ xs - aq[1:] @ ys
        yn = quant(acc, bits - 2)
        if not np.isfinite(yn) or abs(yn) > 1e3:
            y[n:] = np.nan; break
        ys = np.r_[yn, ys[:-1]]; y[n] = yn
    return y


def fixed_sos(sos, x, bits):
    y = x.copy()
    for sec in sos:
        y = fixed_df(sec[:3], sec[3:], y, bits)
    return y


def fig():
    fig, (a1, a2) = plt.subplots(1, 2, figsize=FULL2)
    t, x, pk = bs.ecg(fs=FS, duration=10.0, hr=60, hrv=0.0, seed=23)
    st = np.zeros_like(t)
    for r in pk:
        st[(t > r + 0.04) & (t < r + 0.20)] = 0.15e-3                        # 0.15 mV ST elevation
    xe = x + st
    b, a = sps.butter(1, 0.5 / (FS / 2), "high")
    causal = sps.lfilter(b, a, xe)
    zero = sps.filtfilt(b, a, xe)
    sel = (t > 6.8) & (t < 8.2)
    a1.plot(t[sel], xe[sel] * 1e3, color=PALE, lw=2.0, label="ECG with 0.15 mV ST elevation")
    a1.plot(t[sel], causal[sel] * 1e3, color=C4, lw=1.0, label="causal 1st-order high-pass, 0.5 Hz")
    a1.plot(t[sel], zero[sel] * 1e3, color=C1, lw=1.0, ls="--", label="zero-phase (forward–backward)")
    a1.set_xlim(6.8, 8.2)
    finish(a1, xlabel="Time (s)", ylabel="ECG (mV)", legend=True, loc="upper right")
    a1.legend(loc="upper right", fontsize=6.0)
    panel(a1, "a")
    rng = np.random.default_rng(3)
    xin = 0.4 * rng.standard_normal(20000) / 3
    b4, a4 = sps.butter(4, 0.5 / (FS / 2), "high")                     # baseline-wander high-pass
    sos = sps.butter(4, 0.5 / (FS / 2), "high", output="sos")
    ref = sps.lfilter(b4, a4, xin)
    bits = np.arange(8, 33, 2)
    for kind, c in (("direct form", C4), ("second-order sections", C1)):
        snr = []
        for B in bits:
            y = fixed_df(b4, a4, xin, B) if kind == "direct form" else fixed_sos(sos, xin, B)
            e = y - ref
            snr.append(10 * np.log10(np.var(ref) / np.var(e)) if np.all(np.isfinite(e)) else np.nan)
        a2.plot(bits, snr, "o-", color=c, ms=3, label=kind)
    a2.axhline(74, color=AMBER, ls="--", lw=0.8); a2.text(8.2, 76, "12-bit ADC (74 dB)", fontsize=6.5, color=AMBERDK)
    a2.axhline(98, color=AMBER, ls=":", lw=0.8); a2.text(8.2, 100, "16-bit ADC (98 dB)", fontsize=6.5, color=AMBERDK)
    a2.set_xlim(7, 33); a2.set_ylim(0, 150)
    finish(a2, xlabel="Word length (bits)", ylabel="Output SNR vs floating point (dB)", legend=True, loc="lower right")
    panel(a2, "b")
    savefig(fig, "ch23_dsp")


if __name__ == "__main__":
    fig()
    t, x, pk = bs.ecg(fs=FS, duration=10.0, hr=60, hrv=0.0, seed=23)
    st = np.zeros_like(t)
    for r in pk:
        st[(t > r + 0.04) & (t < r + 0.20)] = 0.15e-3
    for fc in (0.5, 0.05):
        b, a = sps.butter(1, fc / (FS / 2), "high")
        for name, y in (("causal", sps.lfilter(b, a, x + st)), ("zero-phase", sps.filtfilt(b, a, x + st))):
            lv = []
            for r in pk[3:-1]:
                stv = y[(t > r + 0.08) & (t < r + 0.12)].mean(); base = y[(t > r - 0.12) & (t < r - 0.08)].mean()
                lv.append(stv - base)
            print("fc %.2f %s: ST (vs PR baseline) %.3f mV (true 0.150)" % (fc, name, np.mean(lv) * 1e3))
