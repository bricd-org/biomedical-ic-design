"""Lab 12 -- EEG seizure detection (Open-BioAFE, Chapters 25 and 27).

Band-power features per 2 s window, two detectors (a threshold on theta power, as in Chapter 25,
and a linear discriminant on log band powers trained on other records), and what reducing the
converter's word length and sample rate costs in accuracy, latency and a power proxy.

    python lab12_eeg_seizure.py                       # synthetic EEG with rhythmic discharges
    python lab12_eeg_seizure.py --chbmit chb01_03.edf --seizure 2996 3036

The CHB-MIT option reads a local EDF file with wfdb (seizure onset and end in seconds come from
the record's summary file on PhysioNet). Outputs go to labs/python/out/ (git-ignored).
"""
import argparse
import os
import sys
import warnings

import numpy as np
from scipy import signal as sps

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import biosig  # noqa: E402

OUT = os.path.join(HERE, "out")
warnings.filterwarnings("ignore", message="Mean of empty slice")
FS = 256.0
VFS = 0.625e-3          # EEG gain 800 maps +-0.625 mV at the electrodes onto the converter (Table 11.1)
WIN = 2.0
BANDS = {"delta": (0.5, 3), "theta": (3, 8), "alpha": (8, 13), "beta": (13, 30)}


def synthetic(seed, dur=120.0):
    """Two minutes of synthetic EEG with three 10 s rhythmic discharges (3-6 Hz, 60 µV), as in
    Chapter 25. Returns (x, fs, events [(onset, end) in s])."""
    t, x = biosig.eeg(fs=FS, duration=dur, seed=seed)[:2]
    rng = np.random.default_rng(seed)
    ev = []
    for start in sorted(rng.choice(np.arange(5, int(dur / WIN) - 10), 3, replace=False)):
        s0 = start * WIN
        m = (t >= s0) & (t < s0 + 10.0)
        f0 = rng.uniform(3, 6)
        env = np.sin(np.pi * (t[m] - s0) / 10.0)
        ph = np.sin(2 * np.pi * f0 * t[m])
        x[m] += 60e-6 * env * np.sign(ph) * np.abs(ph) ** 0.5
        ev.append((s0, s0 + 10.0))
    return x, FS, ev


def chbmit(path, sz):
    import wfdb
    rec = wfdb.rdrecord(path)
    k = rec.sig_name.index("F7-T7") if "F7-T7" in rec.sig_name else 0
    scale = {"uv": 1e-6, "mv": 1e-3}.get(str(rec.units[k]).lower(), 1.0)
    return rec.p_signal[:, k] * scale, float(rec.fs), [tuple(sz)]


def converter(x, fs, bits, noise, q, seed):
    """Input noise, anti-alias and decimate by q (the converter runs at fs/q), quantise."""
    rng = np.random.default_rng(seed)
    y = x + noise * rng.standard_normal(len(x))
    if q > 1:
        y = sps.resample_poly(y, 1, q)
    return biosig.quantize(y, bits, VFS), fs / q


def features(y, fs):
    """Per 2 s window: line length and the log power in each band."""
    n = int(WIN * fs)
    k = len(y) // n
    seg = y[: k * n].reshape(k, n)
    f, p = sps.welch(seg, fs=fs, nperseg=n, axis=1)
    bp = np.array([p[:, (f >= lo) & (f < hi)].sum(axis=1) for lo, hi in BANDS.values()]).T
    ll = np.sum(np.abs(np.diff(seg, axis=1)), axis=1)
    return ll, np.log10(bp + 1e-30)


def labels(n_win, events):
    lab = np.zeros(n_win, bool)
    for s0, s1 in events:
        lab[int(s0 // WIN): int(np.ceil(s1 / WIN))] = True
    return lab


def evaluate(pred, events, dur):
    """Event sensitivity, mean latency (s) and false detections per hour (runs outside events)."""
    lab = labels(len(pred), events)
    hit, lat = 0, []
    for s0, s1 in events:
        i0, i1 = int(s0 // WIN), int(np.ceil(s1 / WIN))
        w = np.nonzero(pred[i0:i1])[0]
        if len(w):
            hit += 1
            lat.append((i0 + w[0] + 1) * WIN - s0)
    fp = pred & ~lab
    runs = np.sum(fp[1:] & ~fp[:-1]) + int(fp[0])
    return hit / len(events), (np.mean(lat) if lat else np.nan), runs / (dur / 3600), np.mean(pred == lab)


def lda_fit(f, lab):
    m0, m1 = f[~lab].mean(0), f[lab].mean(0)
    s = np.cov(f[~lab].T) + np.cov(f[lab].T) + 1e-6 * np.eye(f.shape[1])
    w = np.linalg.solve(s, m1 - m0)
    return w, w @ (m0 + m1) / 2


def main():
    ap = argparse.ArgumentParser(description="Lab 12: EEG seizure detection")
    ap.add_argument("--chbmit", help="local CHB-MIT .edf file")
    ap.add_argument("--seizure", nargs=2, type=float, default=(2996, 3036), help="onset and end (s)")
    ap.add_argument("--noise", type=float, default=1.5e-6, help="input noise (Vrms)")
    args = ap.parse_args()
    os.makedirs(OUT, exist_ok=True)
    lines = []

    def say(s=""):
        print(s)
        lines.append(s)

    if args.chbmit:
        try:
            recs = [chbmit(args.chbmit, args.seizure)]
            train, test = recs, recs
            say(f"Source: {args.chbmit}, one seizure at {args.seizure[0]:g}-{args.seizure[1]:g} s (train = test: optimistic)")
        except Exception as e:
            print(f"CHB-MIT load failed ({e.__class__.__name__}: {e}); using synthetic records")
            args.chbmit = None
    if not args.chbmit:
        train = [synthetic(s) for s in (100, 101)]
        test = [synthetic(s) for s in (102, 103, 104, 105)]
        say("Source: synthetic EEG, 2 min per record, 3 discharges each; LDA trained on 2 records, tested on 4")

    # train the LDA at full resolution
    ftr, ltr = [], []
    for x, fs, ev in train:
        y, fsc = converter(x, fs, 12, args.noise, 1, 0)
        _, bp = features(y, fsc)
        ftr.append(bp); ltr.append(labels(len(bp), ev))
    w, b0 = lda_fit(np.vstack(ftr), np.concatenate(ltr))

    say(f"Window accuracy / event sensitivity / latency / false detections per hour, input noise {args.noise*1e6:g} µVrms")
    say("   bits  fs (S/s)  power proxy   theta threshold (3x median)          LDA on log band powers")
    rows = []
    for bits, q in ((12, 1), (8, 1), (6, 1), (4, 1), (12, 2), (12, 4), (6, 4)):
        res = {"thr": [], "lda": [], "ll": []}
        for i, (x, fs, ev) in enumerate(test):
            y, fsc = converter(x, fs, bits, args.noise, q, i)
            ll, bp = features(y, fsc)
            dur = len(y) / fsc
            th = bp[:, 1]
            res["thr"].append(evaluate(th > np.log10(3.0) + np.median(th), ev, dur))
            res["lda"].append(evaluate(bp @ w > b0, ev, dur))
            res["ll"].append(evaluate(ll > 3.0 * np.median(ll), ev, dur))
        proxy = (fs / q / FS) * 2.0 ** (bits - 12)
        t_ = np.nanmean(res["thr"], axis=0); l_ = np.nanmean(res["lda"], axis=0)
        rows.append((bits, fs / q, proxy, t_, l_, np.nanmean(res["ll"], axis=0)))
        say(f"   {bits:4d}  {fs/q:8.0f}  {proxy:10.3f}   "
            f"{t_[3]*100:5.1f} % {t_[0]*100:4.0f} % {t_[1]:4.1f} s {t_[2]:5.0f}/h    "
            f"{l_[3]*100:5.1f} % {l_[0]*100:4.0f} % {l_[1]:4.1f} s {l_[2]:5.0f}/h")
    say(f"   line length (3x median) at 12 bits, 256 S/s: window accuracy {rows[0][5][3]*100:.1f} %, "
        f"{rows[0][5][2]:.0f} false detections per hour")

    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        x, fs, ev = test[0]
        y, fsc = converter(x, fs, 12, args.noise, 1, 0)
        ll, bp = features(y, fsc)
        fig, (a1, a2) = plt.subplots(1, 2, figsize=(11, 4.2), constrained_layout=True)
        tw = (np.arange(len(bp)) + 0.5) * WIN
        a1.plot(np.arange(len(y)) / fsc, y * 1e6 / 2 + 150, lw=0.4, color="0.4", label="EEG (µV / 2, offset)")
        a1.plot(tw, (bp[:, 1] - np.median(bp[:, 1])) * 40, "o-", ms=3, label="log theta power (×40, median removed)")
        a1.axhline(np.log10(3.0) * 40, color="C3", ls="--", lw=0.8, label="threshold: 3 × median")
        for s0, s1 in ev:
            a1.axvspan(s0, s1, color="C1", alpha=0.15)
        a1.set(xlabel="time (s)", title="(a) theta power flags the discharges (shaded)")
        a1.legend(fontsize=7, loc="lower right")
        b_ = [f"{r[0]} b\n{r[1]:.0f} S/s" for r in rows]
        a2.plot(range(len(rows)), [r[3][3] * 100 for r in rows], "o-", label="theta threshold")
        a2.plot(range(len(rows)), [r[4][3] * 100 for r in rows], "s--", label="LDA, band powers")
        a2.set_xticks(range(len(rows))); a2.set_xticklabels(b_, fontsize=7)
        a2.set(ylabel="window accuracy (%)", title="(b) accuracy against word length and sample rate", ylim=(70, 101))
        a2.legend(fontsize=8)
        fig.savefig(os.path.join(OUT, "lab12_eeg_seizure.png"), dpi=130)
        say(f"\nwrote {os.path.join(OUT, 'lab12_eeg_seizure.png')}")
    except ImportError:
        pass
    with open(os.path.join(OUT, "lab12_summary.txt"), "w") as fh:
        fh.write("\n".join(lines) + "\n")


if __name__ == "__main__":
    main()
