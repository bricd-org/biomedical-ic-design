"""ch26_figs.py -- Chapter 26 figures and numbers.

fig()            ch26_emg.svg       synthetic 8-channel surface EMG for five gestures (each a fixed pattern of
                                    channel amplitudes with trial-to-trial variation), features MAV, WL, ZC and SSC
                                    per channel over 200 ms windows, a linear discriminant, and accuracy versus ADC
                                    bits for three sample rates (EMG range +-5 mV).
fig_features()   ch26_features.svg  biosig.emg() contraction with its RMS envelope over 200 ms windows and a 50 ms
                                    hop, and the four time-domain features per window, ZC with and without a dead band.
fig_spikes()     ch26_spikes.svg    small synthetic spikes (biosig.spikes()) with an amplitude threshold from the
                                    median noise estimate and the NEO at lag 1 and lag 5; detection versus false
                                    alarms per second for the three detectors.
numbers()        prints every other number quoted in Chapter 26 (latency, envelope noise, operation counts, data
                 rates, noise estimates, false-alarm rates, median tracker).

Run:  python ch26_figs.py            (all figures and numbers, about a minute)
      python ch26_figs.py numbers    (numbers only)
"""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "labs", "python"))
from bricdstyle import *
import biosig as bs
from scipy import signal as sps

CH, G = 8, 5
FS_IN = 5e-3
rng0 = np.random.default_rng(26)
PATTERN = rng0.uniform(0.05, 1.0, (G, CH)) * 0.6e-3          # rms amplitude per channel and gesture


def window(g, fs, rng, dur=0.2):
    n = int(dur * fs)
    sos = sps.butter(4, [20 / (fs / 2), min(450, 0.45 * fs) / (fs / 2)], "band", output="sos")
    x = sps.sosfilt(sos, rng.standard_normal((CH, n + 200)), axis=1)[:, 200:]
    x = x / x.std(axis=1, keepdims=True)
    amp = PATTERN[g] * rng.uniform(0.75, 1.25, CH) * rng.uniform(0.7, 1.3)
    return x * amp[:, None] + 3e-6 * rng.standard_normal((CH, n))


def feats(x, thr=10e-6):
    mav = np.mean(np.abs(x), axis=1)
    wl = np.sum(np.abs(np.diff(x, axis=1)), axis=1)
    zc = np.sum((x[:, :-1] * x[:, 1:] < 0) & (np.abs(x[:, :-1] - x[:, 1:]) > thr), axis=1)
    d1, d2 = x[:, 1:-1] - x[:, :-2], x[:, 1:-1] - x[:, 2:]
    ssc = np.sum((d1 * d2 > 0) & ((np.abs(d1) > thr) | (np.abs(d2) > thr)), axis=1)
    return np.concatenate([np.log(mav + 1e-9), np.log(wl + 1e-9), zc / x.shape[1], ssc / x.shape[1]])


def lda_fit(X, y):
    mu = np.array([X[y == k].mean(0) for k in range(G)])
    S = sum(np.cov(X[y == k].T) for k in range(G)) / G + 1e-6 * np.eye(X.shape[1])
    Si = np.linalg.inv(S)
    return mu, Si


def lda_predict(model, X):
    mu, Si = model
    d = [np.einsum("ij,jk,ik->i", X - m, Si, X - m) for m in mu]
    return np.argmin(np.array(d), axis=0)


def accuracy(bits, fs, n_train=40, n_test=40, seed=0):
    rng = np.random.default_rng(seed)
    def data(n):
        X, y = [], []
        for g in range(G):
            for _ in range(n):
                w = np.clip(window(g, fs, rng), -FS_IN, FS_IN * (1 - 2.0 ** (1 - bits)))
                X.append(feats(bs.quantize(w, bits, vfs=FS_IN))); y.append(g)
        return np.array(X), np.array(y)
    Xtr, ytr = data(n_train); Xte, yte = data(n_test)
    return np.mean(lda_predict(lda_fit(Xtr, ytr), Xte) == yte) * 100


def fig():
    fig, (a1, a2) = plt.subplots(1, 2, figsize=FULL2)
    rng = np.random.default_rng(1)
    fs = 2000.0
    x = np.concatenate([window(g, fs, rng, 0.5)[0] for g in (0, 2, 4)])
    t = np.arange(len(x)) / fs
    a1.plot(t, x * 1e3, color=C1, lw=0.4, label="channel 1, three gestures")
    n = int(0.2 * fs)
    mav = [np.mean(np.abs(x[i:i + n])) for i in range(0, len(x) - n, n // 2)]
    a1.plot((np.arange(len(mav)) * n / 2 + n / 2) / fs, np.array(mav) * 1e3 * 3, color=C4, lw=1.5, label="MAV × 3 (200 ms windows)")
    a1.set_xlim(0, 1.5)
    finish(a1, xlabel="Time (s)", ylabel="EMG (mV)", legend=True, loc="upper right")
    a1.legend(loc="upper right", fontsize=6.0)
    panel(a1, "a")
    bits = np.array([3, 4, 5, 6, 8, 10, 12])
    for fs, c in ((500.0, C2), (1000.0, C1), (2000.0, C3)):
        a2.plot(bits, [np.mean([accuracy(b, fs, seed=s) for s in range(2)]) for b in bits], "o-", color=c, ms=3, label=f"{fs:g} S/s")
    a2.axhline(100 / G, color=MUTED, ls=":", lw=0.8)
    a2.text(2.7, 22, "chance: 20 %", fontsize=6.3, color=MUTED)
    a2.set_xlim(2.5, 12.5); a2.set_ylim(0, 102)
    finish(a2, xlabel="ADC bits (±5 mV input range)", ylabel="Gesture accuracy (%)", legend=True, loc="lower right")
    panel(a2, "b")
    savefig(fig, "ch26_emg")


# ------------------------------------------------------------------------------------------------ EMG features
FS_EMG = 2000.0
NOISE_EMG = 3.4e-6            # analog + quantisation noise at the EMG input, Worked Example 13.3
DEADBAND = 20e-6              # ZC/SSC dead band used in Figure 26.1 and the text


def emg_record(seed=3):
    """biosig.emg() (two contractions, 1 mV peak) plus 3.4 uVrms of input noise, quantised to 12 bits over +-5 mV."""
    t, x = bs.emg(fs=FS_EMG, seed=seed)
    x = x + NOISE_EMG * np.random.default_rng(seed + 100).standard_normal(len(x))
    return t, bs.quantize(np.clip(x, -FS_IN, FS_IN * (1 - 2.0 ** -11)), 12, vfs=FS_IN)


def td_features(seg, T=DEADBAND):
    """MAV, RMS, WL, ZC and SSC of one window (ZC and SSC with dead band T on the sample-to-sample step)."""
    d = np.diff(seg)
    zc = np.sum((seg[:-1] * seg[1:] < 0) & (np.abs(d) >= T))
    ssc = np.sum((d[:-1] * d[1:] < 0) & ((np.abs(d[:-1]) >= T) | (np.abs(d[1:]) >= T)))
    return np.array([np.mean(np.abs(seg)), np.sqrt(np.mean(seg ** 2)), np.sum(np.abs(d)), zc, ssc])


def sliding(x, fs, win=0.2, hop=0.05, T=DEADBAND):
    """Features over windows of `win` seconds every `hop` seconds; time stamps are the windows' ends."""
    W, H = int(win * fs), int(hop * fs)
    F = np.array([td_features(x[i:i + W], T) for i in range(0, len(x) - W + 1, H)])
    return (np.arange(len(F)) * H + W) / fs, F


def fig_features():
    t, x = emg_record()
    te, F = sliding(x, FS_EMG)
    _, F0 = sliding(x, FS_EMG, T=0.0)
    fig, (a1, a2) = plt.subplots(1, 2, figsize=FULL2)
    a1.plot(t, x * 1e3, color=PALE, lw=0.35, label="EMG (12 b, ±5 mV)")
    a1.plot(te, F[:, 1] * 1e3, color=C1, lw=1.4, label="RMS, 200 ms window")
    a1.plot(te, -F[:, 1] * 1e3, color=C1, lw=1.4)
    for k, (t0, a) in enumerate(((2.6, 0.22), (2.65, 0.12))):
        a1.axvspan(t0, t0 + 0.2, color=AMBER, alpha=a, lw=0)
    a1.annotate("", xy=(2.85, 0.86), xytext=(2.8, 0.86),
                arrowprops=dict(arrowstyle="-|>", lw=0.7, color=AMBERDK, mutation_scale=6))
    a1.text(2.62, 0.95, "200 ms window,\n50 ms hop", fontsize=6.3, color=AMBERDK, va="bottom")
    a1.set_xlim(0, 4); a1.set_ylim(-1.05, 1.35)
    finish(a1, xlabel="Time (s)", ylabel="EMG (mV)")
    a1.legend(loc="upper left", fontsize=6.0, ncol=1)
    panel(a1, "a")
    names = ("MAV", "WL", "ZC", "SSC")
    cols = (C1, C3, C4, C5)
    for j, n, c in zip((0, 2, 3, 4), names, cols):
        a2.plot(te, F[:, j] / F[:, j].max(), color=c, lw=1.2, label=n)
    a2.plot(te, F0[:, 3] / F[:, 3].max(), color=C4, lw=0.9, ls="--", label="ZC, no dead band")
    a2.set_xlim(0, 4); a2.set_ylim(0, 1.25)
    finish(a2, xlabel="Time (s), end of window", ylabel="Feature / maximum")
    a2.legend(loc="upper right", fontsize=6.0, ncol=3, columnspacing=0.8, handlelength=1.4)
    panel(a2, "b")
    savefig(fig, "ch26_features")


def latency(win, hop, n_off=40):
    """Delay from contraction onset to the first window end where MAV passes half-way from rest to plateau,
    over n_off onset positions spread across one hop. Returns (mean, max) in seconds."""
    W, H = int(win * FS_EMG), int(hop * FS_EMG)
    out = []
    for j in range(n_off):
        t0 = 0.5 + j * hop / n_off
        t, x = bs.emg(fs=FS_EMG, duration=2.0, bursts=((t0, 1.9),), seed=3 + j)
        a = np.abs(x)
        ends = np.arange(W, len(x) + 1, H)
        mav = np.array([a[e - W:e].mean() for e in ends]); te = ends / FS_EMG
        rest = a[:int((t0 - 0.1) * FS_EMG)].mean()
        plat = mav[(te > t0 + 0.4) & (te < 1.8)].mean()
        out.append(te[np.flatnonzero((mav > rest + 0.5 * (plat - rest)) & (te > t0 - 0.1))[0]] - t0)
    return np.mean(out), np.max(out)


def feature_engine(codes, block=100, nblk=4, T=8):
    """Streaming integer feature engine on one channel of integer codes: per sample |x|, the step d = x[n]-x[n-1],
    |d|, a dead-band compare, two sign XORs and four accumulations (11 operations, no multiplier). Sums are kept per
    block (block samples) and nblk blocks are added for each window. Returns the window sums (sum of magnitudes,
    WL, ZC, SSC) and the largest of each, to check word lengths. Window k covers samples [block*k, block*(k+nblk)),
    the same windows as sliding(); WL, ZC and SSC also count the step into the window's first sample."""
    n = len(codes) // block * block
    acc = np.zeros((n // block, 4), np.int64)
    xp, dp, bp = codes[0], 0, False
    for i in range(n):
        x = int(codes[i]); d = x - xp; ad = abs(d); b = ad >= T
        k = i // block
        acc[k, 0] += x if x >= 0 else ~x          # mid-rise magnitude |code + 1/2| - 1/2: a bitwise NOT, no adder
        acc[k, 1] += ad
        acc[k, 2] += ((x < 0) != (xp < 0)) and b
        acc[k, 3] += ((d < 0) != (dp < 0)) and d != 0 and dp != 0 and (b or bp)
        xp, dp, bp = x, d, b
    win = np.array([acc[k - nblk + 1:k + 1].sum(0) for k in range(nblk - 1, len(acc))])
    return win, np.abs(win).max(0)


# ------------------------------------------------------------------------------------------------ spikes
FS_SPK = 30000.0
NOISE_SPK = 8e-6              # background noise of the spike recordings (Chapter 2, Figure 2.4)
SPK_IN = 0.625e-3             # spike-mode input range: +-0.5 V at the SAR over a gain of 800 (Table 11.1)
DEAD = int(1e-3 * FS_SPK)     # 1 ms dead time after each detection


def _noise_gain(fs):
    """biosig.spikes() divides its band-pass noise by 0.37, which is not its rms at these rates (it is 0.61 at
    30 kS/s): measure the real gain so that the background is NOISE_SPK."""
    return bs.spikes(fs=fs, duration=60.0, amp=0.0, noise_rms=1.0, seed=99)[1].std()


_GAIN = {}


def spike_rec(amp=150e-6, duration=60.0, seed=4, rate=20.0, fs=FS_SPK, noise=NOISE_SPK):
    if fs not in _GAIN:
        _GAIN[fs] = _noise_gain(fs)
    return bs.spikes(fs=fs, duration=duration, rate=rate, amp=amp, noise_rms=noise / _GAIN[fs], seed=seed)


def sigma_hat(x):
    """Robust noise estimate: median(|x|)/0.6745 (the median of |x| is 0.6745 sigma for Gaussian noise)."""
    return np.median(np.abs(x)) / 0.6745


def neo(x, lag=1, L=5):
    """Nonlinear energy operator x[n]^2 - x[n-lag] x[n+lag], smoothed with an L-point Bartlett window."""
    p = np.zeros_like(x)
    p[lag:-lag] = x[lag:-lag] ** 2 - x[:-2 * lag] * x[2 * lag:]
    if L > 1:
        w = np.bartlett(L + 2)[1:-1]
        p = np.convolve(p, w / w.sum(), "same")
    return p


def detect(above, dead=DEAD):
    """Sample indices where `above` turns true, ignoring any within `dead` samples of the previous detection."""
    idx = np.flatnonzero(above[1:] & ~above[:-1]) + 1
    out, last = [], -10 ** 9
    for i in idx:
        if i - last >= dead:
            out.append(i); last = i
    return np.array(out, int)


def score(ev, times, duration, fs=FS_SPK, tol=0.6e-3):
    """Detection (% of spikes with an event within tol of the trough) and false alarms per second."""
    trough = times + 0.5e-3                        # biosig.spikes() templates start 0.5 ms before the trough
    hit = np.zeros(len(trough), bool); fa = 0
    for e in ev / fs:
        k = np.argmin(np.abs(trough - e))
        if abs(trough[k] - e) < tol:
            hit[k] = True
        else:
            fa += 1
    return hit.mean() * 100, fa / duration


def roc(stat, thresholds, times, duration):
    return np.array([score(detect(stat > th), times, duration) for th in thresholds])


def at_fa(r, target):
    """Detection (%) at a false-alarm rate, interpolated on a log axis."""
    o = np.argsort(r[:, 1])
    return np.interp(np.log(target), np.log(np.maximum(r[o, 1], 1e-3)), r[o, 0])


SPK_SMALL = 50e-6             # nominal amplitude for the small-spike study: troughs 35-50 uV (biosig scales 0.7-1)


_ROCS = {}


def spike_rocs(duration=400.0):
    if duration in _ROCS:
        return _ROCS[duration]
    t, x, tm = spike_rec(SPK_SMALL, duration)
    s = sigma_hat(x)
    out = {"amp": (roc(-x, np.linspace(2.5, 6.5, 41) * s, tm, duration), np.linspace(2.5, 6.5, 41))}
    for lag in (1, 5):
        p = neo(x, lag)
        q = np.quantile(p, [0.9, 0.99999])
        th = np.geomspace(q[0], q[1] * 3, 60)
        out[f"neo{lag}"] = (roc(p, th, tm, duration), th)
    _ROCS[duration] = (t, x, tm, s, out)
    return _ROCS[duration]


def fig_spikes():
    t, x, tm, s, R = spike_rocs()
    fig = plt.figure(figsize=FULL)
    gs = fig.add_gridspec(2, 2, height_ratios=(1.3, 1), width_ratios=(1.15, 1))
    a1 = fig.add_subplot(gs[0, 0]); a3 = fig.add_subplot(gs[1, 0], sharex=a1); a2 = fig.add_subplot(gs[:, 1])
    # a 60 ms stretch with several spikes
    w = 0.06
    starts = np.arange(0.5, t[-1] - w, 0.005)
    best = starts[np.argmax([np.sum((tm > s0 + 0.002) & (tm < s0 + w - 0.004)) for s0 in starts])]
    m = (t >= best) & (t < best + w)
    tt = (t[m] - best) * 1e3
    a1.plot(tt, x[m] * 1e6, color=GRAPHITE, lw=0.6)
    a1.axhline(-4.5 * s * 1e6, color=C3, ls="--", lw=0.9)
    a1.text(w * 1e3, -4.5 * s * 1e6 - 4, r"$-4.5\hat\sigma$", fontsize=6.5, color=C3, ha="right", va="top")
    for ts in tm[(tm > best) & (tm < best + w)]:
        a1.plot((ts + 0.5e-3 - best) * 1e3, 32, "v", color=C4, ms=3.5)
    a1.set_ylim(-72, 42)
    finish(a1, ylabel="Signal (µV)")
    plt.setp(a1.get_xticklabels(), visible=False)
    panel(a1, "a")
    for lag, c, off in ((1, C2, 0.0), (5, C1, 1.6)):
        r, th = R[f"neo{lag}"]
        thr = th[np.argmin(np.abs(np.log(np.maximum(r[:, 1], 1e-3)) - np.log(1.0)))]   # threshold for ~1 false alarm/s
        p = neo(x, lag)[m] / thr
        a3.plot(tt, off + np.clip(p, 0, 1.45), color=c, lw=0.8)
        a3.axhline(off + 1, color=c, ls=":", lw=0.7)
        a3.text(26, off + 1.08, f"NEO, lag {lag}", fontsize=6.3, color=c, va="bottom")
    a3.set_ylim(-0.1, 3.2); a3.set_yticks([])
    a3.set_xlim(0, w * 1e3)
    finish(a3, xlabel="Time (ms)", ylabel="ψ / threshold")
    ra, ka = R["amp"]
    a2.semilogx(np.maximum(ra[:, 1], 1e-3), ra[:, 0], color=C3, lw=1.3, label="amplitude, $-k\\hat\\sigma$")
    for k in (3.5, 4.0, 4.5, 5.0):
        i = np.argmin(np.abs(ka - k))
        if ra[i, 1] < 0.01:
            continue
        a2.plot(max(ra[i, 1], 1e-3), ra[i, 0], "o", mfc="white", mec=C3, mew=1.0, ms=3.8, zorder=4)
        a2.text(max(ra[i, 1], 1e-3) * 1.3, ra[i, 0] - 4, f"{k:g}σ", fontsize=6.3, color=C3, va="top")
    for lag, c in ((5, C1), (1, C2)):
        r = R[f"neo{lag}"][0]
        o = np.argsort(r[:, 1])
        a2.semilogx(np.maximum(r[o, 1], 1e-3), r[o, 0], color=c, lw=1.3, label=f"NEO, lag {lag}")
    a2.set_xlim(0.01, 100); a2.set_ylim(0, 102)
    finish(a2, xlabel="False alarms per second", ylabel="Spikes detected (%)")
    a2.legend(loc="lower right", fontsize=6.3)
    panel(a2, "b")
    savefig(fig, "ch26_spikes")
    return R


def numbers():
    from scipy import stats
    print("== EMG envelope and features (biosig.emg, 12 b over +-5 mV, 3.4 uVrms noise)")
    t, x = emg_record()
    te, F = sliding(x, FS_EMG)
    _, F0 = sliding(x, FS_EMG, T=0.0)
    rest, act = (te > 0.25) & (te < 0.45), (te > 0.9) & (te < 1.4)
    for lab, mm in (("rest", rest), ("contraction", act)):
        print("  %-11s MAV %.1f uV RMS %.1f uV WL %.2f mV ZC %.1f SSC %.1f | no dead band ZC %.1f SSC %.1f"
              % (lab, F[mm, 0].mean() * 1e6, F[mm, 1].mean() * 1e6, F[mm, 2].mean() * 1e3, F[mm, 3].mean(),
                 F[mm, 4].mean(), F0[mm, 3].mean(), F0[mm, 4].mean()))
    print("  RMS/MAV in contraction %.3f (sqrt(pi/2) = %.3f)" % (F[act, 1].mean() / F[act, 0].mean(), np.sqrt(np.pi / 2)))
    print("  ZC rate in contraction %.0f /s -> mean frequency ~ %.0f Hz" % (F[act, 3].mean() / 0.2, F[act, 3].mean() / 0.4))
    print("== Envelope noise: CV of MAV in a steady contraction")
    _, xs = bs.emg(fs=FS_EMG, duration=60.0, bursts=((0.0, 61.0),), seed=11)
    for w_ms in (25, 50, 100, 200, 300):
        W = int(w_ms * FS_EMG / 1000); n = len(xs) // W
        mv = np.abs(xs[:n * W]).reshape(n, W).mean(1)
        print("  %3d ms: %.1f %%" % (w_ms, mv.std() / mv.mean() * 100))
    print("== Latency to half the step (simulated mean/max; analytic W/2 + H/2 and W/2 + H)")
    for win, hop in ((0.2, 0.2), (0.2, 0.1), (0.2, 0.05), (0.1, 0.025)):
        mu, mx = latency(win, hop)
        print("  W %3.0f ms H %3.0f ms: %3.0f / %3.0f ms (analytic %3.0f / %3.0f) decisions/s %2.0f"
              % (win * 1e3, hop * 1e3, mu * 1e3, mx * 1e3, (win + hop) / 2 * 1e3, (win / 2 + hop) * 1e3, 1 / hop))
    print("== Feature engine: integer check and word lengths (8-bit and 12-bit codes over +-5 mV, 1 mV peak EMG)")
    for bits in (8, 12):
        lsb = 2 * FS_IN / 2 ** bits
        codes = np.floor(np.clip(x, -FS_IN, FS_IN * (1 - 2.0 ** (1 - bits))) / lsb).astype(int)
        T = max(1, int(round(DEADBAND / lsb)))
        win, mx = feature_engine(codes, T=T)
        ref = np.array([td_features((codes[i:i + 400] + 0.5) * lsb, T * lsb - 1e-12) for i in range(0, len(codes) - 399, 100)])
        k = min(len(ref), len(win))
        print("  %2d b: integer vs floating MAV max error %.1e (relative); ZC, SSC differ by at most %d, %d counts"
              % (bits, np.max(np.abs((win[:k, 0] + 0.5 * 400) * lsb / 400 / ref[:k, 0] - 1)),
                 np.max(np.abs(win[:k, 2] - ref[:k, 3])), np.max(np.abs(win[:k, 3] - ref[:k, 4]))))
        print("  %2d b: dead band %d LSB; largest window sums MAV*N %d WL %d ZC %d SSC %d; worst-case bounds %d / %d bits"
              % (bits, T, *mx, int(np.ceil(np.log2(400 * 2 ** (bits - 1)))), int(np.ceil(np.log2(400 * (2 ** bits - 1))))))
    ops = 11
    print("  operations/sample %d -> %.0f k/s per channel, %.0f k/s for 8 channels; window sums %.0f ops/s"
          % (ops, ops * FS_EMG / 1e3, 8 * ops * FS_EMG / 1e3, 8 * 4 * 3 * 20))
    print("  at 1 pJ/operation: %.2f uW" % (8 * ops * FS_EMG * 1e-12 * 1e6))
    raw = 8 * FS_EMG * 12
    for lab, r in (("features 5/s", 8 * 4 * 16 * 5), ("features 20/s", 8 * 4 * 16 * 20), ("labels 20/s", 3 * 20)):
        print("  raw %.0f kb/s vs %s %.2f kb/s: %.0fx; radio at 5 nJ/b %.1f vs %.2f uW"
              % (raw / 1e3, lab, r / 1e3, raw / r, raw * 5e-9 * 1e6, r * 5e-9 * 1e6))
    print("  LDA on chip: 5 classes x 32 features = %d MAC per decision, %d MAC/s at 20/s" % (5 * 32, 5 * 32 * 20))
    print("== Spike noise estimate (30 kS/s, 8 uVrms background)")
    t, x, tm = spike_rec(150e-6)
    print("  biosig.spikes() noise gain at 30 kS/s %.3f (requested noise x %.2f)" % (_GAIN[FS_SPK], _GAIN[FS_SPK]))
    print("  %d spikes in 60 s (%.1f /s), troughs 105-150 uV: std %.2f uV, median estimate %.2f uV"
          % (len(tm), len(tm) / 60, x.std() * 1e6, sigma_hat(x) * 1e6))
    s = sigma_hat(x)
    for k in (4.0, 4.5, 5.0):
        print("  k=%.1f: threshold %.1f uV (median) vs %.1f uV (std); detection of these spikes %.1f %%"
              % (k, k * s * 1e6, k * x.std() * 1e6, score(detect(-x > k * s), tm, 60.0)[0]))
    print("== False alarms on noise alone (120 x 10 s), R_FA ~ fs Q(k), Rice nu0 exp(-k^2/2)")
    from scipy import signal as sps
    for fs in (20000.0, 30000.0):
        b, a = sps.butter(2, [300, 7000], btype="band", fs=fs)
        f, h = sps.freqz(b, a, worN=2 ** 16, fs=fs)
        S = np.abs(h) ** 4                                    # filtfilt
        nu0 = np.sqrt(np.trapz(f ** 2 * S, f) / np.trapz(S, f))
        ks = (4.0, 4.5, 5.0); n = np.zeros(3); T = 0.0
        for sd in range(120):
            _, xn, _ = spike_rec(0.0, 10.0, seed=2000 + sd, fs=fs)
            T += 10.0
            for i, k in enumerate(ks):
                n[i] += len(detect(-xn > k * NOISE_SPK, dead=int(1e-3 * fs)))
        print("  fs %.0f kS/s, nu0 %.0f Hz" % (fs / 1e3, nu0))
        for i, k in enumerate(ks):
            print("    k=%.1f: simulated %.3f /s (n=%d)  fs*Q(k) %.3f  Rice %.3f  Q(k) %.2e  mean excursion %.1f us"
                  % (k, n[i] / T, n[i], fs * stats.norm.sf(k), nu0 * np.exp(-k * k / 2), stats.norm.sf(k),
                     stats.norm.sf(k) / (nu0 * np.exp(-k * k / 2)) * 1e6))
    print("== Small spikes (troughs 35-50 uV): amplitude threshold vs NEO")
    t, x, tm, s, R = spike_rocs()
    dur = len(x) / FS_SPK
    print("  %.0f s, %d spikes, sigma_hat %.2f uV" % (dur, len(tm), s * 1e6))
    for k in (3.5, 4.0, 4.5, 5.0):
        d, fa = score(detect(-x > k * s), tm, dur)
        print("  amplitude %.1f sigma: %.1f %% at %.2f FA/s" % (k, d, fa))
    for key in ("amp", "neo1", "neo5"):
        print("  %-5s detection at 1 FA/s %.1f %%, at 0.1 FA/s %.1f %%" % (key, at_fa(R[key][0], 1.0), at_fa(R[key][0], 0.1)))
    r1 = roc(neo(x, 1, 1), np.geomspace(*np.quantile(neo(x, 1, 1), [0.9, 0.99999]), 60), tm, dur)
    print("  neo1 unsmoothed: at 1 FA/s %.1f %%" % at_fa(r1, 1.0))
    fs2, d2 = 20000.0, 120.0
    t2, x2, tm2 = spike_rec(SPK_SMALL, d2, fs=fs2)
    for lag in (1, 2, 3, 4, 5):
        p = neo(x2, lag); q = np.quantile(p, [0.9, 0.99999])
        r = np.array([score(detect(p > th, int(1e-3 * fs2)), tm2, d2, fs=fs2) for th in np.geomspace(q[0], q[1] * 3, 50)])
        print("  20 kS/s, NEO lag %d: detection at 1 FA/s %.1f %%, at 0.1 FA/s %.1f %%" % (lag, at_fa(r, 1.0), at_fa(r, 0.1)))
    tt = np.arange(-0.5e-3, 1.5e-3, 1 / FS_SPK)
    tmpl = -np.exp(-0.5 * (tt / 0.12e-3) ** 2) + 0.35 * np.exp(-0.5 * ((tt - 0.45e-3) / 0.25e-3) ** 2)
    tmpl = 50e-6 * tmpl / -tmpl.min()
    for lag in (1, 5):
        print("  50 uV spike: peak psi lag %d = %.2e V^2 = %.1f sigma^2; noise mean psi = %.2f sigma^2"
              % (lag, neo(tmpl, lag, 1).max(), neo(tmpl, lag, 1).max() / NOISE_SPK ** 2,
                 neo(spike_rec(0.0, 10.0)[1], lag, 1).mean() / NOISE_SPK ** 2))
    om = 2 * np.pi * 10 / FS_SPK
    print("  100 uV LFP at 10 Hz: psi = A^2 sin^2(w) = %.1e V^2" % ((100e-6) ** 2 * np.sin(om) ** 2))
    print("== Running median of |x| on chip: m += delta*sign(|x| - m), 12-bit codes over +-0.625 mV")
    t, x, tm = spike_rec(150e-6, 10.0)
    a = np.abs(np.floor(x / (2 * SPK_IN / 4096)) + 0.5)
    tgt = np.median(a)
    for sh in (6, 8, 10):
        d = 2.0 ** -sh; m = 0.0; tr = np.empty(len(a))
        for i, v in enumerate(a):
            m += d if v > m else -d
            tr[i] = m
        k = np.flatnonzero(np.abs(tr - tgt) < 0.05 * tgt)[0]
        ss = tr[int(2 * FS_SPK):]
        print("  delta 2^-%d LSB: within 5 %% after %.2f s, then %.1f %% rms (median %.1f LSB = %.2f uV sigma)"
              % (sh, k / FS_SPK, ss.std() / tgt * 100, tgt, tgt / 0.6745 * 2 * SPK_IN / 4096 * 1e6))
    print("== What leaves the chip in spike mode (one channel)")
    rate = len(spike_rec(150e-6)[2]) / 60.0
    for fs, b in ((30000, 12), (20000, 10)):
        print("  raw %d kS/s x %d b = %.0f kb/s" % (fs / 1e3, b, fs * b / 1e3))
    for lab, bits_per in (("times only (32 b)", 32), ("times + 16 x 12 b", 32 + 16 * 12), ("times + 48 x 8 b (1.6 ms)", 32 + 48 * 8)):
        for r in (rate, 30.0):
            print("  %-26s at %4.1f spikes/s: %.2f kb/s, %.0fx less than 360 kb/s"
                  % (lab, r, r * bits_per / 1e3, 360e3 / (r * bits_per)))
    print("  8-bit snippet over +-0.625 mV: LSB %.2f uV, LSB/sqrt12 %.2f uV vs 8 uV noise" % (2 * SPK_IN / 256 * 1e6, 2 * SPK_IN / 256 / np.sqrt(12) * 1e6))
    print("  ten channels raw at 30 kS/s, 10 b: %.1f Mb/s; events %.0f samples per spike" % (10 * 30e3 * 10 / 1e6, 30000 / rate))


if __name__ == "__main__":
    if sys.argv[1:] == ["numbers"]:
        numbers(); sys.exit()
    fig()
    fig_features()
    fig_spikes()
    numbers()
    for fs in (500.0, 1000.0, 2000.0):
        print(fs, " ".join("%d:%.1f" % (b, np.mean([accuracy(b, fs, seed=s) for s in range(2)])) for b in (3, 4, 5, 6, 8, 12)))
