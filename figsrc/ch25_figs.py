"""ch25_figs.py -- Chapter 25 figures and numbers.

fig()         ch25_eeg.svg: a synthetic EEG with rhythmic seizure-like segments, its line-length and theta-power
              features, and window-level detection accuracy (theta-power threshold) versus ADC bits for three input
              noise levels (EEG-mode range +-0.625 mV at the electrodes: total gain 800 into +-0.5 V).
fig_welch()   ch25_welch.svg: Welch spectra of synthetic EEG at the EEG-mode rate (500 S/s) for 1, 4 and 16 averaged
              2 s segments, and the scatter of an alpha-band power estimate versus window length for three estimators.
fig_ssvep()   ch25_ssvep.svg: a small steady-state (SSVEP) line emerging from the EEG background with integration
              time, and its detection SNR against the neighbouring bins.
numbers()     prints every other number quoted in Chapter 25 (band levels, quantisation in band, false alarms of the
              estimators, data rates).

Run `python ch25_figs.py` for everything, or name the parts: `python ch25_figs.py welch ssvep numbers`."""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "labs", "python"))
from bricdstyle import *
import biosig as bs
from scipy import signal as sps, stats

FS = 256.0
FS_IN = 0.625e-3
WIN = 2.0


def record(seed, dur=120.0):
    t, x = bs.eeg(fs=FS, duration=dur, seed=seed)[:2]
    rng = np.random.default_rng(seed)
    lab = np.zeros(int(dur / WIN), bool)
    for start in rng.choice(np.arange(5, int(dur / WIN) - 10), 3, replace=False):
        s0, s1 = start * WIN, start * WIN + 10.0
        m = (t >= s0) & (t < s1)
        f0 = rng.uniform(3, 6)
        env = np.sin(np.pi * (t[m] - s0) / 10.0)
        x[m] += 60e-6 * env * np.sign(np.sin(2 * np.pi * f0 * t[m])) * np.abs(np.sin(2 * np.pi * f0 * t[m])) ** 0.5
        lab[start:start + 5] = True
    return t, x, lab


def adc(x, bits, noise, seed):
    rng = np.random.default_rng(seed)
    y = np.clip(x + noise * rng.standard_normal(len(x)), -FS_IN, FS_IN * (1 - 2.0 ** (1 - bits)))
    return bs.quantize(y, bits, vfs=FS_IN)


def features(y):
    n = int(WIN * FS)
    k = len(y) // n
    seg = y[: k * n].reshape(k, n)
    ll = np.sum(np.abs(np.diff(seg, axis=1)), axis=1)
    f, p = sps.welch(seg, fs=FS, nperseg=n, axis=1)
    theta = p[:, (f >= 3) & (f < 8)].sum(axis=1)
    return ll, theta


def accuracy(bits, noise, seeds=range(4)):
    acc = []
    for s in seeds:
        t, x, lab = record(100 + s)
        _, th = features(adc(x, bits, noise, s))
        thr = np.median(th) * 3.0                      # theta power three times its median
        acc.append(np.mean((th > thr) == lab[: len(th)]))
    return np.mean(acc) * 100


def fig():
    fig, (a1, a2) = plt.subplots(1, 2, figsize=FULL2)
    t, x, lab = record(100)
    y = adc(x, 12, 1.5e-6, 0)
    ll, th = features(y)
    tw = (np.arange(len(ll)) + 0.5) * WIN
    a1.plot(t, y * 1e6 / 4 + 60, color=GRAPHITE, lw=0.3, label="EEG (µV/4, offset)")
    a1.plot(tw, ll / ll.max() * 40, color=C1, lw=1.2, label="line length (normalised)")
    a1.plot(tw, th / th.max() * 40, color=C2, lw=1.0, ls="--", label="theta power 3–8 Hz (normalised)")
    for i, l in enumerate(lab[: len(ll)]):
        if l:
            a1.axvspan(i * WIN, (i + 1) * WIN, color=ATINT, lw=0)
    a1.set_xlim(0, 120); a1.set_yticks([])
    finish(a1, xlabel="Time (s)", legend=True, loc="upper right")
    a1.legend(loc="upper right", fontsize=5.8)
    panel(a1, "a")
    bits = np.arange(3, 15)
    for nz, c in ((1.5e-6, C3), (5e-6, C1), (15e-6, C4)):
        a2.plot(bits, [accuracy(b, nz) for b in bits], "o-", color=c, ms=3, label=f"{nz*1e6:g} µVrms input noise")
    a2.axhline(75, color=MUTED, ls=":", lw=0.8)
    a2.text(10, 73, "always \"no seizure\": 75 %", fontsize=6.3, color=MUTED, va="top")
    a2.set_xlim(2.5, 14.5); a2.set_ylim(50, 101)
    finish(a2, xlabel="ADC bits (±0.625 mV input range)", ylabel="Window accuracy, theta power (%)", legend=True, loc="lower right")
    a2.legend(loc="lower right", fontsize=6.0)
    panel(a2, "b")
    savefig(fig, "ch25_eeg")


# ---------------------------------------------------------------- section 25.4: resolution and variance of band power
FS_EEG = 500.0          # Open-BioAFE EEG-mode output rate (Chapter 29: 512 kHz / 1024)
VN = 1.5e-6             # input noise target, rms over 0.5-100 Hz
LOG10 = 10 / np.log(10)  # 4.34 dB per unit relative error


def eeg_rec(seed, dur, alpha=10e-6, vn=VN, scale=1.0, fs=FS_EEG):
    """Synthetic EEG (biosig.eeg, 20 uVrms background, optional alpha) times `scale`, plus white input noise
    whose rms over 0.5-100 Hz is vn (density vn/sqrt(99.5 Hz), spread up to fs/2)."""
    t, x = bs.eeg(fs=fs, duration=dur, alpha_rms=alpha, seed=seed)
    rng = np.random.default_rng(seed + 10000)
    return t, scale * x + vn * np.sqrt(fs / 2 / 99.5) * rng.standard_normal(len(t))


def welch(x, tseg, fs=FS_EEG):
    """Welch PSD (V^2/Hz) with Hann segments of tseg seconds and 50 % overlap."""
    n = int(round(tseg * fs))
    return sps.welch(x, fs=fs, nperseg=n, noverlap=n // 2, detrend="constant")


def bg_psd(f, vn=VN, scale=1.0):
    """Expected one-sided PSD of eeg_rec without alpha: biosig.eeg shapes the amplitude spectrum as 1/f between
    0.5 and 100 Hz, so the power spectrum is c/f^2 with c set by the 20 uVrms total, plus the white input noise."""
    c = (20e-6) ** 2 / (1 / 0.5 - 1 / 100.0)
    return scale ** 2 * c / np.asarray(f, float) ** 2 + vn ** 2 / 99.5


def band_scatter(T, f1=8.0, f2=13.0, seeds=range(40), dur=256.0):
    """Std (dB) of a band-power estimate between windows of T s of one record (pooled over records, so the
    record-to-record scaling of biosig.eeg drops out), for (0) one Hann segment per window, (1) 1 s Hann segments
    with 50 % overlap, (2) a band-pass filter (2nd-order Butterworth prototype) and squarer averaged over the window.
    Stationary background EEG plus 1.5 uVrms input noise, no alpha rhythm."""
    sos = sps.butter(2, [f1, f2], btype="bandpass", fs=FS_EEG, output="sos")
    var = np.zeros(3)
    for s in seeds:
        t, x = eeg_rec(s, dur, alpha=0.0)
        n = int(T * FS_EEG); k = len(x) // n
        seg = x[: k * n].reshape(k, n)
        out = []
        for nper in (n, min(n, int(FS_EEG))):
            f, p = sps.welch(seg, fs=FS_EEG, nperseg=nper, noverlap=nper // 2, axis=1)
            out.append(p[:, (f >= f1) & (f < f2)].sum(axis=1) * (f[1] - f[0]))
        out.append((sps.sosfilt(sos, x) ** 2)[: k * n].reshape(k, n).mean(axis=1)[1:])   # drop the filter's start-up
        var += [np.var(10 * np.log10(v), ddof=1) for v in out]
    return np.sqrt(var / len(seeds))


def fig_welch():
    fig, (a1, a2) = plt.subplots(1, 2, figsize=FULL2)
    # (a) one record, 2 s Hann segments, K = 1, 4, 16 (2, 5, 17 s with 50 % overlap); reference = mean over 100 records
    t, x = eeg_rec(3, 64.0)
    ref = np.mean([welch(eeg_rec(200 + s, 64.0)[1][: int(17 * FS_EEG)], 2.0)[1] for s in range(100)], axis=0)
    for K, c, lw in ((1, PALE, 0.8), (4, C1, 0.8), (16, C4, 1.2)):
        f, p = welch(x[: int((K + 1) * FS_EEG)], 2.0)
        a1.plot(f, 10 * np.log10(p * 1e12), color=c, lw=lw, label=f"K = {K} ({K + 1} s)")
    a1.plot(f, 10 * np.log10(ref * 1e12), color=GRAPHITE, lw=0.9, ls="--", label="expected (100 records)")
    a1.axvspan(8, 13, color=ATINT, lw=0, zorder=0)
    a1.text(10.5, -20, "α", ha="center", fontsize=7, color=AMBERDK)
    a1.set_xlim(0, 45); a1.set_ylim(-22, 30)
    finish(a1, xlabel="Frequency (Hz)", ylabel="PSD (dB re 1 µV²/Hz)")
    a1.legend(loc="upper right", fontsize=5.8)
    panel(a1, "a")
    # (b) scatter of the alpha-band power against window length
    Ts = np.array([1, 2, 4, 8, 16, 32])
    sc = np.array([band_scatter(T) for T in Ts])
    tt = np.logspace(0, np.log10(32), 50)
    a2.loglog(tt, LOG10 / np.sqrt(5.0 * tt), color=GRAPHITE, lw=0.9, ls="--", label="4.34/√(BT) dB, B = 5 Hz")
    a2.loglog(Ts, sc[:, 0], "o-", color=C2, ms=3, lw=0.9, label="one Hann segment per window")
    a2.loglog(Ts[1:], sc[1:, 1], "s-", color=C1, ms=3, lw=0.9, label="1 s segments, 50 % overlap")
    a2.loglog(Ts, sc[:, 2], "^-", color=C3, ms=3, lw=0.9, label="band-pass filter and squarer")
    a2.axvline(2, color=MUTED, ls=":", lw=0.8)
    a2.text(2.1, 0.27, "2 s epoch", fontsize=6.3, color=MUTED)
    a2.set_xlim(0.9, 36); a2.set_ylim(0.25, 4)
    a2.set_xticks([1, 2, 4, 8, 16, 32]); a2.set_xticklabels(["1", "2", "4", "8", "16", "32"])
    a2.set_yticks([0.25, 0.5, 1, 2, 4]); a2.set_yticklabels(["0.25", "0.5", "1", "2", "4"])
    a2.minorticks_off()
    finish(a2, xlabel="Window length T (s)", ylabel="Scatter of α-band power (dB, 1σ)")
    a2.legend(loc="upper right", fontsize=5.8)
    panel(a2, "b")
    savefig(fig, "ch25_welch")
    print("band-power scatter (dB) alpha: T, one Hann, 1 s Welch, filter, theory")
    for T, v in zip(Ts, sc):
        print("  %4.0f s  %.2f  %.2f  %.2f  %.2f" % (T, v[0], v[1], v[2], LOG10 / np.sqrt(5.0 * T)))
    # scatter of single bins (outside the alpha peak) for K = 1, 4, 16, against 4.34/sqrt(K)
    for K in (1, 4, 16):
        lp = np.array([np.log10(welch(eeg_rec(400 + s, 64.0)[1][: int((K + 1) * FS_EEG)], 2.0)[1]) for s in range(100)])
        f = welch(np.zeros(int(4 * FS_EEG)), 2.0)[0]
        m = ((f > 2) & (f < 7)) | ((f > 15) & (f < 40))
        refK = np.log10(np.mean(10 ** lp, axis=0))
        print("  K = %2d (%2d s): bin scatter %.2f dB (4.34/sqrt(K) = %.2f dB)" % (
            K, K + 1, np.std(10 * (lp[:, m] - refK[m])), LOG10 / np.sqrt(K)))


# ---------------------------------------------------------------- section 25.5: a steady-state (SSVEP) line
F0 = 15.0                      # flicker frequency (Hz), away from the 10 Hz alpha
NBR = np.r_[-6:-1, 2:7]        # neighbour bins: 2 to 6 bins either side (the Hann main lobe is +-1 bin)
ENBW = 1.5                     # Hann window, bins
THR = stats.f.ppf(0.99, 2, 2 * len(NBR))   # 1 % false alarms, F(2, 20)


def ssvep(seed, T, A, vn=VN, scale=1.0, K=1, df_rel=0.0):
    """One trial: T s of synthetic EEG (with alpha) plus a line of A Vrms at F0*(1+df_rel), random phase.
    Returns f, PSD and the ratio of the F0 bin to the mean of the neighbour bins (K Hann segments, no overlap)."""
    t, x = eeg_rec(seed, T, vn=vn, scale=scale)
    rng = np.random.default_rng(seed + 777)
    x = x + np.sqrt(2) * A * np.sin(2 * np.pi * F0 * (1 + df_rel) * t + rng.uniform(0, 2 * np.pi))
    n = len(x) // K
    f, p = sps.welch(x, fs=FS_EEG, window="hann", nperseg=n, noverlap=0, detrend="constant")
    k0 = int(round(F0 / (f[1] - f[0])))
    return f, p, p[k0] / p[k0 + NBR].mean()


def snr_theory(T, A, vn=VN, scale=1.0):
    return 1 + A ** 2 * T / (ENBW * bg_psd(F0, vn, scale))


def t_needed(A, vn=VN, scale=1.0):
    """Integration time at which the expected ratio reaches the 1 % false-alarm threshold."""
    return (THR - 1) * ENBW * bg_psd(F0, vn, scale) / A ** 2


def fig_ssvep():
    fig = plt.figure(figsize=FULL2)
    gs = fig.add_gridspec(3, 2, hspace=0.12, wspace=0.28)
    axs = [fig.add_subplot(gs[i, 0]) for i in range(3)]
    a2 = fig.add_subplot(gs[:, 1])
    for ax, (T, c) in zip(axs, ((2, MUTED), (8, C1), (32, C4))):
        f, p, r = ssvep(36, T, 1e-6)          # a record whose three ratios are close to the medians of 40
        m = (f >= 12) & (f <= 18)
        y = p[m] / bg_psd(f[m])
        ax.plot(f[m], y, color=c, lw=0.8, drawstyle="steps-mid")
        ax.axvline(F0, color=AMBER, ls=":", lw=0.8, zorder=0)
        ax.set_xlim(12, 18); ax.set_ylim(0, 1.3 * y.max())
        ax.text(0.98, 0.95, f"T = {T} s", transform=ax.transAxes, fontsize=6.5, color=c, va="top", ha="right")
        ax.set_xticks([12, 13, 14, 15, 16, 17, 18])
        if ax is not axs[-1]:
            ax.set_xticklabels([])
    axs[1].set_ylabel("PSD / background")
    axs[-1].set_xlabel("Frequency (Hz)")
    axs[0].text(F0, 1.04, "15 Hz line, 1 µVrms", transform=axs[0].get_xaxis_transform(), fontsize=6.3,
                color=AMBERDK, va="bottom", ha="center")
    panel(axs[0], "a", y=1.08)
    Ts = np.array([2, 3, 4, 6, 8, 12, 16, 24, 32])
    tt = np.linspace(1.8, 34, 100)
    for A, c in ((1e-6, C1), (2e-6, C4)):
        r = np.array([[ssvep(s, T, A)[2] for s in range(300)] for T in Ts])
        lo, hi = np.percentile(r, [10, 90], axis=1)
        a2.fill_between(Ts, 10 * np.log10(lo), 10 * np.log10(hi), color=c, alpha=0.15, lw=0)
        a2.plot(Ts, 10 * np.log10(r.mean(axis=1)), "o", color=c, ms=3, label=f"{A*1e6:g} µVrms: simulated mean")
        a2.plot(tt, 10 * np.log10(snr_theory(tt, A)), color=c, lw=0.9, label=f"{A*1e6:g} µVrms: 1 + A²T/(1.5 S)")
        print("A = %g uVrms: P(detect) at T =" % (A * 1e6), " ".join("%g s: %.2f" % (T, np.mean(v > THR)) for T, v in zip(Ts, r)))
    h0 = np.array([[ssvep(s, T, 0.0)[2] for s in range(400)] for T in Ts])
    print("no line: false alarms at T =", " ".join("%g s: %.3f" % (T, np.mean(v > THR)) for T, v in zip(Ts, h0)),
          "mean %.3f" % np.mean(h0 > THR))
    a2.axhline(10 * np.log10(THR), color=AMBER, ls="--", lw=0.9)
    a2.text(33, 10 * np.log10(THR) - 0.4, "1 % false alarms", fontsize=6.3, color=AMBERDK, ha="right", va="top")
    a2.set_xscale("log"); a2.set_xlim(1.8, 36); a2.set_ylim(-2, 25)
    a2.set_xticks([2, 4, 8, 16, 32]); a2.set_xticklabels(["2", "4", "8", "16", "32"]); a2.minorticks_off()
    finish(a2, xlabel="Integration time T (s)", ylabel="Line over neighbours (dB)")
    a2.legend(loc="upper left", fontsize=5.8)
    panel(a2, "b")
    savefig(fig, "ch25_ssvep")


# ---------------------------------------------------------------- the other numbers of the chapter
def band_power(x, fs, f1, f2):
    f, p = bs.psd(x, fs, seg_s=4.0)
    return p[(f >= f1) & (f < f2)].sum() * (f[1] - f[0])


def numbers():
    print("Hann ENBW (bins): %.3f; 50 %% overlap correlation %.4f" % (
        len(np.hanning(1000)) * np.sum(np.hanning(1000) ** 2) / np.sum(np.hanning(1000)) ** 2,
        np.sum(np.hanning(1000)[:500] * np.hanning(1000)[500:]) / np.sum(np.hanning(1000) ** 2)))
    w = np.hanning(100000)
    print("Hann effective duration (sum w^2)^2 / (N sum w^4): %.3f of the window" % (np.sum(w ** 2) ** 2 / len(w) / np.sum(w ** 4)))
    pk = np.exp(-10 ** 0.5)
    lp = []
    for s in range(100):
        f, p1 = welch(eeg_rec(400 + s, 64.0)[1][: int(2 * FS_EEG)], 2.0)
        lp.append(p1)
    lp = np.array(lp); ref1 = lp.mean(axis=0)
    m = ((f >= 0.5) & (f < 7)) | ((f > 15) & (f <= 100))
    print("single 2 s periodogram: P(bin > 5 dB above expected) = %.3f analytic, %.3f simulated; %d bins in 0.5-100 Hz -> %.1f bins" % (
        pk, np.mean(lp[:, m] > 10 ** 0.5 * ref1[m]), np.sum((f >= 0.5) & (f <= 100)), pk * np.sum((f >= 0.5) & (f <= 100))))
    rho2 = (1 / 6) ** 2
    for K in (16, 20, 80):
        keff = K / (1 + 2 * (K - 1) / K * rho2)
        print("K = %d segments: K_eff %.1f, sigma %.2f dB, record %.0f s with 2 s segments" % (
            K, keff, LOG10 / np.sqrt(keff), (K + 1) / 2 * 2.0))
    # band levels of the synthetic EEG, the input noise and quantisation error, at 500 and 250 S/s
    for fs in (500.0, 250.0):
        acc = {}
        for s in range(20):
            t, bg = bs.eeg(fs=fs, duration=128.0, alpha_rms=0.0, seed=s)
            rng = np.random.default_rng(s + 999)
            nz = VN * np.sqrt(fs / 2 / 99.5) * rng.standard_normal(len(t))
            y = bs.eeg(fs=fs, duration=128.0, seed=s)[1] + nz
            for name, (f1, f2) in bs.EEG_BANDS.items():
                acc.setdefault((name, "bg"), []).append(band_power(bg, fs, f1, f2))
                acc.setdefault((name, "nz"), []).append(band_power(nz, fs, f1, f2))
                for b in (6, 8, 10):
                    acc.setdefault((name, b), []).append(band_power(bs.quantize(y, b, vfs=FS_IN) - y, fs, f1, f2))
        print("fs = %g S/s, uVrms in band: background, 1.5 uVrms input noise, quantisation 6/8/10 bits" % fs)
        for name in bs.EEG_BANDS:
            r = {k: np.sqrt(np.mean(acc[(name, k)])) * 1e6 for k in ("bg", "nz", 6, 8, 10)}
            print("  %-6s %5.2f  %.3f  %.3f %.3f %.3f   noise adds %.1f %%, 8 b adds %.1f %% to the band power" % (
                name, r["bg"], r["nz"], r[6], r[8], r[10], 100 * (r["nz"] / r["bg"]) ** 2, 100 * (r[8] / r["bg"]) ** 2))
    print("alpha 10 uVrms over 1.5 uVrms: broadband %.1f dB, in the 5 Hz band %.1f dB" % (
        20 * np.log10(10 / 1.5), 20 * np.log10(10 / (1.5 * np.sqrt(5 / 99.5)))))
    # false alarms of three theta-power estimators (3-8 Hz, 2 s windows, 3 x median) on a stationary background
    sos = sps.butter(2, [3, 8], btype="bandpass", fs=FS, output="sos")
    n = int(WIN * FS)
    res = {k: [] for k in ("one Hann segment", "1 s segments", "filter and squarer")}
    for s in range(300):
        t, x = bs.eeg(fs=FS, duration=240.0, seed=7000 + s)
        y = adc(x, 12, 1.5e-6, s)
        k = len(y) // n
        seg = y[: k * n].reshape(k, n)
        f, p = sps.welch(seg, fs=FS, nperseg=n, axis=1)
        a = p[:, (f >= 3) & (f < 8)].sum(1)
        f, p = sps.welch(seg, fs=FS, nperseg=n // 2, noverlap=n // 4, axis=1)
        b = p[:, (f >= 3) & (f < 8)].sum(1)
        c = (sps.sosfilt(sos, y) ** 2)[: k * n].reshape(k, n).mean(1)[2:]
        for key, v in zip(res, (a, b, c)):
            res[key].append((np.sum(v > 3 * np.median(v)), len(v), np.std(10 * np.log10(v), ddof=1)))
    for key, v in res.items():
        v = np.array(v)
        print("theta, 2 s, %-18s scatter %.2f dB, above 3x median %d of %d windows (%.3f %%, %.1f per hour)" % (
            key, v[:, 2].mean(), v[:, 0].sum(), v[:, 1].sum(), 100 * v[:, 0].sum() / v[:, 1].sum(),
            1800 * v[:, 0].sum() / v[:, 1].sum()))
    # SSVEP integration times and clock tolerance
    print("F(2,%d) 1 %% threshold %.2f = %.1f dB; S(15 Hz): background %.3f, input noise %.4f uV^2/Hz" % (
        2 * len(NBR), THR, 10 * np.log10(THR), bg_psd(F0, 0.0) * 1e12, VN ** 2 / 99.5 * 1e12))
    for A in (0.5e-6, 1e-6, 2e-6):
        print("  A = %.1f uVrms: T = %.2f s (no input noise %.2f s, 5 uVrms %.2f s)" % (
            A * 1e6, t_needed(A), t_needed(A, 0.0), t_needed(A, 5e-6)))
    print("  EEG and line 4x smaller: T = %.2f s with 1.5 uVrms, %.2f s noiseless (+%.0f %%)" % (
        t_needed(0.25e-6, VN, 0.25), t_needed(0.25e-6, 0.0, 0.25), 100 * (t_needed(0.25e-6, VN, 0.25) / t_needed(0.25e-6, 0.0, 0.25) - 1)))
    for K in (1, 2, 4):
        thr = stats.f.ppf(0.99, 2 * K, 2 * K * len(NBR))
        v = np.array([ssvep(s, 8, 1e-6, K=K)[2] for s in range(300)])
        h = np.array([ssvep(s, 8, 0.0, K=K)[2] for s in range(400)])
        print("  T = 8 s, 1 uVrms, %d Hann segment(s): threshold %.2f, detected %.2f, false alarms %.3f" % (
            K, thr, np.mean(v > thr), np.mean(h > thr)))
    w = np.hanning(4096); nn = np.arange(4096)
    for d in (0.25, 0.5, 1.0):
        print("  Hann scalloping at %.2f bin: %.2f dB" % (d, -20 * np.log10(abs(np.sum(w * np.exp(2j * np.pi * d * nn / 4096))) / np.sum(w))))
    for T in (4, 8, 32):
        print("  T = %d s: half a bin at 15 Hz is a frequency error of %.2f %%" % (T, 100 * 0.5 / (F0 * T)))
    # data out: raw versus band powers (8 channels, 2 s epochs, 5 bands + total)
    ch, ep, nb = 8, 2.0, 6
    rates = {"raw 500 S/s x 16 b": ch * 500 * 16, "raw 250 S/s x 16 b": ch * 250 * 16,
             "band powers, 16 b": ch * nb * 16 / ep, "band powers, 8-b log": ch * nb * 8 / ep,
             "seizure and artefact flags": ch * 2 / ep}
    eb, eev = 5e-9, 10e-6              # Chapter 27's order-of-magnitude radio model
    for k, r in rates.items():
        tci = 0.1 if r > 1000 else ep
        print("  %-28s %8.0f b/s  (%5.0f x less than raw 500 S/s)  radio %.1f uW bits + %.1f uW events (T_CI %.1f s)" % (
            k, r, rates["raw 500 S/s x 16 b"] / r, eb * r * 1e6, eev / tci * 1e6, tci))
    r = rates["band powers, 16 b"]
    print("  band powers, five epochs per packet: %.1f uW bits + %.1f uW events = %.1f uW" % (
        eb * r * 1e6, eev / (5 * ep) * 1e6, (eb * r + eev / (5 * ep)) * 1e6))
    fs_pow = (FS_IN / np.sqrt(2)) ** 2
    print("  log code: full-scale sine %.3g uV^2; 64 dB below is %.3f uV^2 = %.2f uVrms" % (
        fs_pow * 1e12, fs_pow * 1e12 / 10 ** 6.4, np.sqrt(fs_pow / 10 ** 6.4) * 1e6))
    print("  0.25 dB steps: rounding error %.3f dB rms" % (0.25 / np.sqrt(12)))
    print("  FFT buffer, 2 s at 250 S/s: %d words/ch, %d kbit for 8 ch at 16 b; filter bank state 5 bands x 4 words x 24 b"
          " x 8 ch = %d bit" % (500, 8 * 500 * 16 / 1000, 5 * 4 * 24 * 8))
    print("  AFE power 8 x 6.8 uW = %.1f uW" % (8 * 6.8))


if __name__ == "__main__":
    parts = sys.argv[1:] or ["eeg", "welch", "ssvep", "numbers"]
    if "eeg" in parts:
        fig()
        for nz in (1.5e-6, 5e-6, 15e-6):
            print("noise %g:" % nz, " ".join("%d:%.1f" % (b, accuracy(b, nz)) for b in (4, 5, 6, 7, 8, 10, 12, 14)))
        print("LSB at 6/8 bits: %.1f / %.1f uV" % (2 * FS_IN / 64 * 1e6, 2 * FS_IN / 256 * 1e6))
    if "welch" in parts:
        fig_welch()
    if "ssvep" in parts:
        fig_ssvep()
    if "numbers" in parts:
        numbers()
