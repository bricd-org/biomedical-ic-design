"""ch26_figs.py -- Chapter 26 figure: time-domain EMG features and gesture classification. Synthetic
8-channel surface EMG for five gestures (each a fixed pattern of channel amplitudes with trial-to-trial
variation), features MAV, WL, ZC and SSC per channel over 200 ms windows, a linear discriminant, and
accuracy versus ADC bits for three sample rates (EMG range +-5 mV)."""
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


if __name__ == "__main__":
    fig()
    for fs in (500.0, 1000.0, 2000.0):
        print(fs, " ".join("%d:%.1f" % (b, np.mean([accuracy(b, fs, seed=s) for s in range(2)])) for b in (3, 4, 5, 6, 8, 12)))
