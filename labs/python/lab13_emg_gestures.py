"""Lab 13 -- EMG gesture recognition (Open-BioAFE, Chapter 26).

Time-domain features (MAV, WL, ZC, SSC) per channel over 200 ms windows, a linear discriminant,
and accuracy against the number of channels, the sample rate and the converter resolution; then
the same classifier in fixed point (integer features, a Mitchell log2, 8-bit weights), and the
effect of an electrode shift between training and use.

    python lab13_emg_gestures.py                       # synthetic 8-channel EMG, 5 gestures (Chapter 26)
    python lab13_emg_gestures.py --ninapro S1_E1_A1.mat

NinaPro: the .mat file's 'emg' (samples x channels), 'restimulus' (gesture per sample, 0 = rest)
and 'rerepetition' arrays are used; repetitions 2 and 5 are the test set, as in the NinaPro papers.
Outputs go to labs/python/out/ (git-ignored).
"""
import argparse
import os
import sys

import numpy as np
from scipy import signal as sps

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import biosig  # noqa: E402

OUT = os.path.join(HERE, "out")
VFS = 5e-3                       # EMG mode: gain 10 x 8 maps +-5 mV onto the converter (Table 11.1)
CH, G = 8, 5
PATTERN = np.random.default_rng(26).uniform(0.05, 1.0, (G, CH)) * 0.6e-3   # rms per gesture and channel


def window(g, fs, rng, dur=0.2, shift=0.0):
    """One synthetic 200 ms trial of gesture g (as in Chapter 26). shift mixes each channel with its
    neighbours, as when the electrode band is put back on rotated."""
    n = int(dur * fs)
    sos = sps.butter(4, [20, min(450, 0.45 * fs)], "band", fs=fs, output="sos")
    x = sps.sosfilt(sos, rng.standard_normal((CH, n + 200)), axis=1)[:, 200:]
    x = x / x.std(axis=1, keepdims=True)
    amp = PATTERN[g] * rng.uniform(0.75, 1.25, CH) * rng.uniform(0.7, 1.3)
    if shift:
        amp = (1 - shift) * amp + shift * np.roll(amp, 1)
    return x * amp[:, None] + 3e-6 * rng.standard_normal((CH, n))


def feats(c, thr):
    """Features from integer codes c (channels x samples); thr in LSB. Returns integers."""
    mav = np.sum(np.abs(c), axis=1)
    wl = np.sum(np.abs(np.diff(c, axis=1)), axis=1)
    zc = np.sum((c[:, :-1] * c[:, 1:] < 0) & (np.abs(c[:, :-1] - c[:, 1:]) > thr), axis=1)
    d1, d2 = c[:, 1:-1] - c[:, :-2], c[:, 1:-1] - c[:, 2:]
    ssc = np.sum((d1 * d2 > 0) & ((np.abs(d1) > thr) | (np.abs(d2) > thr)), axis=1)
    return mav, wl, zc, ssc


def to_vector(f, n, fixed=False):
    mav, wl, zc, ssc = (np.asarray(v, float) for v in f)
    if fixed:            # Mitchell's log2: position of the leading one plus the remaining fraction
        lg = lambda v: np.where(v > 0, np.floor(np.log2(np.maximum(v, 1))) + v / 2 ** np.floor(np.log2(np.maximum(v, 1))) - 1, 0)
    else:
        lg = lambda v: np.log2(v + 1e-9)
    return np.concatenate([lg(mav), lg(wl), zc / n, ssc / n])


def codes(w, bits):
    """Signed integer codes of an N-bit converter over +-VFS."""
    lsb = 2 * VFS / 2 ** bits
    return np.clip(np.floor(w / lsb), -2 ** (bits - 1), 2 ** (bits - 1) - 1).astype(np.int64)


def lda_fit(X, y):
    """LDA with a shared covariance on standardised features (offsets and scales stored with the
    model, as a fixed-point implementation would subtract and shift them)."""
    m, sd = X.mean(0), X.std(0) + 1e-12
    Z = (X - m) / sd
    k = np.unique(y)
    mu = np.array([Z[y == c].mean(0) for c in k])
    S = sum(np.cov(Z[y == c].T) for c in k) / len(k) + 1e-6 * np.eye(Z.shape[1])
    W = np.linalg.solve(S, mu.T).T                      # linear discriminants g_k = W_k.z + b_k
    b = -0.5 * np.sum(W * mu, axis=1)
    return k, W, b, m, sd


def lda_predict(model, X, wbits=None):
    k, W, b, m, sd = model
    if wbits:                                            # quantise weights to wbits signed; b on the same grid
        s = (2 ** (wbits - 1) - 1) / np.abs(W).max()
        W, b = np.round(W * s) / s, np.round(b * s) / s
    return k[np.argmax(((X - m) / sd) @ W.T + b, axis=1)]


def synth_set(n_per, bits, fs, nch, rng, fixed=False, shift=0.0):
    X, y = [], []
    lsb = 2 * VFS / 2 ** bits
    for g in range(G):
        for _ in range(n_per):
            c = codes(window(g, fs, rng, shift=shift), bits)[:nch]
            X.append(to_vector(feats(c, 10e-6 / lsb), c.shape[1], fixed)); y.append(g)
    return np.array(X), np.array(y)


def ninapro(path, bits, fs_div, fixed):
    from scipy.io import loadmat
    m = loadmat(path)
    emg = np.asarray(m["emg"], float)[::fs_div]
    lab = np.squeeze(m["restimulus"])[::fs_div]
    rep = np.squeeze(m["rerepetition"])[::fs_div]
    fs = float(np.squeeze(m.get("frequency", 2000.0))) / fs_div
    n = int(0.2 * fs)
    scale = VFS / np.percentile(np.abs(emg), 99.9)       # fit the converter range to the recording
    Xtr, ytr, Xte, yte = [], [], [], []
    lsb = 2 * VFS / 2 ** bits
    for i in range(0, len(emg) - n, n // 2):             # 200 ms windows, 50 % overlap
        g, r = lab[i + n // 2], rep[i + n // 2]
        if g == 0 or lab[i] != g or lab[i + n - 1] != g:
            continue
        c = codes(emg[i:i + n].T * scale, bits)
        v = to_vector(feats(c, 10e-6 / lsb), n, fixed)
        (Xte if r in (2, 5) else Xtr).append(v); (yte if r in (2, 5) else ytr).append(g)
    return np.array(Xtr), np.array(ytr), np.array(Xte), np.array(yte)


def main():
    ap = argparse.ArgumentParser(description="Lab 13: EMG gesture recognition")
    ap.add_argument("--ninapro", help="local NinaPro .mat file")
    args = ap.parse_args()
    os.makedirs(OUT, exist_ok=True)
    lines = []

    def say(s=""):
        print(s)
        lines.append(s)

    if args.ninapro:
        try:
            say(f"NinaPro {os.path.basename(args.ninapro)}: accuracy (%) on repetitions 2 and 5")
            for bits in (4, 6, 8, 12):
                for div in (1, 2, 4):
                    Xtr, ytr, Xte, yte = ninapro(args.ninapro, bits, div, False)
                    acc = np.mean(lda_predict(lda_fit(Xtr, ytr), Xte) == yte) * 100
                    say(f"   {bits:2d} bits, {2000/div:5.0f} S/s: {acc:5.1f} %  ({len(np.unique(ytr))} gestures)")
            return
        except Exception as e:
            print(f"NinaPro load failed ({e.__class__.__name__}: {e}); using synthetic EMG")

    rng = np.random.default_rng(13)
    grid = {}
    say("1. Synthetic EMG, 5 gestures, 40 training and 40 test trials each: accuracy (%)")
    say("   channels  fs (S/s) " + " ".join(f"{b:>6d} b" for b in (3, 4, 5, 6, 8, 12)))
    for nch in (2, 4, 8):
        for fs in (500.0, 1000.0, 2000.0):
            row = []
            for bits in (3, 4, 5, 6, 8, 12):
                Xtr, ytr = synth_set(40, bits, fs, nch, rng)
                Xte, yte = synth_set(40, bits, fs, nch, rng)
                row.append(np.mean(lda_predict(lda_fit(Xtr, ytr), Xte) == yte) * 100)
            grid[(nch, fs)] = row
            say(f"   {nch:8d}  {fs:8.0f} " + " ".join(f"{a:7.1f}" for a in row))

    say("2. Fixed point, 8 channels, 1 kS/s, 8 bits: integer features, Mitchell log2, quantised weights")
    Xtr, ytr = synth_set(40, 8, 1000.0, 8, rng, fixed=True)
    Xte, yte = synth_set(40, 8, 1000.0, 8, rng, fixed=True)
    mdl = lda_fit(Xtr, ytr)
    for wb in (None, 8, 6, 4):
        acc = np.mean(lda_predict(mdl, Xte, wb) == yte) * 100
        say(f"   weights {'float' if wb is None else str(wb) + ' bits':>8}: {acc:5.1f} %")

    say("3. Electrode shift between training and use (8 channels, 1 kS/s, 8 bits):")
    Xtr, ytr = synth_set(40, 8, 1000.0, 8, rng)
    mdl = lda_fit(Xtr, ytr)
    for sh in (0.0, 0.2, 0.4, 0.6):
        Xte, yte = synth_set(40, 8, 1000.0, 8, rng, shift=sh)
        say(f"   shift {sh:.1f}: {np.mean(lda_predict(mdl, Xte) == yte) * 100:5.1f} %")

    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        fig, ax = plt.subplots(figsize=(6.5, 4.2), constrained_layout=True)
        for (nch, fs), row in grid.items():
            if fs == 1000.0:
                ax.plot((3, 4, 5, 6, 8, 12), row, "o-", label=f"{nch} channels, 1 kS/s")
        ax.plot((3, 4, 5, 6, 8, 12), grid[(8, 500.0)], "s--", label="8 channels, 500 S/s")
        ax.axhline(100 / G, color="0.5", ls=":", lw=0.8, label="chance")
        ax.set(xlabel="ADC bits (±5 mV range)", ylabel="accuracy (%)", title="Gesture accuracy, synthetic EMG", ylim=(0, 102))
        ax.legend(fontsize=8)
        fig.savefig(os.path.join(OUT, "lab13_emg_gestures.png"), dpi=130)
        say(f"\nwrote {os.path.join(OUT, 'lab13_emg_gestures.png')}")
    except ImportError:
        pass
    with open(os.path.join(OUT, "lab13_summary.txt"), "w") as fh:
        fh.write("\n".join(lines) + "\n")


if __name__ == "__main__":
    main()
