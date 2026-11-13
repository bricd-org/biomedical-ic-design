"""ch25_figs.py -- Chapter 25 figure: a synthetic EEG with a rhythmic seizure-like segment and its line-length
and theta-power features, and window-level seizure detection accuracy (theta-power threshold) versus ADC bits for three input noise
levels (EEG-mode range +-0.625 mV at the electrodes: total gain 800 into +-0.5 V)."""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "labs", "python"))
from bricdstyle import *
import biosig as bs
from scipy import signal as sps

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


if __name__ == "__main__":
    fig()
    for nz in (1.5e-6, 5e-6, 15e-6):
        print("noise %g:" % nz, " ".join("%d:%.1f" % (b, accuracy(b, nz)) for b in (4, 5, 6, 7, 8, 10, 12, 14)))
    print("LSB at 6/8 bits: %.1f / %.1f uV" % (2 * FS_IN / 64 * 1e6, 2 * FS_IN / 256 * 1e6))
