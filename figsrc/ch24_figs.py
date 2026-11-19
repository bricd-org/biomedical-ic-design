"""ch24_figs.py -- Chapter 24 figures and numbers.

  fig()          a Pan-Tompkins QRS detector on a synthetic ECG through a behavioural front-end and ADC,
                 and its sensitivity versus ADC bits for several input noise levels      -> ch24_qrs.svg
  fig_stages()   the original integer Pan-Tompkins filters at 200 S/s, stage by stage, with the adaptive
                 threshold, and their frequency responses                                  -> ch24_ptstages.svg
  fig_hrv()      heart-rate variability from detected beats: tachogram, RR spectrum (LF/HF) and R-peak
                 timing error versus sample rate                                           -> ch24_hrv.svg
  numbers()      every other number quoted in Chapter 24 (delays, HRV example, record length, operation
                 count, data rates)

Run:  python ch24_figs.py
"""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "labs", "python"))
from bricdstyle import *
import biosig as bs
from scipy import signal as sps
from scipy.interpolate import PchipInterpolator     # (CubicSpline needs LAPACK, which this Python lacks)

FS = 500.0
FS_IN = 5e-3            # +-5 mV at the electrodes fills the converter (gain 100 into +-0.5 V)


def pan_tompkins(x, fs=FS):
    """Simplified Pan-Tompkins: 5-15 Hz band-pass, derivative, squaring, 150 ms integration, adaptive
    threshold with a 200 ms refractory period. Returns detected R times (s) and the stages."""
    sos = sps.butter(2, [5 / (fs / 2), 15 / (fs / 2)], "band", output="sos")
    bp = sps.sosfilt(sos, x)
    d = np.convolve(bp, np.array([1, 2, 0, -2, -1]) * fs / 8, mode="same")
    sq = d ** 2
    w = int(0.15 * fs)
    mwi = np.convolve(sq, np.ones(w) / w, mode="same")
    pk, _ = sps.find_peaks(mwi, distance=int(0.2 * fs))
    spki, npki = np.max(mwi[: int(2 * fs)]) * 0.5, np.mean(mwi[: int(2 * fs)]) * 0.5
    det = []
    for p in pk:
        thr = npki + 0.25 * (spki - npki)
        if mwi[p] > thr:
            det.append(p); spki = 0.125 * mwi[p] + 0.875 * spki
        else:
            npki = 0.125 * mwi[p] + 0.875 * npki
    det = np.array(det, dtype=int)
    # refine to the R peak in the raw signal within +-75 ms (group delay of the filters)
    r = [p - int(0.075 * fs) + np.argmax(bp[max(p - int(0.075 * fs), 0): p + int(0.075 * fs)]) for p in det]
    return np.array(r) / fs, (bp, mwi)


def score(det, truth, tol=0.075):
    det = det[(det > truth.min() - 0.3) & (det < truth.max() + 0.3)]      # same window as the truth
    tp = sum(np.any(np.abs(det - t) < tol) for t in truth)
    fp = len(det) - sum(np.any(np.abs(truth - d) < tol) for d in det)
    return tp / len(truth), tp / max(tp + fp, 1)


def chain(t, x, noise_rms, bits, seed):
    rng = np.random.default_rng(seed)
    y = x + noise_rms * rng.standard_normal(len(x)) + 200e-6 * np.sin(2 * np.pi * 0.3 * t)
    y = np.clip(y, -FS_IN, FS_IN * (1 - 2.0 ** (1 - bits)))
    return bs.code_to_volts(bs.quantize(y, bits, vfs=FS_IN) * 0 + np.floor((y + FS_IN) / (2 * FS_IN) * 2 ** bits), bits, vfs=FS_IN)


def fig():
    t, x, pk = bs.ecg(fs=FS, duration=60.0, hr=75, hrv=0.05, seed=24)
    fig, (a1, a2) = plt.subplots(1, 2, figsize=FULL2)
    y = chain(t, x, 50e-6, 8, 1)
    det, (bp, mwi) = pan_tompkins(y)
    sel = (t > 10) & (t < 14)
    a1.plot(t[sel], y[sel] / np.max(np.abs(y[sel])) + 2.2, color=GRAPHITE, lw=0.7, label="ECG, 8 bits, 50 µVrms noise")
    a1.plot(t[sel], bp[sel] / np.max(np.abs(bp[sel])) + 1.0, color=C2, lw=0.7, label="band-pass 5–15 Hz")
    a1.plot(t[sel], mwi[sel] / np.max(mwi[sel]) - 0.4, color=C1, lw=0.9, label="moving-window integral")
    for d in det[(det > 10) & (det < 14)]:
        a1.axvline(d, color=C3, lw=0.8, ls=":")
    a1.set_xlim(10, 14); a1.set_yticks([])
    finish(a1, xlabel="Time (s)", ylabel="Stages (normalised, offset)", legend=True, loc="upper right")
    a1.legend(loc="upper right", fontsize=5.8)
    panel(a1, "a")
    bits = np.arange(3, 13)
    res = {}
    for nz, c in ((10e-6, C3), (50e-6, C1), (100e-6, C2), (200e-6, C4)):
        se = []
        for b in bits:
            vals = [score(pan_tompkins(chain(t, x, nz, b, s))[0], pk[(pk > 2) & (pk < 58)])[0] for s in range(3)]
            se.append(np.mean(vals) * 100)
        res[nz] = se
        a2.plot(bits, se, "o-", color=c, ms=3, label=f"{nz*1e6:g} µVrms input noise")
    a2.axhline(99, color=AMBER, ls="--", lw=0.8)
    a2.text(3.1, 99.3, "99 %", fontsize=6.5, color=AMBERDK)
    a2.set_xlim(2.5, 12.5); a2.set_ylim(60, 101)
    finish(a2, xlabel="ADC bits (±5 mV input range)", ylabel="QRS sensitivity (%)", legend=True, loc="lower right")
    a2.legend(loc="lower right", fontsize=6.0)
    panel(a2, "b")
    savefig(fig, "ch24_qrs")
    return bits, res


# ------------------------------------------------------------------------------------------------
# The original integer Pan-Tompkins filters (designed for 200 S/s), scaled to other rates by keeping
# their time spans: low-pass (1 - z^-m)^2 / (1 - z^-1)^2 with m = 6 at 200 S/s, high-pass
# z^-(M/2) - (1/M)(1 - z^-M)/(1 - z^-1) with M = 32, five-point derivative, N = 0.15 fs integrator.
def pt_filters(fs):
    m_lp, m_hp, n_mwi = int(round(6 * fs / 200)), int(round(32 * fs / 200)), int(round(0.15 * fs))
    lp = np.convolve(np.ones(m_lp), np.ones(m_lp)) / m_lp ** 2          # unity DC gain (integer form: m^2)
    hp = -np.ones(m_hp) / m_hp
    hp[m_hp // 2] += 1.0
    dv = np.array([2, 1, 0, -1, -2]) / 8.0
    return dict(m_lp=m_lp, m_hp=m_hp, n_mwi=n_mwi, lp=lp, hp=hp, dv=dv, mwi=np.ones(n_mwi) / n_mwi)


def pt_delays(fs, f0=10.0):
    """Group delay (samples) of each stage at f0, and the total."""
    F = pt_filters(fs)
    d = {k: float(sps.group_delay((F[k], [1.0]), w=[f0], fs=fs)[1][0]) for k in ("lp", "hp", "dv", "mwi")}
    d["total"] = sum(d.values())
    return d


def pt_ops(fs):
    """Additions/subtractions, multiplications and comparisons per sample of the integer detector,
    written as recursions (shifts by powers of two are free), and the words of delay-line memory."""
    F = pt_filters(fs)
    ops = dict(lp=4,            # y = 2y1 - y2 + x - 2x[m] + x[2m]
               hp=3,            # running sum p += x - x[M]; y = x[M/2] - p/M
               dv=3,            # 2x + x1 - x3 - 2x4
               sq=1,            # one multiplication
               mwi=2,           # running sum s += q - q[N]
               peak=2)          # local-maximum test and threshold comparison
    mem = 2 * F["m_lp"] + 2 + F["m_hp"] + 1 + 4 + F["n_mwi"]
    return ops, sum(ops.values()), mem


def pt_integer(x, fs=200.0, dq=None):
    """Pan-Tompkins with the integer filters, stage by stage, and the adaptive threshold of the
    original paper (SPKI/NPKI running estimates, THR = NPKI + 0.25 (SPKI - NPKI), 200 ms refractory).
    dq: optional quantisation step for the derivative before squaring. Returns stages, threshold
    traces and the indices of the integrator peaks accepted as beats."""
    F = pt_filters(fs)
    lp = sps.lfilter(F["lp"], 1, x)
    bp = sps.lfilter(F["hp"], 1, lp)
    d = sps.lfilter(F["dv"], 1, bp)
    if dq is not None:
        d = np.round(d / dq) * dq
    sq = d ** 2
    mwi = sps.lfilter(F["mwi"], 1, sq)
    init = int(2 * fs)
    spki, npki = 0.5 * mwi[:init].max(), 0.5 * mwi[:init].mean()
    n = len(x)
    S, Nn, T = np.zeros(n), np.zeros(n), np.zeros(n)
    pk, _ = sps.find_peaks(mwi, distance=int(0.2 * fs))       # largest peak within +-200 ms, as fig()
    det, k0 = [], 0
    for k in pk:
        S[k0:k], Nn[k0:k], T[k0:k] = spki, npki, npki + 0.25 * (spki - npki)
        if mwi[k] > npki + 0.25 * (spki - npki):
            det.append(k); spki = 0.125 * mwi[k] + 0.875 * spki
        else:
            npki = 0.125 * mwi[k] + 0.875 * npki
        k0 = k
    S[k0:], Nn[k0:], T[k0:] = spki, npki, npki + 0.25 * (spki - npki)
    return dict(lp=lp, bp=bp, d=d, sq=sq, mwi=mwi, spki=S, npki=Nn, thr=T, det=np.array(det, int))


def fig_stages():
    """Figure: the integer Pan-Tompkins filters at 200 S/s, stage by stage, and their responses."""
    fs = 200.0
    t5, x5, pk = bs.ecg(fs=FS, duration=20.0, hr=75, hrv=0.05, seed=24)
    y5 = chain(t5, x5, 20e-6, 16, 2)                            # Open-BioAFE ECG mode, 500 S/s, 16 bits
    y = sps.resample_poly(y5, 2, 5)                             # decimated to 200 S/s for the detector
    t = np.arange(len(y)) / fs
    R = pt_integer(y, fs)
    delay = pt_delays(fs)["total"]
    fig = plt.figure(figsize=FULLTALL)
    gs = fig.add_gridspec(1, 2, width_ratios=[1.65, 1])
    a1, a2 = fig.add_subplot(gs[0]), fig.add_subplot(gs[1])
    t0, t1 = 8.0, 12.0
    sel = (t >= t0) & (t <= t1)
    rows = [("ECG in", y, GRAPHITE), ("band-pass", R["bp"], C2), ("derivative", R["d"], C5),
            ("squared", R["sq"], C4), ("integral", R["mwi"], C1)]
    off = [4.4, 3.3, 2.2, 1.1, 0.0]
    for (lab, s, c), o in zip(rows, off):
        sc = np.max(np.abs(s[sel]))
        a1.plot(t[sel], s[sel] / sc * 0.9 + o + (0.0 if lab in ("squared", "integral") else 0.45),
                color=c, lw=0.8 if lab != "integral" else 1.0)
        a1.text(t0 - 0.05, o + 0.45, lab, ha="right", va="center", fontsize=7, color=c)
        if lab == "integral":
            a1.plot(t[sel], R["thr"][sel] / sc * 0.9, color=AMBERDK, lw=0.9, ls="--")
            a1.plot(t[sel], R["spki"][sel] / sc * 0.9, color=MUTED, lw=0.6, ls=":")
            a1.plot(t[sel], R["npki"][sel] / sc * 0.9, color=MUTED, lw=0.6, ls=":")
            dk = R["det"][(t[R["det"]] >= t0) & (t[R["det"]] <= t1)]
            a1.plot(t[dk], R["mwi"][dk] / sc * 0.9, "v", color=C3, ms=4)
    for p in pk[(pk >= t0) & (pk <= t1)]:
        a1.axvline(p, color=PALE, lw=0.7, ls="-", zorder=0)
        a1.axvline(p + delay / fs, color=C3, lw=0.6, ls=":", zorder=0)
    i = np.argmin(np.abs(pk - 9.0)); p = pk[i]
    a1.annotate("", xy=(p + delay / fs, 5.6), xytext=(p, 5.6),
                arrowprops=dict(arrowstyle="<->", lw=0.6, color=C3, shrinkA=0, shrinkB=0, mutation_scale=6))
    a1.text(p + delay / fs + 0.03, 5.6, "%.0f ms delay" % (delay / fs * 1e3), va="center", fontsize=6.5, color=C3)
    k1 = np.searchsorted(t, t1) - 1
    sc = np.max(R["mwi"][sel])
    for lab, v, c in (("SPKI", R["spki"][k1], MUTED), ("THR", R["thr"][k1], AMBERDK), ("NPKI", R["npki"][k1], MUTED)):
        a1.text(t1 + 0.03, v / sc * 0.9, lab, va="center", fontsize=6.3, color=c)
    a1.set_xlim(t0 - 0.62, t1 + 0.32); a1.set_ylim(-0.15, 5.8); a1.set_yticks([])
    a1.set_xticks(np.arange(t0, t1 + 0.1, 1.0))
    a1.spines["left"].set_visible(False)
    finish(a1, xlabel="Time (s)")
    a1.grid(axis="y", visible=False)
    panel(a1, "a", x=0.0)
    F = pt_filters(fs)
    f = np.linspace(0.1, 60, 1200)
    for lab, h, c, ls in (("low-pass", F["lp"], C1, "-"), ("high-pass", F["hp"], C2, "-"),
                          ("band-pass", np.convolve(F["lp"], F["hp"]), GRAPHITE, "-"),
                          ("band-pass × d/dt", np.convolve(np.convolve(F["lp"], F["hp"]), F["dv"]), C4, "--")):
        _, H = sps.freqz(h, 1, worN=f, fs=fs)
        m = np.abs(H)
        a2.plot(f, 20 * np.log10(np.maximum(m / m.max(), 1e-6)), color=c, ls=ls, lw=1.1 if lab == "band-pass" else 0.9, label=lab)
    a2.axvspan(5, 15, color=ATINT, zorder=0)
    a2.text(10, -37, "QRS\n5–15 Hz", ha="center", fontsize=6.5, color=AMBERDK)
    a2.set_xlim(0, 60); a2.set_ylim(-40, 3)
    finish(a2, xlabel="Frequency (Hz)", ylabel="Gain (dB, peak = 0)")
    a2.legend(loc="center right", fontsize=6.0, bbox_to_anchor=(1.0, 0.66))
    panel(a2, "b")
    savefig(fig, "ch24_ptstages")
    inner = pk[(pk > 2.5) & (pk < 19.5)]
    se, ppv = score((R["det"] - delay) / fs, inner)
    d = R["det"] / fs
    off = np.array([d[np.argmin(np.abs(d - p - delay / fs))] - p for p in inner])
    return dict(delay=delay, se=se, ppv=ppv, off_mean=off.mean(), off_std=off.std())


# ------------------------------------------------------------------------------------------------
# Heart-rate variability: an RR process with the two-peak (LF 0.1 Hz, HF 0.25 Hz) spectrum of the
# McSharry ECG model, beats placed by integrating it, and an ECG built on those beats.
def rr_process(duration, mean_rr=0.8, sdnn=0.05, lf_hf=0.5, f1=0.1, f2=0.25, c=0.01, seed=0, fr=4.0):
    """Gaussian RR(t) process sampled at fr, with spectral peaks at f1 (LF) and f2 (HF) of width c and
    power ratio lf_hf; scaled to the expected standard deviation sdnn (not the realised one)."""
    rng = np.random.default_rng(seed)
    n = int(duration * fr) + 1
    n2 = 2 ** int(np.ceil(np.log2(2 * n)))
    f = np.fft.rfftfreq(n2, 1 / fr)
    S = lf_hf / (1 + lf_hf) * np.exp(-0.5 * ((f - f1) / c) ** 2) + 1 / (1 + lf_hf) * np.exp(-0.5 * ((f - f2) / c) ** 2)
    z = np.sqrt(S) * (rng.standard_normal(f.size) + 1j * rng.standard_normal(f.size)) / np.sqrt(2)
    r = np.fft.irfft(z, n2)[:n]
    r_exp = np.sqrt((2 * np.sum(S) - S[0]) / n2 ** 2)          # expected rms of the irfft output
    return np.arange(n) / fr, mean_rr + sdnn * r / r_exp


def beats_from_rr(tg, rrc, t0=0.3, duration=None):
    duration = tg[-1] - 2.0 if duration is None else duration
    b = [t0]
    while b[-1] < duration:
        b.append(b[-1] + np.interp(b[-1], tg, rrc))
    return np.array(b[:-1])


def ecg_from_beats(beats, fs, duration, amp=1e-3):
    """biosig.ecg()'s beat shape (ECG_WAVES) placed at given R times."""
    t = np.arange(int(duration * fs)) / fs
    x = np.zeros_like(t)
    rr = np.diff(beats, append=2 * beats[-1] - beats[-2])
    for tr, r in zip(beats, rr):
        lo, hi = np.searchsorted(t, tr - 0.5), np.searchsorted(t, tr + 0.8)
        for a, mu, sig in bs.ECG_WAVES.values():
            x[lo:hi] += a * np.exp(-0.5 * ((t[lo:hi] - tr - mu * np.sqrt(r)) / sig) ** 2)
    return t, x * amp


def hrv_time(rr):
    """SDNN and RMSSD (same units as rr)."""
    return np.std(rr, ddof=1), np.sqrt(np.mean(np.diff(rr) ** 2))


def hrv_freq(beats, fr=4.0, seg=120.0):
    """LF (0.04-0.15 Hz) and HF (0.15-0.4 Hz) power of the RR series, resampled at fr with a
    shape-preserving cubic, Welch with seg-second Hann segments. Returns LF, HF (s^2), f, PSD."""
    rr, tb = np.diff(beats), beats[1:]
    tu = np.arange(tb[0], tb[-1], 1 / fr)
    ru = PchipInterpolator(tb, rr)(tu)
    f, p = sps.welch(ru - ru.mean(), fs=fr, nperseg=min(int(seg * fr), len(ru)), detrend="constant")
    df = f[1] - f[0]
    lf = p[(f >= 0.04) & (f < 0.15)].sum() * df
    hf = p[(f >= 0.15) & (f < 0.4)].sum() * df
    return lf, hf, f, p


def parabolic(sig, k):
    """Sub-sample peak position from the three samples around index k."""
    a, b, c = sig[k - 1], sig[k], sig[k + 1]
    den = a - 2 * b + c
    return k + np.where(den != 0, 0.5 * (a - c) / np.where(den != 0, den, 1), 0.0)


def detect_times(y, fs, interp=True):
    """R times from pan_tompkins(), optionally refined by parabolic interpolation on the band-pass."""
    det, (bp, _) = pan_tompkins(y, fs)
    k = np.clip(np.round(det * fs).astype(int), 1, len(y) - 2)
    return (parabolic(bp, k) if interp else k.astype(float)) / fs


def match(det, beats):
    """Detected time nearest to each true beat, and the timing error with its constant part removed."""
    m = np.array([det[np.argmin(np.abs(det - b))] for b in beats])
    e = m - beats
    return m, e - np.median(e)


def hrv_record(seed=24, duration=300.0):
    tg, rrc = rr_process(duration + 10, seed=seed)
    beats = beats_from_rr(tg, rrc, duration=duration - 0.5)
    return beats


def timing_vs_rate(beats, rates, noise=20e-6, bits=16, duration=300.0):
    out = {}
    inner = beats[(beats > 2) & (beats < duration - 2)]
    for fs in rates:
        t, x = ecg_from_beats(beats, fs, duration)
        y = chain(t, x, noise, bits, 3)
        out[fs] = [np.std(match(detect_times(y, fs, ip), inner)[1]) for ip in (False, True)]
        out[fs] += list(score(detect_times(y, fs), inner))
    return out


def fig_hrv():
    """Figure: tachogram, RR spectrum and R-timing error versus sample rate."""
    D = 300.0
    beats = hrv_record()
    inner = beats[(beats > 2) & (beats < D - 2)]
    t, x = ecg_from_beats(beats, FS, D)
    y = chain(t, x, 20e-6, 8, 4)                                  # monitoring mode: 8 bits
    det = detect_times(y, FS)
    se, ppv = score(det, inner)
    m, e = match(det, inner)
    rr_true, rr_det = np.diff(inner), np.diff(m)
    fig = plt.figure(figsize=FULLTALL)
    gs = fig.add_gridspec(2, 2, height_ratios=[1, 1.15])
    a1 = fig.add_subplot(gs[0, :]); a2 = fig.add_subplot(gs[1, 0]); a3 = fig.add_subplot(gs[1, 1])
    a1.plot(inner[1:], rr_true * 1e3, color=PALE, lw=2.2, label="true RR")
    a1.plot(m[1:], rr_det * 1e3, ".", color=C1, ms=2.2, label="detected, 8 bits, 500 S/s")
    s0, r0 = hrv_time(rr_true); s1, r1 = hrv_time(rr_det)
    a1.text(0.995, 0.97, "SDNN %.2f / %.2f ms    RMSSD %.2f / %.2f ms  (true / detected)" % (s0 * 1e3, s1 * 1e3, r0 * 1e3, r1 * 1e3),
            transform=a1.transAxes, ha="right", va="top", fontsize=6.5, color=GRAPHITE)
    a1.set_xlim(0, D); a1.set_ylim(640, 990)
    finish(a1, xlabel="Time (s)", ylabel="RR (ms)", legend=True, loc="upper left")
    a1.legend(loc="upper left", fontsize=6.0, ncol=2)
    panel(a1, "a")
    lf0, hf0, f, p0 = hrv_freq(inner)
    lf1, hf1, f, p1 = hrv_freq(m)
    a2.axvspan(0.04, 0.15, color=BTINT, zorder=0); a2.axvspan(0.15, 0.4, color=ATINT, zorder=0)
    a2.plot(f, p0 * 1e6, color=PALE, lw=2.2, label="true")
    a2.plot(f, p1 * 1e6, color=C1, lw=0.9, label="detected")
    top = 1.08 * max(p0.max(), p1.max()) * 1e6
    a2.text(0.095, top * 0.93, "LF", ha="center", fontsize=7, color=C1)
    a2.text(0.275, top * 0.93, "HF", ha="center", fontsize=7, color=AMBERDK)
    a2.text(0.395, top * 0.55, "LF/HF\n%.2f true\n%.2f detected" % (lf0 / hf0, lf1 / hf1), ha="right", fontsize=6.3, color=GRAPHITE)
    a2.set_xlim(0, 0.5); a2.set_ylim(0, top)
    finish(a2, xlabel="Frequency (Hz)", ylabel="RR PSD (ms²/Hz)", legend=True, loc="upper left")
    a2.legend(loc="center left", fontsize=6.0, bbox_to_anchor=(0.0, 0.62))
    panel(a2, "b")
    rates = [100, 125, 150, 200, 250, 300, 400, 500]
    tv = timing_vs_rate(beats, rates)
    fr = np.linspace(90, 520, 200)
    a3.plot(fr, 1e3 / (fr * np.sqrt(12)), color=PALE, lw=2.2, label=r"$1/(f_\mathrm{s}\sqrt{12})$")
    a3.plot(rates, [tv[r][0] * 1e3 for r in rates], "o-", color=C4, ms=3, lw=0.9, label="sample of the peak")
    a3.plot(rates, [tv[r][1] * 1e3 for r in rates], "s-", color=C3, ms=3, lw=0.9, label="parabolic interpolation")
    a3.set_xlim(80, 520); a3.set_ylim(0, 3.3)
    finish(a3, xlabel="Sample rate (S/s)", ylabel="R timing error (ms rms)", legend=True, loc="upper right")
    a3.legend(loc="upper right", fontsize=6.0)
    panel(a3, "c")
    savefig(fig, "ch24_hrv")
    return dict(n=len(inner), se=se, ppv=ppv, sdnn=(s0, s1), rmssd=(r0, r1), lfhf=(lf0 / hf0, lf1 / hf1),
                lf=(lf0, lf1), hf=(hf0, hf1), timing=tv, mean_rr=rr_true.mean(), err8=np.std(e))


# ------------------------------------------------------------------------------------------------
def numbers():
    print("\n--- Worked Example: delays and windows of the integer filters")
    for fs in (200.0, 250.0, 500.0):
        F, d = pt_filters(fs), pt_delays(fs)
        ops, tot, mem = pt_ops(fs)
        print("fs %3.0f: m_lp %d m_hp %d N_mwi %d | delay lp %.1f hp %.2f dv %.1f mwi %.1f total %.1f samples = %.1f ms"
              % (fs, F["m_lp"], F["m_hp"], F["n_mwi"], d["lp"], d["hp"], d["dv"], d["mwi"], d["total"], d["total"] / fs * 1e3))
        print("        ops/sample %d -> %.0f ops/s per channel, %.0f for 8 channels; memory %d words" % (tot, tot * fs, 8 * tot * fs, mem))
    for fs in (200.0, 500.0):
        F = pt_filters(fs)
        f = np.linspace(0.05, 60, 12000)
        for lab, h in (("band-pass", np.convolve(F["lp"], F["hp"])), ("bp x d/dt", np.convolve(np.convolve(F["lp"], F["hp"]), F["dv"]))):
            _, H = sps.freqz(h, 1, worN=f, fs=fs); m = np.abs(H)
            b = f[m >= m.max() / np.sqrt(2)]
            print("  fs %3.0f %-9s peak %.1f Hz, -3 dB %.1f-%.1f Hz" % (fs, lab, f[np.argmax(m)], b.min(), b.max()))
    print("  integer LP DC gain %d (m^2)" % (6 ** 2))
    print("\n--- Worked Example: HRV from a short RR series")
    beats = hrv_record()
    rr = np.round(np.diff(beats) * 1e3)                          # ms, rounded
    s8 = rr[:8]
    s, r = hrv_time(s8)
    print("first 8 RR (ms):", s8.astype(int).tolist(), " mean %.1f ms -> HR %.1f bpm" % (s8.mean(), 60e3 / s8.mean()))
    print("  deviations:", (s8 - s8.mean()).round(1).tolist(), " sum sq %.0f" % np.sum((s8 - s8.mean()) ** 2))
    print("  successive diffs:", np.diff(s8).astype(int).tolist(), " sum sq %.0f" % np.sum(np.diff(s8) ** 2))
    print("  SDNN %.1f ms, RMSSD %.1f ms" % (s, r))
    D = 300.0
    inner = beats[(beats > 2) & (beats < D - 2)]
    sa, ra = hrv_time(np.diff(inner) * 1e3)
    lf, hf, _, _ = hrv_freq(inner)
    print("  5 min: %d beats, mean RR %.1f ms, SDNN %.1f ms, RMSSD %.1f ms, LF %.0f ms2 HF %.0f ms2 LF/HF %.2f"
          % (len(inner), np.diff(inner).mean() * 1e3, sa, ra, lf * 1e6, hf * 1e6, lf / hf))
    print("  spread over 200 records (median and 10-90 % range):")
    for L in (60.0, 120.0, 300.0):
        res = []
        for sd in range(200):
            b = hrv_record(seed=1000 + sd, duration=L + 4)
            b = b[(b > 2) & (b < L + 2)]
            s_, r_ = hrv_time(np.diff(b) * 1e3)
            lf_, hf_, _, _ = hrv_freq(b, seg=min(120.0, L))
            res.append((s_, r_, lf_ / hf_, len(b)))
        res = np.array(res)
        q = np.percentile(res, [10, 50, 90], axis=0)
        print("   %3.0f s (%3.0f beats): SDNN %.1f [%.1f-%.1f]  RMSSD %.1f [%.1f-%.1f]  LF/HF %.2f [%.2f-%.2f]"
              % (L, q[1, 3], q[1, 0], q[0, 0], q[2, 0], q[1, 1], q[0, 1], q[2, 1], q[1, 2], q[0, 2], q[2, 2]))
    one_missed = np.delete(inner, 100)
    one_extra = np.sort(np.append(inner, 0.5 * (inner[100] + inner[101])))
    for lab, b in (("one missed beat", one_missed), ("one false beat", one_extra)):
        s_, r_ = hrv_time(np.diff(b) * 1e3)
        print("  %s in %d: SDNN %.1f -> %.1f ms, RMSSD %.1f -> %.1f ms" % (lab, len(inner), sa, s_, ra, r_))
    print("  interpolation onto 4 Hz, paired against the 4 Hz process itself (200 records, medians):")
    res = []
    for sd in range(200):
        tg, rrc = rr_process(310.0, seed=1000 + sd)
        sel = (tg > 2) & (tg < 302)
        f, p0 = sps.welch(rrc[sel] - rrc[sel].mean(), fs=4.0, nperseg=480, detrend="constant")
        r0 = p0[(f >= 0.04) & (f < 0.15)].sum() / p0[(f >= 0.15) & (f < 0.4)].sum()
        b = beats_from_rr(tg, rrc, duration=304.0); b = b[(b > 2) & (b < 302)]
        lf_, hf_, _, _ = hrv_freq(b)
        rr_, tb = np.diff(b), b[1:]
        tu = np.arange(tb[0], tb[-1], 0.25)
        f, p1 = sps.welch(np.interp(tu, tb, rr_) - rr_.mean(), fs=4.0, nperseg=480, detrend="constant")
        res.append((r0, (lf_ / hf_) / r0, (p1[(f >= 0.04) & (f < 0.15)].sum() / p1[(f >= 0.15) & (f < 0.4)].sum()) / r0))
    res = np.array(res)
    print("   process LF/HF median %.2f; PCHIP raises LF/HF x%.3f, linear x%.3f" % tuple(np.median(res, axis=0)))
    print("  timing error propagation: SDNN^2 + 2 s^2, RMSSD^2 + 6 s^2")
    for st in (0.27, 0.11):
        print("   sigma %.2f ms (parabolic): RMSSD 10 -> %.2f ms" % (st, np.sqrt(100 + 6 * st ** 2)))
    for fs in (500.0, 125.0):
        st = 1e3 / (fs * np.sqrt(12))
        for base in (50.0, 10.0):
            print("   fs %3.0f sigma %.2f ms: RMSSD %.0f -> %.2f ms, SDNN %.0f -> %.2f ms"
                  % (fs, st, base, np.sqrt(base ** 2 + 6 * st ** 2), base, np.sqrt(base ** 2 + 2 * st ** 2)))
    print("\n--- Worked Example: on-chip cost and data")
    raw1, raw8 = 500 * 16, 8 * 500 * 16
    for bpm in (75, 180):
        rt = bpm / 60 * 16
        print("  %d bpm: R times (16 b per beat) %.0f b/s; raw one channel %d b/s (x%.0f); raw 8 ch %d b/s (x%.0f)"
              % (bpm, rt, raw1, raw1 / rt, raw8, raw8 / rt))
    print("  16-bit RR in 0.25 ms units: range %.1f s, rounding error %.3f ms rms" % (2 ** 16 * 0.25e-3, 0.25 / np.sqrt(12)))
    feat27 = 8 * 2 * 16 * 1.25 + 16
    print("  Ch 27 ECG features %.0f b/s (x%.0f vs raw 8 ch)" % (feat27, raw8 / feat27))
    for rate in (raw8, feat27, 20.0):
        print("  radio at 5 nJ/b: %7.0f b/s -> %.2f uW" % (rate, rate * 5e-9 * 1e6))
    ops, tot, mem = pt_ops(500.0)
    for fs in (500.0, 250.0):
        ops, tot, mem = pt_ops(fs)
        print("  ops 8 ch at %3.0f S/s: %.0f /s = %.1f %% of one operation per cycle at the 512 kHz feature clock;"
              " at 1 pJ/op %.0f nW (%.1f nW per channel)" % (fs, 8 * tot * fs, 100 * 8 * tot * fs / 512e3,
                                                             8 * tot * fs * 1e-12 * 1e9, tot * fs * 1e-12 * 1e9))
    print("\n--- Squaring a truncated derivative (200 S/s integer filters, 60 s, 3 seeds)")
    t5, x5, pk = bs.ecg(fs=FS, duration=60.0, hr=75, hrv=0.05, seed=24)
    fs = 200.0
    F = pt_filters(fs)
    h = np.convolve(np.convolve(F["lp"], F["hp"]), F["dv"])
    dfs = FS_IN * np.sum(np.abs(h))                              # largest possible derivative output
    delay = pt_delays(fs)["total"]
    y = sps.resample_poly(chain(t5, x5, 50e-6, 16, 0), 2, 5)
    dd = pt_integer(y, fs)["det"] / fs
    inner = pk[(pk > 2.5) & (pk < 57.5)]
    off = np.array([dd[np.argmin(np.abs(dd - p - delay / fs))] - p for p in inner])
    print("  50 uVrms, 60 s: integrator peak - R = %.0f ms, scatter %.1f ms rms" % (off.mean() * 1e3, off.std() * 1e3))
    print("  a 1 mV R wave uses %.1f %% of the derivative's worst-case range" % (100 * np.max(np.abs(pt_integer(y, fs)["d"])) / dfs))
    for nz in (50e-6, 200e-6):
        for bd in (None, 8, 6, 4, 3):
            r = []
            for sd in range(3):
                y = sps.resample_poly(chain(t5, x5, nz, 16, sd), 2, 5)
                R = pt_integer(y, fs, dq=None if bd is None else 2 * dfs / 2 ** bd)
                r.append(score((R["det"] - delay) / fs, pk[(pk > 2.5) & (pk < 57.5)]))
            r = np.array(r)
            print("  %3.0f uVrms, derivative %s bits: Se %.1f-%.1f %%  PPV %.1f-%.1f %%" % (nz * 1e6, "full" if bd is None else bd,
                  100 * r[:, 0].min(), 100 * r[:, 0].max(), 100 * r[:, 1].min(), 100 * r[:, 1].max()))


if __name__ == "__main__":
    bits, res = fig()
    for k, v in res.items():
        print("noise %.0f uV:" % (k * 1e6), " ".join("%d:%.1f" % (b, s) for b, s in zip(bits, v)))
    t, x, pk = bs.ecg(fs=FS, duration=60.0, hr=75, hrv=0.05, seed=24)
    for nz, b in ((10e-6, 12), (100e-6, 6), (200e-6, 12)):
        se, ppv = score(pan_tompkins(chain(t, x, nz, b, 0))[0], pk[(pk > 2) & (pk < 58)])
        print("noise %g bits %d: Se %.3f PPV %.3f" % (nz, b, se, ppv))
    st = fig_stages()
    print("stages figure: total delay %.1f samples at 200 S/s, Se %.3f PPV %.3f; integrator peak - R = %.0f ms (%.1f ms rms)"
          % (st["delay"], st["se"], st["ppv"], st["off_mean"] * 1e3, st["off_std"] * 1e3))
    h = fig_hrv()
    print("HRV figure: %d beats, mean RR %.1f ms, Se %.4f PPV %.4f, timing std (8 b, 500 S/s, interp) %.2f ms"
          % (h["n"], h["mean_rr"] * 1e3, h["se"], h["ppv"], h["err8"] * 1e3))
    print("  SDNN %.2f / %.2f ms, RMSSD %.2f / %.2f ms, LF %.0f / %.0f ms2, HF %.0f / %.0f ms2, LF/HF %.3f / %.3f"
          % (h["sdnn"][0] * 1e3, h["sdnn"][1] * 1e3, h["rmssd"][0] * 1e3, h["rmssd"][1] * 1e3,
             h["lf"][0] * 1e6, h["lf"][1] * 1e6, h["hf"][0] * 1e6, h["hf"][1] * 1e6, h["lfhf"][0], h["lfhf"][1]))
    for r, (a, b, se, ppv) in h["timing"].items():
        print("  %3d S/s: timing %.2f ms (peak sample), %.2f ms (parabolic); 1/(fs sqrt12) = %.2f ms; Se %.4f PPV %.4f"
              % (r, a * 1e3, b * 1e3, 1e3 / (r * np.sqrt(12)), se, ppv))
    numbers()
