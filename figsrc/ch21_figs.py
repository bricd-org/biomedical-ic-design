"""ch21_figs.py -- Chapter 21 figure: level-crossing sampling of a synthetic ECG: the samples kept and the
reconstruction error versus the crossing threshold, against uniform 500 S/s sampling."""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "labs", "python"))
from bricdstyle import *
import biosig as bs

FS_HI = 20e3


def level_crossing(x, delta):
    """Indices where x has moved by delta since the last kept sample (ideal level-crossing ADC)."""
    keep = [0]
    ref = x[0]
    for i in range(1, len(x)):
        if abs(x[i] - ref) >= delta:
            ref = ref + delta * np.sign(x[i] - ref) * np.floor(abs(x[i] - ref) / delta)
            keep.append(i)
    return np.array(keep)


def fig():
    t, x = bs.ecg(fs=FS_HI, duration=10.0, hr=72, seed=21)[:2]
    fig, (a1, a2) = plt.subplots(1, 2, figsize=FULL2)
    sel = (t > 2.0) & (t < 3.6)
    k = level_crossing(x, 50e-6)
    a1.plot(t[sel], x[sel] * 1e3, color=PALE, lw=1.5, label="ECG")
    ks = k[(t[k] > 2.0) & (t[k] < 3.6)]
    a1.plot(t[ks], x[ks] * 1e3, "o", color=C1, ms=2.2, label=f"level-crossing samples, δ = 50 µV")
    a1.set_xlim(2.0, 3.6)
    finish(a1, xlabel="Time (s)", ylabel="ECG (mV)", legend=True, loc="upper right")
    a1.legend(loc="upper right", fontsize=6.3)
    panel(a1, "a")
    deltas = np.logspace(np.log10(5e-6), np.log10(500e-6), 12)
    rate, err = [], []
    for d in deltas:
        kk = level_crossing(x, d)
        rate.append(len(kk) / 10.0)
        y = np.interp(t, t[kk], x[kk])
        err.append(np.sqrt(np.mean((y - x) ** 2)))
    a2.loglog(deltas * 1e6, rate, "o-", color=C1, ms=3, label="samples per second (level crossing)")
    a2.axhline(500, color=C4, ls="--", lw=0.9, label="uniform 500 S/s")
    a2.set_xlabel("Crossing threshold δ (µV)")
    a2.set_ylabel("Samples per second", color=C1)
    a3 = a2.twinx()
    a3.loglog(deltas * 1e6, np.array(err) * 1e6, "s-", color=C3, ms=3, label="reconstruction error (rms)")
    a3.set_ylabel("Reconstruction error (µVrms)", color=C3)
    a2.set_xlim(4, 600)
    h1, l1 = a2.get_legend_handles_labels(); h3, l3 = a3.get_legend_handles_labels()
    a2.legend(h1 + h3, l1 + l3, loc="upper right", fontsize=6.0)
    panel(a2, "b")
    savefig(fig, "ch21_levelcrossing")
    return deltas, rate, err


if __name__ == "__main__":
    d, r, e = fig()
    for a, b, c in zip(d, r, e):
        print("delta %.1f uV: %.0f S/s, err %.2f uV" % (a * 1e6, b, c * 1e6))
