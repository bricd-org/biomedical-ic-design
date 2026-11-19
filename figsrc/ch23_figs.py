"""ch23_figs.py -- Chapter 23 figures.

Figure 23.1 (ch23_dsp.svg): ST-segment distortion by a causal high-pass filter against zero-phase filtering,
and the output SNR of a fixed-point 4th-order high-pass versus word length, direct form against
second-order sections.
Figure 23.2 (ch23_fir_iir.svg): group delay of linear-phase FIR filters against an IIR band-pass for
monitoring ECG (0.5-40 Hz at 500 S/s), and what each does to an ECG beat with ST elevation.
Figure 23.3 (ch23_notch.svg): a second-order 50 Hz notch at 500 S/s for several pole radii r: magnitude
around 50 Hz against the mains drift, and the ringing after a 1 mV step artefact.

Run with no argument to redraw all three and print the numbers quoted in the chapter.
"""
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


def st_ecg(duration=20.0, st_mv=0.15):
    """Synthetic ECG (60 beats/min) with an ST elevation from R+40 ms to R+200 ms."""
    t, x, pk = bs.ecg(fs=FS, duration=duration, hr=60, hrv=0.0, seed=23)
    st = np.zeros_like(t)
    for r in pk:
        st[(t > r + 0.04) & (t < r + 0.20)] = st_mv * 1e-3
    return t, x + st, pk


def st_level(t, y, beats):
    """Mean ST level (R+80..120 ms) relative to the PR baseline (R-120..-80 ms), in mV."""
    return np.mean([y[(t > r + 0.08) & (t < r + 0.12)].mean() - y[(t > r - 0.12) & (t < r - 0.08)].mean()
                    for r in beats]) * 1e3


def fir_bp(a_db=40.0, df=0.5, band=(0.5, 40.0), fs=FS):
    """Linear-phase (type I) Kaiser-window FIR band-pass; taps from Kaiser's estimate (scipy kaiserord)."""
    n, beta = sps.kaiserord(a_db, df / (fs / 2))
    n += 1 - n % 2                                                  # odd length: type I, integer delay
    return sps.firwin(n, list(band), window=("kaiser", beta), pass_zero=False, fs=fs)


def fir_lp(a_db=40.0, df=10.0, fc=40.0, fs=FS):
    n, beta = sps.kaiserord(a_db, df / (fs / 2))
    n += 1 - n % 2
    return sps.firwin(n, fc, window=("kaiser", beta), fs=fs)


def fig_fir_iir():
    """Figure 23.2: group delay, FIR against IIR, and the ST segment through each."""
    fig, (a1, a2) = plt.subplots(1, 2, figsize=FULL2)
    h_bp, h_lp = fir_bp(), fir_lp()
    b, a = sps.butter(2, [0.5, 40.0], btype="band", fs=FS)          # 4th-order IIR band-pass
    sos = sps.butter(2, [0.5, 40.0], btype="band", fs=FS, output="sos")
    f = np.logspace(-1, 2, 600)
    _, gd = sps.group_delay((b, a), w=f, fs=FS)
    d_bp, d_lp = (len(h_bp) - 1) / 2 / FS, (len(h_lp) - 1) / 2 / FS
    a1.loglog(f, np.full_like(f, d_bp * 1e3), color=C1, label="FIR band-pass 0.5–40 Hz, %d taps" % len(h_bp))
    a1.loglog(f, np.full_like(f, d_lp * 1e3), color=C3, ls="--", label="FIR low-pass 40 Hz, %d taps" % len(h_lp))
    a1.loglog(f, gd / FS * 1e3, color=C4, label="IIR band-pass 0.5–40 Hz (4th order)")
    a1.set_xlim(0.1, 100); a1.set_ylim(2, 6000)
    finish(a1, xlabel="Frequency (Hz)", ylabel="Group delay (ms)")
    a1.legend(loc="lower left", fontsize=6.0)
    panel(a1, "a")
    t, xe, pk = st_ecg()
    d = (len(h_bp) - 1) // 2
    y_fir = np.convolve(xe, h_bp)[d:d + len(xe)]                      # shifted back by the group delay
    y_iir = sps.sosfilt(sos, xe)
    beats = pk[(pk > d / FS + 1) & (pk < t[-1] - d / FS - 1)]
    lv = [st_level(t, y, beats) for y in (xe, y_fir, y_iir)]
    sel = (t > 9.8) & (t < 11.2)
    a2.plot(t[sel], xe[sel] * 1e3, color=PALE, lw=2.0, label="ECG, ST +%.3f mV" % lv[0])
    a2.plot(t[sel], y_fir[sel] * 1e3, color=C1, lw=1.0, ls="--",
            label="FIR, shifted back %.2f s: ST +%.3f mV" % (d_bp, lv[1]))
    a2.plot(t[sel], y_iir[sel] * 1e3, color=C4, lw=1.0, label="IIR, causal: ST +%.3f mV" % lv[2])
    a2.set_xlim(9.8, 11.2); a2.set_ylim(-0.45, 1.6)
    finish(a2, xlabel="Time (s)", ylabel="ECG (mV)")
    a2.legend(loc="upper right", fontsize=6.0)
    panel(a2, "b")
    savefig(fig, "ch23_fir_iir")
    return dict(n_bp=len(h_bp), d_bp=d_bp, n_lp=len(h_lp), d_lp=d_lp, st=lv,
                gd_iir={ff: float(np.interp(ff, f, gd)) / FS for ff in (0.5, 1.0, 2.0, 10.0)},
                gd_iir_max=float(gd.max() / FS))


def notch_ba(r, f0=50.0, fs=FS, unity_dc=True):
    """Second-order notch: zeros on the unit circle at f0, poles at radius r. Scaled to unity gain at DC."""
    c = np.cos(2 * np.pi * f0 / fs)
    b, a = np.array([1.0, -2 * c, 1.0]), np.array([1.0, -2 * r * c, r * r])
    return (b * a.sum() / b.sum() if unity_dc else b), a


RADII = ((0.95, C4), (0.99, C1), (0.995, C3))


def fig_notch():
    """Figure 23.3: notch magnitude for several r, and its ringing after a 1 mV step artefact."""
    fig, (a1, a2) = plt.subplots(1, 2, figsize=FULL2)
    f = np.linspace(45, 55, 4001)
    a1.axvspan(49.8, 50.2, color=ATINT, lw=0)
    note(a1, (50.2, -31), "mains drift ±0.2 Hz", (51.0, -31), color=AMBERDK, fs=6.5)
    for r, c in RADII:
        b, a = notch_ba(r)
        _, h = sps.freqz(b, a, worN=f, fs=FS)
        ff = np.linspace(40, 60, 200001)
        stop = ff[np.abs(sps.freqz(b, a, worN=ff, fs=FS)[1]) < 1 / np.sqrt(2)]
        a1.plot(f, 20 * np.log10(np.maximum(np.abs(h), 1e-6)), color=c,
                label="r = %g: width %.2f Hz" % (r, stop.max() - stop.min()))
    a1.set_xlim(45, 55); a1.set_ylim(-40, 3)
    finish(a1, xlabel="Frequency (Hz)", ylabel="Gain (dB)")
    a1.legend(loc="lower left", fontsize=6.0)
    panel(a1, "a")
    n0 = 50
    u = np.r_[np.zeros(n0), np.ones(int(1.5 * FS))] * 1e-3            # 1 mV step artefact at t = 0
    t = (np.arange(u.size) - n0) / FS
    for r, c in RADII:
        b, a = notch_ba(r)
        e = (sps.lfilter(b, a, u) - u)[n0:]
        pk = np.abs(e[:e.size // 10 * 10]).reshape(-1, 10).max(axis=1) * 1e6   # peak per 20 ms mains period
        tt = t[n0::10][:pk.size]
        tau = 1 / ((1 - r) * FS)
        a2.semilogy(tt, pk, color=c, label="r = %g: τ = %.0f ms" % (r, tau * 1e3))
    a2.set_xlim(0, 1.5); a2.set_ylim(0.1, 300)
    finish(a2, xlabel="Time after a 1 mV step (s)", ylabel="Ringing, peak per period (µV)")
    a2.legend(loc="upper right", fontsize=6.0)
    panel(a2, "b")
    savefig(fig, "ch23_notch")


def notch_numbers():
    """Numbers for Worked Example 23.4."""
    w0 = 2 * np.pi * 50 / FS
    for r in (0.95, 0.99, 0.995):
        b, a = notch_ba(r)
        f = np.linspace(40, 60, 200001)
        _, h = sps.freqz(b, a, worN=f, fs=FS)
        stop = f[np.abs(h) < 1 / np.sqrt(2)]
        att = lambda ff: 20 * np.log10(abs(sps.freqz(b, a, worN=[ff], fs=FS)[1][0]))
        b0, a0 = notch_ba(r, unity_dc=False)
        g0 = b0.sum() / a0.sum()
        t, x, pk = bs.ecg(fs=FS, duration=6.0, hr=60, hrv=0.0, seed=23)
        e = sps.lfilter(b, a, x) - x
        u = np.r_[np.zeros(50), np.ones(750)] * 1e-3
        es = sps.lfilter(b, a, u) - u
        tau = 1 / ((1 - r) * FS)
        print("notch r %.3f: -3 dB width %.3f Hz (approx %.3f); tau %.3f s, 1%% residual after %.2f s; "
              "unscaled DC gain %+.3f dB; att @50.2 %.1f dB, @50.5 %.1f dB; ECG beat |y-x| max %.1f uV; "
              "1 mV step ringing peak %.0f uV" % (r, stop.max() - stop.min(), (1 - r) * FS / np.pi, tau,
              np.log(100) * tau, 20 * np.log10(g0), att(50.2), att(50.5), np.abs(e[(t > 3) & (t < 4.3)]).max() * 1e6,
              np.abs(es).max() * 1e6))
    rng = np.random.default_rng(3)
    xin = 0.4 * rng.standard_normal(20000) / 3
    b, a = notch_ba(0.99, unity_dc=False)
    ref = sps.lfilter(b, a, xin)
    for B in (16, 18, 20, 22, 24):
        print("  notch r 0.99, %d bits: SNR vs float %.1f dB" % (B, 10 * np.log10(np.var(ref) / np.var(fixed_df(b, a, xin, B) - ref))))
    for fb in (8, 12, 20):
        print("  notch-frequency error, %d fractional coefficient bits: <= %.4f Hz" % (fb, 2.0 ** -fb * FS / (8 * np.pi * np.sin(w0))))
    z, p, k = sps.butter(4, 0.5 / (FS / 2), "high", output="zpk")
    print("  0.5 Hz HP pole angles (Hz)", np.round(np.abs(np.angle(p[:2])) * FS / 2 / np.pi, 3),
          "sin(theta)", np.round(np.sin(np.abs(np.angle(p[:2]))), 4), "vs notch sin(w0) %.3f" % np.sin(w0))


def baseline_numbers():
    """Numbers for Worked Example 23.3: ST level after baseline removal, with respiratory wander."""
    from scipy.ndimage import median_filter
    from scipy.interpolate import splrep, splev               # FITPACK cubic spline (no LAPACK needed)
    odd = lambda n: n + 1 - n % 2
    for hr, hrv in ((60, 0.0), (72, 0.03)):
        t, x, pk = bs.ecg(fs=FS, duration=40.0, hr=hr, hrv=hrv, seed=23)
        st = np.zeros_like(t)
        for r in pk:
            st[(t > r + 0.04) & (t < r + 0.20)] = 0.15e-3
        xe = x + st + 0.5e-3 * (np.sin(2 * np.pi * 0.25 * t + 0.3) + 0.4 * np.sin(2 * np.pi * 0.08 * t))
        beats = pk[(pk > 4) & (pk < 36)]
        res = {"no wander": st_level(t, x + st, beats)}
        b, a = sps.butter(1, 0.5 / (FS / 2), "high")
        res["causal HP 0.5 Hz"] = st_level(t, sps.lfilter(b, a, xe), beats)
        m2 = median_filter(median_filter(xe, odd(int(0.2 * FS)), mode="nearest"), odd(int(0.6 * FS)), mode="nearest")
        res["median 200+600 ms"] = st_level(t, xe - m2, beats)
        res["median 1.5 s"] = st_level(t, xe - median_filter(xe, odd(int(1.5 * FS)), mode="nearest"), beats)
        kn = np.array([r - 0.1 for r in pk if r > 0.2])
        kv = np.array([xe[(t > r - 0.12) & (t < r - 0.08)].mean() for r in pk if r > 0.2])
        res["PR-knot cubic spline"] = st_level(t, xe - splev(t, splrep(kn, kv, k=3, s=0)), beats)
        print("baseline, %d beats/min, 0.5 mV wander: " % hr + ", ".join("%s %.3f" % kv_ for kv_ in res.items()))


def cost_numbers(e_mac=10e-12):
    """Numbers for Worked Example 23.6: multiply-accumulates per second per channel (symmetric FIR folded)."""
    taps = lambda a_db, df, fs: (lambda n: n + 1 - n % 2)(sps.kaiserord(a_db, df / (fs / 2))[0])   # odd: type I
    n500, n125, nlp125, ndec = taps(40, 0.5, 500), taps(40, 0.5, 125), taps(40, 10, 125), taps(60, 45, 500)
    rows = [("IIR: 40 Hz low-pass (2 biquads) + 50 and 100 Hz notches at 500 S/s", 4 * 5 * 500),
            ("FIR band-pass 0.5-40 Hz at 500 S/s, %d taps" % n500, np.ceil(n500 / 2) * 500),
            ("FIR band-pass 0.5-40 Hz at 125 S/s, %d taps" % n125, np.ceil(n125 / 2) * 125),
            ("decimator 500->125 S/s (%d taps) + FIR low-pass (%d taps)" % (ndec, nlp125),
             (np.ceil(ndec / 2) + np.ceil(nlp125 / 2)) * 125)]
    for name, m in rows:
        print("cost %-62s %8.0f MAC/s/ch  %6.3f uW/ch  %6.2f uW for 8 ch (at %g pJ/MAC)"
              % (name, m, m * e_mac * 1e6, 8 * m * e_mac * 1e6, e_mac * 1e12))
    print("cost: FIR delay line at 500 S/s %d x 16 b = %.1f kbit/ch, %.0f kbit for 8 ch"
          % (n500, n500 * 16 / 1e3, 8 * n500 * 16 / 1e3))


def decimate_first_numbers():
    """Section 23.5: the 4th-order 0.5 Hz high-pass in fixed-point sections at 500 S/s and after decimating to 125 S/s."""
    rng = np.random.default_rng(3)
    xin = 0.4 * rng.standard_normal(20000) / 3
    for fs in (500.0, 125.0):
        sos = sps.butter(4, 0.5 / (fs / 2), "high", output="sos")
        ref = sps.sosfilt(sos, xin)
        snr = [10 * np.log10(np.var(ref) / np.var(fixed_sos(sos, xin, B) - ref)) for B in (24, 26, 28)]
        print("0.5 Hz HP as sections at %g S/s: %.1f / %.1f / %.1f dB at 24 / 26 / 28 bits" % ((fs,) + tuple(snr)))


if __name__ == "__main__":
    fig()
    out = fig_fir_iir()
    print("FIR band-pass %d taps, delay %.3f s; FIR low-pass %d taps, delay %.3f s; ST input/FIR/IIR %s mV; "
          "IIR group delay %s s, max %.3f s" % (out["n_bp"], out["d_bp"], out["n_lp"], out["d_lp"],
          np.round(out["st"], 3), {k: round(v, 4) for k, v in out["gd_iir"].items()}, out["gd_iir_max"]))
    fig_notch()
    notch_numbers()
    baseline_numbers()
    cost_numbers()
    decimate_first_numbers()
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
